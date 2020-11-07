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

    def __init__(self, server_ip: str, server_port: int, msg_queue: queue.Queue = None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sent_messages = 0
        self.token = None
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.msg_queue = msg_queue
        self.is_running = False

    def run(self):
        # TODO:
        #  implement command sending and receiving
        #  request-response mechanism with confirmable and non-confirmable messages
        #  validation of messages and proper response to them
        while self.is_running:
            cmd = self.msg_queue.get(block=True)

    def send_message(self, payload: str, msg_type: int, msg_class: int, msg_code: int):
        # generate a random token and calculate its length in bytes
        self.generate_token()
        token_length = int(math.ceil(math.log(self.token, 8)))
        # create message
        coap_msg = CoAPMessage(payload, msg_type, msg_class, msg_code, self.sent_messages,
                               token_length=token_length, token=self.token)
        self.sent_messages += 1
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
