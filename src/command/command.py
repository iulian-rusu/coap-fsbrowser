from src.client.message_format import CoAPMessage
from src.file_system.file_system import *
from typing import Callable

from src.parser.fs_parser import FSParser


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

    @abc.abstractmethod
    def exec(self, coap_response: CoAPMessage):
        """
        Called once the client has reveived an OK repsonse from the server.
        Executes the command on the client-side by means of a given callback function.

        :param coap_response: The response from the server, may be unused in the callback.
        :return: None
        """
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

    def __init__(self, current_dir_name: str, callback: Callable = None):
        super().__init__(callback)
        self.current_dir_name = current_dir_name

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_BACK}{self.current_dir_name}'

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # parse response and get the directory to go to
            new_dir = FSParser.parse(coap_response.payload)
            self.callback(new_dir)


class OpenCommand(FSCommand):
    """
    Class that implements the OPEN command.
    Allows the user to open a directory or file.

    CoAP format:
        class = 0x1 (Method)

        code = 0x1 (GET)

        payload = <code><component_name>
    """

    def __init__(self, component_name: str, callback: Callable = None):
        super().__init__(callback)
        self.component_name = component_name

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_OPEN}{self.component_name}'

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # parse response and get the component to be opened
            to_open = FSParser.parse(coap_response.payload)
            self.callback(to_open)


class SaveCommand(FSCommand):
    """
    Class that implements the SAVE command.
    Allows the user to open a directory or file.

    CoAP format:
        class = 0x1 (Method)

        code = 0x2 (POST)

        payload = <code><file_name>0x0<file_content>
    """

    def __init__(self, file_name: str, content: str, callback: Callable = None):
        super().__init__(callback)
        self.file_name = file_name
        self.content = content

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_SAVE}{self.file_name}\x00{self.content}'

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # no need to parse the response, just save the current file content
            self.callback()


class NewFileCommand(FSCommand):
    """
    Class that implements the NEW FILE command.
    Allows the user to create a file in the current directory.

    CoAP format:
        class = 0x1 (Method)

        code = 0x2 (POST)

        payload = <code><file_name>
    """

    def __init__(self, new_file_name: str, callback: Callable = None):
        super().__init__(callback)
        self.new_file_name = new_file_name

    @staticmethod
    def get_coap_class() -> int:
        return 0x0

    @staticmethod
    def get_coap_code() -> int:
        return 0x1

    def get_coap_payload(self) -> str:
        return f'{FSCommand.CMD_NEWF}{self.new_file_name}'

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # no need to parse the response, just create an empty file
            self.callback()


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

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # no need to parse the response, just create an empty directory
            self.callback()


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

    def exec(self, coap_response: CoAPMessage):
        if self.callback:
            # no need to parse the response, just delete component
            self.callback()
