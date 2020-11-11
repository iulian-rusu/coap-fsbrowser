from src.file_system.file_system import *
from typing import Callable


class FSCommand(metaclass=abc.ABCMeta):
    """
        Interface for a generic command.
        Provides infromation about the CoAP header fields associated with the command.
        The constructor receives a callback function that will be called once the command has been executed and
        the data has been received from the server.
    """

    # command codes
    CMD_BACK = '\x01'
    CMD_OPEN = '\x02'
    CMD_SAVE = '\x03'
    CMD_NEWF = '\x04'
    CMD_NEWD = '\x05'
    CMD_DEL = '\x06'

    def __init__(self, callback: Callable):
        self.callback = callback

    def exec(self, *args, **kwargs):
        if self.callback:
            self.callback(*args, **kwargs)

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

            payload = <code><dir_name>
    """

    def __init__(self, current_dir: str, callback: Callable = None):
        super().__init__(callback)
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

            payload = <code><component_name>
    """

    def __init__(self, component: str, callback: Callable = None):
        super().__init__(callback)
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

            payload = <code><file_name>0x0<file_content>
    """

    def __init__(self, file: str, content: str, callback: Callable = None):
        super().__init__(callback)
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

            payload = <code><file_name>
    """

    def __init__(self, new_file: str, callback: Callable = None):
        super().__init__(callback)
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

            payload = <code><dir_name>
    """

    def __init__(self, new_dir: Directory, callback: Callable = None):
        super().__init__(callback)
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

            payload = <code><component_name>
    """

    def __init__(self, component: FSNamedComponent, callback: Callable = None):
        super().__init__(callback)
        self.component = component

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_DEL}{self.component}'
