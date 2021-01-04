import logging
import socket
import random
import math
import queue
from typing import Optional

from src.client.exceptions import InvalidResponse
from src.client.coap_message import CoAPMessage, CoAP
from src.command.command import FSCommand


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
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_inst.settimeout(Client.SOCK_TIMEOUT)
        self.msg_queue = msg_queue
        self.server_ip = socket.gethostbyname(server_ip)
        self.server_port = server_port
        self.last_msg_id = 0
        self.last_token = None
        self.confirmation_req = False
        self.is_running = False
        # initialize logger
        self.logger = logging.Logger(name='CLIENT', level=logging.INFO)
        file_handler = logging.FileHandler('client_log.txt')
        formatter = logging.Formatter('<%(name)s@%(asctime)s>:%(levelname)-8s%(message)s')
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
            # receive command from message queue
            try:
                cmd = self.msg_queue.get(block=True, timeout=Client.QUEUE_TIMEOUT)
            except queue.Empty:
                # no commands for now, check client state and try again
                continue
            # build CoAP message out of command and send it
            msg_type = 0x0 if self.confirmation_req else 0x1
            msg_class = cmd.get_coap_class()
            msg_code = cmd.get_coap_code()
            payload = cmd.coap_payload
            coap_response = self.send_and_receive(payload=payload, msg_class=msg_class,
                                                  msg_code=msg_code, msg_type=msg_type)
            if coap_response:
                self.process_response(coap_response, cmd)

    def send_and_receive(self, payload: str, msg_type: int, msg_class: int, msg_code: int) -> Optional[CoAPMessage]:
        """
        Sends a CoAP message to the server until the received response is correct or until the client runs out of
        resend attempts.
        A correct response has a matching tokken and a piggybacked acknowledge in case of confirmable requests.
        Any incorrect response will trigger a retransmission attempt, up to a set maximum amount of retransmissions.
        If the server does not send any response during the socket timoeut period, the transmission will be aborted.

        :param payload: The payload (body) of the message to be sent.
        :param msg_type: The type of the message to be sent.
        :param msg_class: The class of the message to be sent.
        :param msg_code: The code of the message to be sent.
        :return: Optional[CoAPMessage] - returns None in case of errors.
        """
        self.last_msg_id += 1
        self.last_token = Client.generate_token()
        token_length = int(math.ceil(math.log(self.last_token, 8)))
        coap_msg = CoAPMessage(payload=payload, msg_type=msg_type, msg_class=msg_class, msg_code=msg_code,
                               msg_id=self.last_msg_id, token_length=token_length, token=self.last_token)
        send_again = True
        attempts = Client.MAX_RESEND_ATTEMPTS
        while send_again:
            send_again = False
            self.send_message(coap_msg)
            try:
                coap_response = self.recv_message()
                while self.last_token != coap_response.token:
                    # ignore responses with incorrect token
                    coap_response = self.recv_message()
                if self.confirmation_req and self.last_msg_id != coap_response.msg_id:
                    raise InvalidResponse("Acknowledge message id did not match")
                # all good - return message
                return coap_response
            except socket.timeout:
                self.logger.error("(TIMEOUT)\tServer not responding")
            except InvalidResponse as e:
                self.logger.error(e)
                # resend message
                attempts -= 1
                if attempts <= 0:
                    self.logger.error("Too many invalid responses - abandonning retransmission")
                else:
                    send_again = True
        # something wrong - return nothing
        return None

    def process_response(self, coap_response: CoAPMessage, cmd: FSCommand):
        """
        Checks the response code and executes the command in case of OK response.
        Any errors or unknown responses are logged.

        :param coap_response: The response from the server.
        :param cmd: The current comand awaiting response.
        :return: None
        """
        print(coap_response)
        response_code = 100 * coap_response.msg_class + coap_response.msg_code
        if coap_response.msg_class == 2:
            self.logger.info(f'(RESPONSE)\tSuccess: {response_code}')
            # all good - execute the command locally to be up to date with the server
            cmd.exec(coap_response.payload)
        elif coap_response.msg_class == 4:
            # client error
            self.logger.error(f'(RESPONSE)\tClient error: {response_code}')
        elif coap_response.msg_class == 5:
            # server error
            self.logger.error(f'(RESPONSE)\tServer error: {response_code}')
        else:
            # other response classes not recognized/implemented
            self.logger.warning(f'Could not identify server response: {response_code}')

    def send_message(self, coap_msg: CoAPMessage):
        coap_data = CoAP.wrap(coap_msg)
        self.logger.info(f"(REQUEST)\t{coap_data.hex(sep=' ', bytes_per_sep=1)}")
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
        return random.randint(0, 65536)
