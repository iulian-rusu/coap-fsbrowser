import socket

from src.client.message_format import CoAPMessage
from src.client.protocols import CoAP, UDP


class Client:
    def __init__(self, server_ip: str, server_port: int):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sent_messages = 0
        self.socket_inst = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.is_connected = False

    def connect(self):
        if not self.is_connected:
            try:
                self.socket_inst.connect((self.server_ip, self.server_port))
                self.is_connected = True
            except socket.timeout as error:
                print(f"Client: {error}")

    def send_message(self, data: str, msg_type: int, msg_class: int, msg_code: int):
        # sends a string to the server using UDP + CoAP
        coap_msg = CoAPMessage(data, msg_type, msg_class, msg_code, self.sent_messages)
        self.sent_messages += 1
        coap_data = CoAP.wrap(coap_msg)
        udp_data = UDP.wrap(coap_data, src_port=0x0, dst_port=self.server_port)
        self.send_bytes(udp_data)

    def recv_message(self) -> CoAPMessage:
        # receives bytes from the server and returns a CoAPMessage object
        udp_header = self.recv_bytes(UDP.HEADER_LEN)
        msg_len = int.from_bytes(udp_header[4:6], 'big')
        coap_bytes = self.recv_bytes(msg_len - 8)  # read only the UDP data without the 8 byte header
        return CoAPMessage.from_bytes(coap_bytes)

    def send_bytes(self, msg: bytes):
        if self.is_connected:
            self.socket_inst.send(msg)

    def recv_bytes(self, ammount: int) -> bytes:
        if self.is_connected:
            return self.socket_inst.recv(ammount)
