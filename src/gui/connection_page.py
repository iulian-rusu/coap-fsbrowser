import tkinter as tk

from src.gui.base_page import BasePage


class ConnectionPage(BasePage):
    def __init__(self, title: str, *args, **kwargs):
        BasePage.__init__(self, title, *args, **kwargs)
        self.entries.append(self.addr_entry)

    def display_message(self, msg: str, duration: int = 2, color: str = 'red'):
        self._display_message_impl(msg, duration, color, anchor='nw', relx='0.05', rely='0.35', width='900')

    def on_connect(self):
        addr = self.addr_entry.get()
        split_addr = addr.strip().split(':')
        if len(split_addr) != 2:
            self.display_message('Invalid address')
            return
        try:
            ip, port = split_addr
            port = int(port)
            if port < 0 or port > 65535:
                raise ValueError
            self.master.on_connect(ip, port)
        except ValueError:
            self.display_message('Invalid port')

    def build_gui(self):
        self.addr_entry = tk.Entry(self)
        self.addr_entry.place(anchor='nw', relx='0.4', rely='0.4', width='200')
        self.addr_entry.bind('<Return>', lambda e: self.on_connect())

        self.connect_btn = tk.Button(self)
        self.connect_btn.config(text='Connect')
        self.connect_btn.place(anchor='nw', relx='0.45', rely='0.45', width='100')
        self.connect_btn.configure(command=self.on_connect)

        self.addr_lbl = tk.Label(self)
        self.addr_lbl.config(text='Server address:')
        self.addr_lbl.place(anchor='nw', relx='0.25', rely='0.4')

        self.config(height='600', width='1000')
        self.place(anchor='nw')
