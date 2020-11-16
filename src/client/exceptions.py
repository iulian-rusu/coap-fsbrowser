class InvalidResponse(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    def __str__(self):
        return f"(INVALID RESPONSE) {Exception.__str__(self)}"


class InvalidFormat(InvalidResponse):
    def __init__(self, msg: str):
        super().__init__(msg)

    def __str__(self):
        return f"(INVALID FORMAT) {Exception.__str__(self)}"
