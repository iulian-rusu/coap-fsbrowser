class InvalidResponse(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self) -> str:
        return f"(INVALID RESPONSE) {Exception.__str__(self)}"


class InvalidFormat(InvalidResponse):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self) -> str:
        return f"(INVALID FORMAT) {Exception.__str__(self)}"
