from src.file_system.file_system import *


class FSCommand(metaclass=abc.ABCMeta):
    """
        Interface for a generic command.
        Provides infromation about the CoAP header fields associated with the command.
    """

    CMD_BACK = '\x01'
    CMD_OPEN = '\x02'
    CMD_SAVE = '\x03'
    CMD_NEWF = '\x04'
    CMD_NEWD = '\x05'
    CMD_DEL = '\x06'

    @staticmethod
    @abc.abstractmethod
    def get_coap_class() -> int:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_coap_code() -> int:
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
            payload = 0x1<dir_name>
    """

    def __init__(self, current_dir: str):
        self.current_dir = current_dir

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_BACK}{self.current_dir}'


class OpenCommand(FSCommand):
    """
        Class that implements the OPEN command.
        Allows the user to open a directory or file.
        CoAP format:
            class = 0x1 (Method)
            code = 0x1 (GET)
            payload = 0x2<component_name>
    """

    def __init__(self, component: str):
        self.component = component

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_OPEN}{self.component}'


class SaveCommand(FSCommand):
    """
        Class that implements the SAVE command.
        Allows the user to open a directory or file.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = 0x3<file_name>0x0<file_content>
    """

    def __init__(self, file: str, content: str):
        self.file = file
        self.content = content

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_SAVE}{self.file}\x00{self.content}'


class NewFileCommand(FSCommand):
    """
        Class that implements the NEW FILE command.
        Allows the user to create a file in the current directory.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = 0x4<file_name>
    """

    def __init__(self, new_file: str):
        self.new_file = new_file

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_NEWF}{self.new_file}'


class NewDirCommand(FSCommand):
    """
        Class that implements the NEW DIR command.
        Allows the user to create a directory in the current directory.
        CoAP format:
            class = 0x1 (Method)
            code = 0x2 (POST)
            payload = 0x5<dir_name>
    """

    def __init__(self, new_dir: Directory):
        self.new_dir = new_dir

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_NEWD}{self.new_dir}'


class DeleteCommand(FSCommand):
    """
        Class that implements the DELETE command.
        Allows the user to delete the specified component.
        CoAP format:
            class = 0x1 (Method)
            code = 0x4 (DELETE)
            payload = 0x5<component_name>
    """

    def __init__(self, component: FSNamedComponent):
        self.component = component

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_DEL}{self.component}'
