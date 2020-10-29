from src.client.message_format import CoAPMessage
from src.client.protocols import CoAP, UDP
from src.parser.fs_parser import FSParser

''' file for testing various functions '''

def test_parser():
    test_cases = [
        "fsome content",  # content of a file
        "d/mnt\x00dBD\x00fsample.txt\x00dRC",  # directory + children
        "d/usr/bin/env\x00",  # empty directory
        "f"  # empty file
    ]

    for test_case in test_cases:
        result = FSParser.parse(test_case)
        print(result)


def test_protocols():
    # encoding stage
    coap_msg = CoAPMessage(data="hello world! this message was sent with CoAP + UDP", msg_type=1, msg_class=2,
                           msg_code=3, msg_id=0xABCD, header_version=0b10)
    coap_data = CoAP.wrap(coap_msg)  # wrap message using CoAP protocol
    udp_data = UDP.wrap(coap_data, src_port=0xF0, dst_port=0x0F)  # wrap CoAP bytes using UDP

    # decoding stage
    udp_header = udp_data[0:UDP.HEADER_LEN]  # use the UDP 8 byte header to get the necessary information
    msg_len = int.from_bytes(udp_header[4:6], 'big') - 8
    coap_bytes = udp_data[UDP.HEADER_LEN:UDP.HEADER_LEN + msg_len]  # get the CoAP bytes from the message
    received_msg = CoAPMessage.from_bytes(coap_bytes)  # construct CoAPMessage from bytes
    print(received_msg)


if __name__ == "__main__":
    test_protocols()
