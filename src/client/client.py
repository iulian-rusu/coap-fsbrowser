import logging
import socket
import random
import math
import queue
from typing import Tuple, Any

from src.client.message_format import CoAPMessage
from src.client.protocol import CoAP


class Client:
    """
        Implements the client end of the client-server communication.
        The run() method is blocking so it's recommended to run it in a separate thread.
        The communication with other threads is done via message queues.
    """
    MSG_BUFFER_SIZE = 1024
    MAX_RESEND_ATTEMPTS = 16

    def __init__(self, server_ip: str, server_port: int, msg_queue: queue.Queue = None):
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket_inst.settimeout(5)
        self.msg_queue = msg_queue
        self.server_ip = server_ip
        self.server_port = server_port
        self.last_msg_id = 0
        self.last_token = None
        self.confirmation_req = False
        self.is_running = False
        # initialize logger
        self.logger = logging.Logger(name='CLIENT', level=logging.INFO)
        file_handler = logging.FileHandler('client_log.txt')
        formatter = logging.Formatter('[%(levelname)s]<%(name)s@%(asctime)s>: %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def run(self):
        """
            Runs the client-server communication. Messages are received from the message queue.
        """
        self.is_running = True
        while self.is_running:
            # receive command from message queue
            try:
                cmd = self.msg_queue.get(block=True, timeout=1)
            except queue.Empty:
                # no commands for now, check client state and try again
                continue
            # build CoAP message out of command and send it
            msg_type = 0x0 if self.confirmation_req else 0x1
            msg_class = cmd.get_coap_class()
            msg_code = cmd.get_coap_code()
            payload = cmd.get_coap_payload()
            self.send_until_response_ok(payload=payload, msg_class=msg_class, msg_code=msg_code, msg_type=msg_type)

    def send_until_response_ok(self, payload: str, msg_type: int, msg_class: int, msg_code: int):
        """
            Sends a CoAP message to the server until the received response is correct or until the client runs out of
            resend attempts.
        """
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
                if self.last_token != coap_response.token:
                    raise InvalidResponse("Received token did not match")
                if self.confirmation_req and self.last_msg_id != coap_response.msg_id:
                    raise InvalidResponse("Acknowledge message id did not match")
                # TODO: do something useful with the received response
                self.logger.info(CoAP.wrap(coap_response).hex(sep=' ', bytes_per_sep=1))
            except socket.timeout:
                self.logger.error("(TIMEOUT) Server not responding")
            except Exception as e:
                self.logger.error(e)
                # resend request
                attempts -= 1
                if attempts <= 0:
                    self.logger.error("Too many invalid responses - abandonning attemptsS")
                else:
                    send_again = True

    def send_message(self, coap_msg: CoAPMessage):
        self.last_msg_id += 1
        coap_msg.msg_id = self.last_msg_id
        # wrap it using CoAP and send it
        coap_data = CoAP.wrap(coap_msg)
        self.send_bytes(coap_data, self.server_ip, self.server_port)

    def recv_message(self) -> CoAPMessage:
        # receives bytes from the server and returns a CoAPMessage object
        coap_bytes, server = self.recv_bytes(Client.MSG_BUFFER_SIZE)
        return CoAPMessage.from_bytes(coap_bytes)

    def send_bytes(self, msg: bytes, ip: str, port: int):
        self.socket_inst.sendto(msg, (ip, port))

    def recv_bytes(self, amount: int) -> Tuple[bytes, Any]:
        return self.socket_inst.recvfrom(amount)

    @staticmethod
    def generate_token() -> int:
        return random.randint(0, 65536)


class InvalidResponse(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    def __str__(self):
        return f"(INVALID RESPONSE) {super().__str__()}"
