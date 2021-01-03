import tkinter as tk
import abc


class BasePage(tk.Frame, metaclass=abc.ABCMeta):
    """
    Base abstract class for all GUI pages.
    Sets the frame dimensions and adds the frame to the master grid.
    """

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.grid(row=0, column=0, sticky="nsew")
        self.entries = []
        self.build_gui()

    def show(self):
        self.winfo_toplevel().title(self.title)
        self.reset()
        self.tkraise()

    def reset(self):
        for entry in self.entries:
            entry.delete(0, 'end')
            entry.config(fg='black')

    @abc.abstractmethod
    def build_gui(self):
        pass
