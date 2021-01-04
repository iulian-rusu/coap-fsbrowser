import logging
import queue
import threading
import tkinter as tk
from src.client.client import Client
from src.command.command import FSCommand
from src.gui.browser_page import BrowserPage
from src.gui.connection_page import ConnectionPage


class AppRoot(tk.Tk):
    """
    Top level view of the application.
    Contains GUI pages and the CoAP Client, as well as the thread that runs the client.
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # dictionary with all app pages
        self.pages = {
            'connection': ConnectionPage('Connect', master=self),
            'browser': BrowserPage('Browse Files', master=self)
        }
        self.active_page = None
        self.geometry('1000x600')
        self.resizable(False, False)
        self.show_page('connection')

        self.client = None
        self.client_thread = None
        self.msg_queue = queue.Queue()

    def show_page(self, frame_name: str):
        try:
            self.active_page = self.pages[frame_name]
            self.title(self.active_page.title)
            self.active_page.reset()
            self.active_page.tkraise()
        except KeyError as e:
            logging.error(f"Unknown page: '{e}'")

    def on_connect(self, ip: str, port: int):
        self.client_thread = threading.Thread(target=lambda: self.start_client(ip, port))
        self.client_thread.start()
        self.active_page.display_message('connecting...', color='green', delay=10)

    def start_client(self, ip: str, port: int):
        try:
            self.client = Client(server_ip=ip, server_port=port, msg_queue=self.msg_queue)
            self.show_page('browser')
            self.client.run()
        except OSError as err:
            self.active_page.display_message(err.strerror)

    def set_message_confirmation(self, is_confirmable: bool):
        if self.client:
            self.client.confirmation_req = is_confirmable

    def send_to_client(self, cmd: FSCommand):
        self.msg_queue.put(cmd)

    def destroy(self):
        if self.client:
            self.client.is_running = False
        super().destroy()
