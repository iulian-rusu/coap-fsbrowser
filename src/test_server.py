import socket
import threading

from src.client.coap_message import CoAPMessage, CoAP


class TestServer(threading.Thread):
    def __init__(self):
        super().__init__(target=self.execute)
        localIP = "127.0.0.1"

        localPort = 5000

        self.bufferSize = 1024

        # create a list of messages to be sent

        self.messages = ['d/mnt/\x00fBD Proiect\x00fRC\x00dporn\x00dsecrets',
                         'fksdjlaksjdkaj klajskjaskljasdjals jlajsd kajkd',
                         '',
                         'd/mnt/secrets/\x00']
        self.contor = 0

        # Create a datagram socket

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to address and ip

        self.UDPServerSocket.bind((localIP, localPort))

    def execute(self):
        print("UDP server up and listening")
        while True:
            message, address = self.UDPServerSocket.recvfrom(self.bufferSize)
            coap_message = CoAPMessage.from_bytes(message)
            coap_message.payload = self.messages[self.contor]
            coap_message.msg_type = CoAP.TYPE_ACK
            coap_message.msg_class = CoAP.CLASS_SUCCESS
            coap_message.msg_code = 1

            bytes_to_send = CoAP.wrap(coap_message)

            self.UDPServerSocket.sendto(bytes_to_send, address)
            self.contor += 1

