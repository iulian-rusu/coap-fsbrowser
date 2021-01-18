import socket
import threading
from typing import Iterator

from src.client.coap_message import CoAPMessage, CoAP


class TestServer:
    """
    Test server with hard-coded responses
    """
    MSG_BUFFER_SIZE = 65535
    SOCK_TIMEOUT = 1

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket_inst = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_inst.bind((self.ip, self.port))
        self.socket_inst.settimeout(TestServer.SOCK_TIMEOUT)
        self.is_running = False
        self.run_thread = threading.Thread(target=self.run)
        self.responses = TestServer.gen_responses()

    def start(self):
        self.is_running = True
        self.run_thread.start()

    def stop(self):
        self.is_running = False

    def run(self):
        print("\t\t[STARTED TEST SERVER]")
        while self.is_running:
            try:
                coap_bytes, addr = self.socket_inst.recvfrom(TestServer.MSG_BUFFER_SIZE)
            except socket.timeout:
                continue
            msg = CoAPMessage.from_bytes(coap_bytes)
            try:
                response = next(self.responses)
            except StopIteration:
                continue
            print(f"\t\t[SERVER RECEIVED MESSAGE]")
            print(msg)
            response.msg_id = msg.msg_id
            response.token_length = msg.token_length
            response.token = msg.token
            print("\t\t[SENDING RESPONSE ...]")
            self.socket_inst.sendto(CoAP.wrap(response), addr)
        print("\t\t[STOPED TEST SERVER]")

    @staticmethod
    def gen_responses() -> Iterator[CoAPMessage]:
        # Scenario
        response_list = [
            # Acknowledge to ping
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=3,
                        msg_id=0),
            # Open home directory
            CoAPMessage(payload='d/home/rcp\x00dDocuments\x00dDownloads\x00dDesktop\x00dMusic'
                                '\x00fsecrets.txt\x00ferror.log\x00frandom.txt\x00fmain.py\x00dWork',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=3,
                        msg_id=0),
            # Open Documents
            CoAPMessage(payload='d/home/rcp/Documents\x00dPython\x00dC++\x00dProjects\x00ftodo.txt',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=3,
                        msg_id=0),
            # Back
            CoAPMessage(payload='d/home/rcp\x00dDocuments\x00dDownloads\x00dDesktop\x00dMusic'
                                '\x00fsecrets.txt\x00ferror.log\x00frandom.txt\x00fmain.py\x00dWork',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=3,
                        msg_id=0),
            # Open error.log
            CoAPMessage(payload="fThis is an error log:\n"
                                "<CLIENT@2021-01-14 21:50:20,805>:[ERROR] 	(TIMEOUT)	Server not responding\n\
<CLIENT@2021-01-14 21:50:21,807>:[ERROR] 	(TIMEOUT)	Server not responding\n\
<CLIENT@2021-01-14 21:50:22,810>:[ERROR] 	(TIMEOUT)	Server not responding\n",
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=3,
                        msg_id=0),
            # Change error.log and press Save
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=4,
                        msg_id=0),
            # Make a new file
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=1,
                        msg_id=0),
            # Make a new directory
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=1,
                        msg_id=0),
            # Open the new directory
            CoAPMessage(payload='d/home/rcp/New dir name\x00',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=1,
                        msg_id=0),
            # Error - invalid response data
            CoAPMessage(payload='incorrect response',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SUCCESS,
                        msg_code=1,
                        msg_id=0),
            # Server error
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_SERROR,
                        msg_code=3,
                        msg_id=0),
            # Client error
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=CoAP.CLASS_CERROR,
                        msg_code=4,
                        msg_id=0),
            # Error - use of reserved CoAP message class
            CoAPMessage(payload='',
                        msg_type=CoAP.TYPE_ACK,
                        msg_class=1,
                        msg_code=1,
                        msg_id=0),

        ]
        for response in response_list:
            yield response
