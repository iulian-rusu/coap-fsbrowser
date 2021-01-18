import logging
import socket
import random
import math
import queue
from typing import Optional

from src.client.exceptions import InvalidResponse, InvalidFormat
from src.client.coap_message import CoAPMessage, CoAP
from src.client.command import FSCommand


class Client:
    """
    Implements the client end of the client-server communication.
    The run() method is blocking so it's recommended to run it in a separate thread.
    The communication with other threads is done via message queues.
    """

    MSG_BUFFER_SIZE = 65535
    MAX_RESEND_ATTEMPTS = 16
    SOCK_TIMEOUT = 1.0
    QUEUE_TIMEOUT = 1.0

    def __init__(self, server_ip: str, server_port: int, msg_queue: 'queue.Queue[FSCommand]' = None):
        self.server_ip = socket.gethostbyname(server_ip)
        self.server_port = server_port
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_inst.settimeout(Client.SOCK_TIMEOUT)
        self.msg_queue = msg_queue
        self.last_msg_id = 0
        self.last_token = None
        self.confirmation_required = False
        self.is_running = False
        # Callable used to asychronously display client messages in the GUI
        self.display_message_callback = None

        # Initialize logger
        self.logger = logging.Logger(name='CLIENT', level=logging.INFO)
        file_handler = logging.FileHandler('client_log.txt')
        formatter = logging.Formatter('<%(name)s@%(asctime)s>:[%(levelname)s] \t%(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def run(self):
        """
        Runs the client-server communication. Messages are received from the message queue.
        The client will wait for a response before sending another message from the queue,
        unless the server takes too long or sends too many invalid responses.
        """
        self.is_running = True
        while self.is_running:
            # Receive command from message queue
            try:
                cmd = self.msg_queue.get(block=True, timeout=Client.QUEUE_TIMEOUT)
            except queue.Empty:
                # No commands for now, check client state and try again
                continue
            # Build CoAP message out of command and send it
            coap_msg = self.command_to_coap(cmd)
            if coap_msg.msg_type == CoAP.TYPE_CONF or cmd.response_required():
                coap_response = self.send_and_receive(coap_msg)
                if coap_response:
                    self.process_response(coap_response, cmd)
            else:
                self.send_message(coap_msg)
                cmd.exec(response_data='')

    def command_to_coap(self, cmd: FSCommand) -> CoAPMessage:
        if self.confirmation_required or cmd.confirmation_required():
            msg_type = CoAP.TYPE_CONF
        else:
            msg_type = CoAP.TYPE_NON_CONF
        msg_class = cmd.get_coap_class()
        msg_code = cmd.get_coap_code()
        payload = cmd.coap_payload
        self.last_msg_id += 1
        if msg_class == CoAP.CLASS_METHOD and msg_code == CoAP.CODE_EMPTY:
            token_length = 0
        else:
            self.last_token = Client.generate_token()
            token_length = int(math.ceil(math.log(self.last_token, 8)))
        return CoAPMessage(payload=payload, msg_type=msg_type, msg_class=msg_class, msg_code=msg_code,
                           msg_id=self.last_msg_id, token_length=token_length, token=self.last_token)

    def send_and_receive(self, coap_msg: CoAPMessage) -> Optional[CoAPMessage]:
        """
        Sends a CoAP message to the server until the received response is correct or until the client
        runs out of resend attempts.
        A correct response has a matching token. In case of confirmable messages, the acknowledge is transmitted with a
        piggybacked response. Any incorrect response will trigger a retransmission attempt, up to a set maximum amount
        of retransmissions.
        If the server does not send any response during the socket timeout period, the transmission will be aborted.
        Received messages without a matching token are considered irrelevant and are ignored.

        :param coap_msg: The message to be sent.
        :return: Optional[CoAPMessage] - returns None in case of errors.
        """
        send_again = True
        attempts = Client.MAX_RESEND_ATTEMPTS
        while send_again:
            send_again = False
            self.send_message(coap_msg)
            try:
                coap_response = self.recv_message()
                while coap_response.token_length > 0 and self.last_token != coap_response.token:
                    # Receive responses until the token matches or there is no token
                    coap_response = self.recv_message()
                if not (coap_response.msg_type == CoAP.TYPE_ACK and self.last_msg_id == coap_response.msg_id):
                    raise InvalidResponse('Acknowledge message id did not match')
                # All good - return message
                return coap_response
            except socket.timeout:
                self.logger.error('(TIMEOUT)\tServer not responding')
                self.display_message('Server not responding')
            except InvalidResponse as e:
                self.logger.error(e)
                # Received messsage was incorrect - try to resend
                attempts -= 1
                if attempts > 0:
                    send_again = True
                else:
                    self.logger.error('Too many invalid responses - abandonning retransmission')
        # Something wrong - return nothing
        return None

    def process_response(self, coap_response: CoAPMessage, cmd: FSCommand):
        """
        Checks the response code and executes the command in case of OK response.
        Any errors or unknown responses are logged.

        :param coap_response: The response from the server.
        :param cmd: The current comand awaiting response.
        :return: None
        """
        if coap_response.msg_type == CoAP.TYPE_RESET:
            # Message type is Reset - put the command back in the queue for retransmission
            self.logger.info(f'(RESPONSE)\tReset')
            self.msg_queue.put(cmd)
            return
        response_code = 100 * coap_response.msg_class + coap_response.msg_code
        if coap_response.msg_class == CoAP.CLASS_SUCCESS:
            self.logger.info(f'(RESPONSE)\t{response_code}: {CoAP.RESPONSE_CODE.get(response_code, "Unknown")}')
            # Success - execute the command locally to be up to date with the server
            try:
                cmd.exec(coap_response.payload)
            except InvalidFormat as e:
                self.display_message(f'Incorrect server data: {e.msg}', duration=3)
        elif coap_response.msg_class in (CoAP.CLASS_CERROR, CoAP.CLASS_SERROR):
            # Client or Server error
            msg = f'{response_code}: {CoAP.RESPONSE_CODE.get(response_code, "Unknown")}'
            self.logger.error(f'(RESPONSE)\t{msg}')
            self.display_message(msg)
        elif coap_response.msg_class == CoAP.CLASS_METHOD:
            # Method class is not a valid response class
            msg = f'Invalid response code: {response_code}'
            self.logger.error(f'(RESPONSE)\t{msg}')
            self.display_message_callback(msg)
        else:
            # Other response classes not recognized/implemented
            msg = f'Unknown response code: {response_code}'
            self.logger.warning(f'(RESPONSE)\t{msg}')
            self.display_message(msg, color='orange3')

    def display_message(self, msg: str, duration: int = 2, color: str = 'red'):
        if self.display_message_callback:
            self.display_message_callback(msg, duration, color)

    def send_message(self, coap_msg: CoAPMessage):
        coap_data = CoAP.wrap(coap_msg)
        self.logger.info(f"(REQUEST)\t{coap_msg.logging_format()}")
        self.send_bytes(coap_data, self.server_ip, self.server_port)

    def recv_message(self) -> CoAPMessage:
        coap_bytes = self.recv_bytes()
        return CoAPMessage.from_bytes(coap_bytes)

    def send_bytes(self, msg: bytes, ip: str, port: int):
        self.socket_inst.sendto(msg, (ip, port))

    def recv_bytes(self) -> bytes:
        return self.socket_inst.recv(Client.MSG_BUFFER_SIZE)

    @staticmethod
    def generate_token() -> int:
        return random.randint(0, 0xFFFF)
