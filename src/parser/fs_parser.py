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
        # filter out empty strings in split_str
        split_str = list(filter(lambda x: x != '', string[1:].split('\x00')))
        directory = Directory(split_str[0])

        for child in split_str[1:]:
            if child[0] == 'f':
                directory.add_child(File(child[1:], FileContent()))
            elif child[0] == 'd':
                directory.add_child(Directory(child[1:]))
        return directory


class FSParser:

    def __init__(self):
        raise NotImplemented(f"Cannot instantiate {self.__class__.__name__} class")

    @staticmethod
    def parse(string: str) -> FSComponent:
        if string[0] == 'f':
            return FileParser.parse(string)
        elif string[0] == 'd':
            return DirectoryParser.parse(string)
