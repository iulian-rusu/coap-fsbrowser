import abc
from typing import Callable

from src.client.coap_message import CoAP
from src.file_system.fs_parser import FSParser


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

    @staticmethod
    @abc.abstractmethod
    def response_required() -> bool:
        pass

    @property
    def coap_payload(self) -> str:
        raise NotImplementedError('Attempt to access property of abstract base class FSCommand')

    @abc.abstractmethod
    def exec(self, response_data: str):
        """
        Called once the client has reveived an OK repsonse from the server.
        Executes the command on the client-side by means of a given callback function.

        :param response_data: The response from the server, may be unused in the callback.
        :return: None
        """
        pass


class BackCommand(FSCommand):
    """
    Class that implements the BACK command.
    Allows the user to go to the previous directory.

    CoAP payload = <CMD_BACK><dir_name>
    """

    def __init__(self, current_dir_name: str, callback: Callable = None):
        super().__init__(callback)
        self.current_dir_name = current_dir_name

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_GET

    @staticmethod
    def response_required() -> bool:
        return True

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_BACK}{self.current_dir_name}'

    def exec(self, response_data: str):
        if self.callback:
            # parse response and get the directory to go to
            new_dir = FSParser.parse(response_data)
            self.callback(new_dir)


class OpenCommand(FSCommand):
    """
    Class that implements the OPEN command.
    Allows the user to open a directory or file.

    CoAP payload = <CMD_OPEN><component_name>
    """

    def __init__(self, component_name: str, callback: Callable = None):
        super().__init__(callback)
        self.component_name = component_name

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_GET

    @staticmethod
    def response_required() -> bool:
        return True

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_OPEN}{self.component_name}'

    def exec(self, response_data: str):
        if self.callback:
            # Parse response and get the component to be opened
            to_open = FSParser.parse(response_data)
            self.callback(to_open)


class SaveCommand(FSCommand):
    """
    Class that implements the SAVE command.
    Allows the user to save the state of the opened file.

    CoAP payload = <CMD_SAVE><file_name>\x00<file_content>
    """

    def __init__(self, file_name: str, content: str, callback: Callable = None):
        super().__init__(callback)
        self.file_name = file_name
        self.content = content

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_POST

    @staticmethod
    def response_required() -> bool:
        return False

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_SAVE}{self.file_name}\x00{self.content}'

    def exec(self, response_data: str):
        if self.callback:
            # No need to parse the response, just save the current file content
            self.callback()


class NewFileCommand(FSCommand):
    """
    Class that implements the NEW FILE command.
    Allows the user to create a file in the current directory.

    CoAP payload = <CMD_NEWF><file_name>
    """

    def __init__(self, new_file_name: str, callback: Callable = None):
        super().__init__(callback)
        self.new_file_name = new_file_name

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_POST

    @staticmethod
    def response_required() -> bool:
        return False

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_NEWF}{self.new_file_name}'

    def exec(self, response_data: str):
        if self.callback:
            # No need to parse the response, just create an empty file
            self.callback()


class NewDirCommand(FSCommand):
    """
    Class that implements the NEW DIR command.
    Allows the user to create a directory in the current directory.

    CoAP payload = <CMD_NEWD><dir_name>
    """

    def __init__(self, new_dir_name: str, callback: Callable = None):
        super().__init__(callback)
        self.new_dir_name = new_dir_name

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_POST

    @staticmethod
    def response_required() -> bool:
        return False

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_NEWD}{self.new_dir_name}'

    def exec(self, response_data: str):
        if self.callback:
            # No need to parse the response, just create an empty directory
            self.callback()


class DeleteCommand(FSCommand):
    """
    Class that implements the DELETE command.
    Allows the user to delete the specified component.

    CoAP payload = <CMD_DEL><component_name>
    """

    def __init__(self, component_name: str, callback: Callable = None):
        super().__init__(callback)
        self.component_name = component_name

    @staticmethod
    def get_coap_class() -> int:
        return CoAP.CLASS_METHOD

    @staticmethod
    def get_coap_code() -> int:
        return CoAP.CODE_DELETE

    @staticmethod
    def response_required() -> bool:
        return False

    @property
    def coap_payload(self) -> str:
        return f'{FSCommand.CMD_DEL}{self.component_name}'

    def exec(self, response_data: str):
        if self.callback:
            # No need to parse the response, just delete the component
            self.callback()