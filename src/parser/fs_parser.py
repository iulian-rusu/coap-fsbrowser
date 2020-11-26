from src.client.exceptions import InvalidFormat
from src.file_system.file_system import File, Directory, FSComponent, FileContent


class FileParser:

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def parse(string: str) -> FileContent:
        return FileContent(string[1:])


class DirectoryParser:

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def parse(string: str) -> Directory:
        # split the input and remove any empty strings
        split_str = list(filter(lambda x: x != '', string[1:].split('\x00')))
        directory = Directory(split_str[0])

        for child in split_str[1:]:
            if child[0] == 'f':
                directory.add_child(File(child[1:]))
            elif child[0] == 'd':
                directory.add_child(Directory(child[1:]))
            else:
                raise InvalidFormat("Invalid header for directory child")
        return directory


class FSParser:
    """
    Class that is responsible for parsing encoded file system information.
    The FSParser.parse static method receives an encoded string
    representing the contents of the current directory/file and returns
    the FSComponent encoded in it.
    """

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def parse(string: str) -> FSComponent:
        if string[0] == 'f':
            return FileParser.parse(string)
        elif string[0] == 'd':
            return DirectoryParser.parse(string)
        else:
            raise InvalidFormat("Invalid header for file system component")