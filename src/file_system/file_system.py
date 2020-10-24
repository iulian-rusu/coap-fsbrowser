import abc
from abc import ABC


class FSComponent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def get_type(self):
        pass


class FSNamedComponent(FSComponent, ABC):
    def __init__(self, name: str):
        self.name = name


class FileContent(FSComponent):
    def __init__(self, string: str = ''):
        if len(string) > 0:
            self.content = string
        else:
            self.content = "<empty>"

    def __str__(self):
        return f"[FILE CONTENT]: {self.content}"

    def get_type(self):
        return "[FILE CONTENT]"


class File(FSNamedComponent):
    def __init__(self, name: str, content: FileContent):
        super().__init__(name)
        self.content = content

    def __str__(self):
        return f"[FILE]: {self.name} {self.content}"

    def get_type(self):
        return "[FILE]"


class Directory(FSNamedComponent):
    def __init__(self, name: str):
        super().__init__(name)
        self.children = set()

    def add_child(self, child: FSNamedComponent):
        self.children.add(child)

    def __str__(self):
        result = f"[DIRECTORY]: {self.name}"
        if len(self.children) > 0:
            result += "\n  L "
            for child in self.children:
                result += f"{child.get_type()}{child.name} "
        return result

    def get_type(self):
        return "[DIRECTORY]"
