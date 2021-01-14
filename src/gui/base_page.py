import threading
import time
import tkinter as tk
import abc


class BasePage(tk.Frame, metaclass=abc.ABCMeta):
    """
    Base abstract class for all GUI pages.
    Contains a single widget which is sued to display messages for the user.
    """

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_lbl = tk.Label(master=self)
        self.current_message_id = 0
        self.title = title
        self.grid(row=0, column=0, sticky="nsew")
        self.entries = []
        self.build_gui()

    @abc.abstractmethod
    def display_message(self, msg: str, duration: int = 2, color: str = 'red'):
        pass

    def _display_message_impl(self, msg: str, duration: int = 2, color: str = 'red', **place_kwargs):
        """
        This method displays a message in the GUI for a druation of time.
        The exact postion, size, color and duration of the message can be specified with the arguments.

        :param msg: The message to be displayed in the GUI
        :param color: The color of the message, must be compatible with tk.Label.
        :param duration: The duration of the message on the screen. -1 for unlimited duration.
        :param place_kwargs: Keyword arguments for tk.Label.place() that specify the position and size of the message.
        :return: None
        """
        self.message_lbl.config(text=msg, fg=color)
        self.message_lbl.place(**place_kwargs)
        self.message_lbl.tkraise()
        self.current_message_id += 1
        if duration >= 0:
            threading.Thread(target=lambda: self._remove_after_delay(duration, self.current_message_id)).start()

    def _remove_after_delay(self, delay: int, _id: int):
        time.sleep(delay)
        if _id == self.current_message_id:
            self.current_message_id -= 1
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
