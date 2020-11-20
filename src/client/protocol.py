from src.client.coap_message import CoAPMessage


class CoAP:
    """
    Containts static methods that encode a specified message.
    according to the CoAP RFC-7252 specification.
    """

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
        """
        Takes a CoAPMessage object and converts it into a stream of bytes according to the CoAP protocol

        :param msg: The CoAPMEssage object to be encoded.
        :return: bytes representing the encoded message.
        """

        coap_header = CoAP.build_header(msg)
        payload = ''
        if len(msg.payload):
            payload = 0xFF.to_bytes(1, 'big') + msg.payload.encode('utf-8')
        return coap_header.to_bytes(CoAP.HEADER_LEN + msg.token_length, 'big') + payload

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
