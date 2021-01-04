import time
import tkinter as tk
import abc


class BasePage(tk.Frame, metaclass=abc.ABCMeta):
    """
    Base abstract class for all GUI pages.
    Sets the frame dimensions and adds the frame to the master grid.
    """

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_lbl = tk.Label(master=self)
        self.title = title
        self.grid(row=0, column=0, sticky="nsew")
        self.entries = []
        self.build_gui()

    def display_message(self, msg: str, color: str = 'red', delay: int = 2):
        pass

    def remove_after_delay(self, delay: int):
        time.sleep(delay)
        self.message_lbl.place_forget()
        self.message_lbl.config(fg='black')

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
