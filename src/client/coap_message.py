from src.client.exceptions import InvalidFormat


class CoAPMessage:
    """
    Encapsulates a CoAP-style message, providing an easy means of accessing all header fields.
    Is responsible for validating messages and throws exceptions in case of incorrect formats.
    """

    def __init__(self, payload: str, msg_type: int, msg_class: int, msg_code: int, msg_id: int,
                 header_version=0x1, token_length=0x0, token=0x0):
        self.payload = payload
        self.header_version = header_version
        self.msg_type = msg_type
        self.token_length = token_length
        self.msg_class = msg_class
        self.msg_code = msg_code
        self.msg_id = msg_id
        self.token = token

    def __str__(self) -> str:
        return f"""[VERSION]:\t{self.header_version}\n[TYPE]:\t\t{self.msg_type}\n[TKN LEN]:\t{self.token_length}
[CLASS]:\t{self.msg_class}\n[CODE]:\t\t{self.msg_code}\n[MSG ID]:\t{self.msg_id}
[TOKEN]:\t{hex(self.token) if self.token_length else ''}
[PAYLOAD]:\t{self.payload}\n"""

    def logging_format(self) -> str:
        data_bytes = CoAP.build_header(self)
        ans = data_bytes.hex(sep=' ', bytes_per_sep=1)
        if self.payload:
            ans += f' ff {bytes(self.payload, encoding="utf-8")}'
        return ans

    @classmethod
    def from_bytes(cls, data_bytes: bytes) -> 'CoAPMessage':
        """
        Creates a CoAPMessage from bytes encoded using the CoAP protocol.
        This method will also check any format inconsistencies according to RFC-7252 and will throw InvalidFormat.

        :param data_bytes: The bytes that encode the message.
        """
        header_bytes = data_bytes[0:4]
        header_version = (0xC0 & header_bytes[0]) >> 6
        msg_type = (0x30 & header_bytes[0]) >> 4
        token_length = (0x0F & header_bytes[0]) >> 0
        msg_class = (header_bytes[1] >> 5) & 0x07
        msg_code = (header_bytes[1] >> 0) & 0x1F
        msg_id = (header_bytes[2] << 8) | header_bytes[3]

        # Check if the header has reserved field values
        if header_version not in CoAP.VALID_VERSIONS:
            raise InvalidFormat("Message has incorrect CoAP header version")
        elif 9 <= token_length <= 15:
            raise InvalidFormat("Message has incorrect CoAP token length")

        # Check special message types/classes/codes
        if (msg_class == CoAP.CLASS_METHOD and msg_code == CoAP.CODE_EMPTY) or msg_type == CoAP.TYPE_RESET:
            # This message must be EMPTY
            if not CoAPMessage.is_valid_empty_format(msg_class, msg_code, token_length, data_bytes):
                raise InvalidFormat("Incorrect format for EMPTY CoAP message")
            if msg_type == CoAP.TYPE_NON_CONF:
                raise InvalidFormat("EMPTY CoAP message cannot be non-confirmable")

        token = 0x0
        if token_length:
            token = int.from_bytes(data_bytes[4:4 + token_length], 'big')
        payload = data_bytes[5 + token_length:].decode('utf-8')
        return cls(payload, msg_type, msg_class, msg_code, msg_id,
                   header_version=header_version, token_length=token_length, token=token)

    def is_empty(self):
        return self.msg_class == CoAP.CLASS_METHOD and self.msg_code == CoAP.CODE_EMPTY \
               and self.token_length == 0x0 and self.token is None and len(self.payload) == 0

    def requires_acknowledge(self):
        return self.msg_type == CoAP.TYPE_CONF or (self.msg_type == CoAP.TYPE_ACK and not self.is_empty())

    @staticmethod
    def is_valid_empty_format(msg_class: int, msg_code: int, token_length: int, data_bytes: bytes) -> bool:
        return msg_class == CoAP.CLASS_METHOD and msg_code == CoAP.CODE_EMPTY \
               and token_length == 0x0 and len(data_bytes) == 4


class CoAP:
    """
    Holds information about the Constrained Application Protocol compliant with RFC-7252.
    Containts static methods that encode a specified CoAPMessage object.
    """

    HEADER_LEN = 4
    VALID_VERSIONS = (1, )
    PAYLOAD_MARKER = b'\xFF'
    DEFAULT_PORT = 5683

    # Field offsets
    VERSION = 0x1E
    MSG_TYPE = 0x1C
    TOKEN_LENGTH = 0x18
    MSG_CLASS = 0x15
    MSG_CODE = 0x10
    MSG_ID = 0x00

    # Message types
    TYPE_CONF = 0
    TYPE_NON_CONF = 1
    TYPE_ACK = 2
    TYPE_RESET = 3

    # Message classes
    CLASS_METHOD = 0
    CLASS_SUCCESS = 2
    CLASS_CERROR = 4
    CLASS_SERROR = 5
    CLASS_RESERVED = (1, 6, 7)

    # Method codes
    CODE_EMPTY = 0
    CODE_GET = 1
    CODE_POST = 2
    CODE_DELETE = 4

    # Response code translation
    RESPONSE_CODE = {
        # Success
        201: 'Created',
        202: 'Deleted',
        203: 'Valid',
        204: 'Changed',
        # Client error
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Bad option',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        # Server error
        500: 'Internal Server Error',
        501: 'Not Implemented',
        503: 'Service Not Available'
    }

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def wrap(msg: CoAPMessage) -> bytes:
        """
        Takes a CoAPMessage object and converts it into bytes according to the CoAP protocol

        :param msg: The CoAPMEssage object to be encoded.
        :return: bytes representing the encoded message.
        """

        coap_header = CoAP.build_header(msg)
        payload = b''
        if len(msg.payload):
            payload = CoAP.PAYLOAD_MARKER + msg.payload.encode('utf-8')
        return coap_header + payload

    @staticmethod
    def build_header(msg: CoAPMessage) -> bytes:
        header = 0x00
        header |= msg.header_version << CoAP.VERSION
        header |= (0b11 & msg.msg_type) << CoAP.MSG_TYPE
        header |= (0xFF & msg.token_length) << CoAP.TOKEN_LENGTH
        header |= (0b111 & msg.msg_class) << CoAP.MSG_CLASS
        header |= (0x1F & msg.msg_code) << CoAP.MSG_CODE
        header |= (0xFFFF & msg.msg_id) << CoAP.MSG_ID
        if msg.token_length:
            header = (header << 8 * msg.token_length) | msg.token
        return header.to_bytes(CoAP.HEADER_LEN + msg.token_length, 'big')
