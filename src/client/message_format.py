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

    def __str__(self):
        return f"""[HEADER]: {self.header_version}, [TYPE]: {self.msg_type}, [TOKEN LENGTH]: {self.token_length}, \
[CLASS]: {self.msg_class}, [CODE]: {self.msg_code}, [ID]: {self.msg_id}
[TOKEN]: {hex(self.token) if self.token_length else ''}
[DATA]: {self.payload}\n"""

    @staticmethod
    def from_bytes(data_bytes: bytes):
        """
            Creates a CoAPMessage from bytes encoded using the CoAP protocol.
            This method will also check any format inconsistencies according to RFC-7252 and will throw FormatException.
        """
        header_bytes = data_bytes[0:4]
        header_version = (0xC0 & header_bytes[0]) >> 6
        msg_type = (0x30 & header_bytes[0]) >> 4
        token_length = (0x0F & header_bytes[0]) >> 0
        msg_class = (header_bytes[1] >> 5) & 0x07
        msg_code = (header_bytes[1] >> 0) & 0x1F
        msg_id = (header_bytes[2] << 8) | header_bytes[3]
        # message must have correct header version, token length and class
        if header_version != 0x1:
            raise FormatException("Message has incorrect CoAP header version")
        elif 9 <= token_length <= 15:
            raise FormatException("Message has incorrect CoAP token length")
        elif msg_class in (1, 6, 7):
            raise FormatException("Message uses reserved CoAP message class")
        # check special message types/classes/codes
        if (msg_class == 0x0 and msg_code == 0x0) or msg_type == 0x3:
            # message must be emtpy
            if not CoAPMessage.is_empty(msg_class, msg_code, token_length, data_bytes):
                raise FormatException("Incorrect format for EMPTY CoAP message")
            # empty message must be non-confirmable
            if msg_type == 0x1:
                raise FormatException("Non-confirmable CoAP message cannot be EMPTY")
        token = 0x0
        # if there is a token, read it
        if token_length:
            token = int.from_bytes(data_bytes[4:4 + token_length], 'big')
        # read the message payload
        payload = data_bytes[5 + token_length:].decode('utf-8')
        return CoAPMessage(payload, msg_type, msg_class, msg_code, msg_id,
                           header_version=header_version, token_length=token_length, token=token)

    @staticmethod
    def is_empty(msg_class: int, msg_code: int, token_length: int, data_bytes: bytes) -> bool:
        return msg_class == 0x0 and msg_code == 0x0 and token_length == 0x0 and len(data_bytes) == 4


class FormatException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    def __str__(self):
        return f"(FORMAT EXCEPTION) {super().__str__()}"
