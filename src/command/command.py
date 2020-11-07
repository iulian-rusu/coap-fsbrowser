from src.file_system.file_system import *


class FSCommand(metaclass=abc.ABCMeta):
    """
        Interface for a generic command.
        Provides infromation about the CoAP header fields associated with the command.
    """

    @abc.abstractmethod
    def get_coap_class(self) -> int:
        pass

    @abc.abstractmethod
    def get_coap_code(self) -> int:
        pass

    @abc.abstractmethod
    def get_coap_payload(self) -> str:
        pass


class BackCommand(FSCommand):
    """
        Class that implements the BACK command.
        Allows the user to go to the previous directory.
        CoAP format:
            class = 0x1 (Method)
            code = 0x1 (GET)
            payload = TODO
    """

    def __init__(self, current_dir: Directory):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass


class OpenCommand(FSCommand):
    """
        Class that implements the OPEN command.
        Allows the user to open a directory or file.
        CoAP format:
            class = 0x1 (Method)
            code = 0x1 (GET)
            payload = TODO
    """

    def __init__(self, component: FSNamedComponent):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass


class SaveCommand(FSCommand):
    """
        Class that implements the SAVE command.
        Allows the user to open a directory or file.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = TODO
    """

    def __init__(self, file: File):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass


class NewFileCommand(FSCommand):
    """
        Class that implements the NEW FILE command.
        Allows the user to create a file in the current directory.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = TODO
    """

    def __init__(self, new_file: File):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass


class NewDirCommand(FSCommand):
    """
        Class that implements the NEW DIR command.
        Allows the user to create a directory in the current directory.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = TODO
    """

    def __init__(self, new_dir: Directory):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass


class DeleteCommand(FSCommand):
    """
        Class that implements the DELETE command.
        Allows the user to delete the specified component.
        CoAP format:
            class = 0x1 (Method)
            code = 0x4 (DELETE)
            payload = TODO
    """

    def __init__(self, component: FSNamedComponent):
        # TODO: come up with command encoding
        pass

    def get_coap_class(self) -> int:
        return 0x1

    def get_coap_code(self) -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        pass
