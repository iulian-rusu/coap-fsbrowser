from src.client.message_format import CoAPMessage


class CoAP:
    HEADER_LEN = 4
    VERSION = 0x1E
    MSG_TYPE = 0x1C
    TOKEN_LENGTH = 0x18
    MSG_CLASS = 0x15
    MSG_CODE = 0x10
    MSG_ID = 0x00

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def wrap(msg: CoAPMessage) -> bytes:
        # takes a CoAPMessage object and converts it into a stream of bytes according to the CoAP protocol
        coap_header = CoAP.build_header(msg)
        coap_data = 0xFF.to_bytes(1, 'big') + msg.data.encode('utf-8')
        return coap_header.to_bytes(CoAP.HEADER_LEN + msg.token_length, 'big') + coap_data

    @staticmethod
    def build_header(msg: CoAPMessage) -> int:
        header = 0x00
        header |= msg.header_version << CoAP.VERSION
        header |= (0b11 & msg.msg_type) << CoAP.MSG_TYPE
        header |= msg.token_length << CoAP.TOKEN_LENGTH
        header |= (0b111 & msg.msg_class) << CoAP.MSG_CLASS
        header |= (0x1F & msg.msg_code) << CoAP.MSG_CODE
        header |= (0xFFFF & msg.msg_id) << CoAP.MSG_ID
        if msg.token_length:
            header = (header << 8 * msg.token_length) | msg.token
        return header


class UDP:
    HEADER_LEN = 8
    SRC_PORT = 0x30
    DST_PORT = 0x20
    LENGTH = 0x10
    CHECKSUM = 0x00

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def wrap(data_bytes: bytes, src_port: int, dst_port: int, checksum=0x0) -> bytes:
        # takes a stream of bytes and encodes it using UDP
        length = len(data_bytes) + 8  # 8 byte header length
        udp_header = UDP.build_header(src_port, dst_port, length, checksum)
        return udp_header.to_bytes(UDP.HEADER_LEN, 'big') + data_bytes

    @staticmethod
    def build_header(src_port: int, dst_port: int, length: int, checksum: int) -> int:
        header = 0x00
        header |= (0xFFFF & src_port) << UDP.SRC_PORT
        header |= (0xFFFF & dst_port) << UDP.DST_PORT
        header |= (0xFFFF & length) << UDP.LENGTH
        header |= (0xFFFF & checksum) << UDP.CHECKSUM
        return header
