import abc


class FSComponent(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_type() -> str:
        pass


class FileContent(FSComponent):

    def __init__(self, content: str = ''):
        self.content = content

    def __str__(self) -> str:
        return f"[FILE CONTENT]: {self.content if len(self.content) else '<empty>'}"

    @staticmethod
    def get_type() -> str:
        return "FILE CONTENT"


class FSNamedComponent(FSComponent, abc.ABC):
    """
    Abstract base class for file system components with names.
    This type of component is displayed in the GUI by its name.
    When the user opens the component, the opening strategy associated with it
    will be called, which will handle the opening and displaying of the component
    in the correct format.
    """

    def __init__(self, name: str):
        self.name = name


class File(FSNamedComponent):

    def __init__(self, name: str, content: FileContent = FileContent()):
        super().__init__(name)
        self.content = content

    def __str__(self) -> str:
        return f"[FILE]: {self.name} {self.content}"

    @staticmethod
    def get_type() -> str:
        return "FILE"


class Directory(FSNamedComponent):

    def __init__(self, name: str):
        super().__init__(name)
        self.children = []

    def add_child(self, child: FSNamedComponent):
        self.children.append(child)

    def __str__(self) -> str:
        result = f"[DIRECTORY]: {self.name}"
        if len(self.children) > 0:
            for child in self.children:
                result += f"\n\t|--[{child.get_type()}]: {child.name}"
        return result

    @staticmethod
    def get_type() -> str:
        return "DIRECTORY"
