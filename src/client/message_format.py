class CoAPMessage:
    def __init__(self, data: str, msg_type: int, msg_class: int, msg_code: int, msg_id: int,
                 header_version=0x0, token_length=0x0):
        self.data = data
        self.header_version = header_version
        self.msg_type = msg_type
        self.token_length = token_length
        self.msg_class = msg_class
        self.msg_code = msg_code
        self.msg_id = msg_id

    def as_tuple(self):
        return self.data, self.msg_type, self.msg_class, self.msg_code, self.msg_id

    def __str__(self):
        return f"""[HEADER VERSION]: {self.header_version}, [TYPE]: {self.msg_type}, [TOKEN LENGTH]: {self.token_length}, \
[CLASS]: {self.msg_class}, [CODE]: {self.msg_code}, [ID]: {self.msg_id}
[DATA]: {self.data}\n"""

    @staticmethod
    def from_bytes(data_bytes: bytes):
        # creates a CoAPMessage from bytes encoded using the CoAP protocol
        header_bytes = data_bytes[0:4]
        msg_data = data_bytes[4:].decode('utf-8')
        header_version = (0xC0 & header_bytes[0]) >> 6
        msg_type = (0x30 & header_bytes[0]) >> 4
        token_length = (0x0F & header_bytes[0]) >> 0
        msg_class = (header_bytes[1] >> 5) & 0x07
        msg_code = (header_bytes[1] >> 0) & 0x1F
        msg_id = (header_bytes[2] << 8) | header_bytes[3]
        return CoAPMessage(msg_data, msg_type, msg_class, msg_code, msg_id,
                           header_version=header_version, token_length=token_length)
