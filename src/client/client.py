import logging
import socket
import random
import math
import queue
from typing import Tuple, Any

from src.client.message_format import CoAPMessage, FormatException
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
        self.server_ip = server_ip
        self.server_port = server_port
        self.msg_id = 0
        self.token = None
        self.confirmation_req = False
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.msg_queue = msg_queue
        self.is_running = False
        # initialize logger
        self.logger = logging.getLogger('CLIENT')
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('client_log.txt')
        formatter = logging.Formatter('[%(name)s@%(asctime)s]: %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def run(self):
        self.is_running = True
        while self.is_running:
            # receive command from message queue
            cmd = self.msg_queue.get(block=True)
            # build CoAP message out of command and send it
            msg_type = 0x0 if self.confirmation_req else 0x1
            msg_class = cmd.get_coap_class()
            msg_code = cmd.get_coap_code()
            payload = cmd.get_coap_payload()
            send_again = True
            attemps = Client.MAX_RESEND_ATTEMPTS
            while send_again:
                send_again = False
                self.send_message(payload, msg_type, msg_class, msg_code)
                # await response and process it
                try:
                    coap_response = self.recv_message()
                    if self.token != coap_response.token:
                        raise InvalidResponse("Received token did not match")
                    if self.confirmation_req and self.msg_id != coap_response.msg_id:
                        raise InvalidResponse("Acknowledge message id did not match")
                    # TODO: do something useful with the received response
                except FormatException as e:
                    self.logger.error(f"[FORMAT EXCEPTION] {e}")
                except InvalidResponse as e:
                    self.logger.error(f"[INVALID RESPONSE] {e}")
                    # resend request
                    send_again = True
                    attemps -= 1
                    if attemps == 0:
                        # out of resend attempts
                        self.logger.error("[SERVER NOT RESPONDING]")
                        send_again = False

    def send_message(self, payload: str, msg_type: int, msg_class: int, msg_code: int):
        # generate a token and calculate its length
        self.generate_token()
        token_length = int(math.ceil(math.log(self.token, 8)))
        # create message
        self.msg_id += 1
        coap_msg = CoAPMessage(payload, msg_type, msg_class, msg_code, self.msg_id,
                               token_length=token_length, token=self.token)
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

    def generate_token(self):
        self.token = random.randint(0, 65536)


class InvalidResponse(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
