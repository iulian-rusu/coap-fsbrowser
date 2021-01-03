import tkinter as tk

from src.gui.base_page import BasePage


class ConnectionPage(BasePage):

    def __init__(self, title: str, *args, **kwargs):
        BasePage.__init__(self, title, *args, **kwargs)
        self.entries.append(self.addr_entry)

    def on_connect(self):
        addr = self.addr_entry.get()
        split_addr = addr.strip().split(':')
        if len(split_addr) != 2:
            self.error_msg('invalid address')
            return
        try:
            ip, port = split_addr
            port = int(port)
            self.master.on_connect(ip, port)
        except ValueError as err:
            self.error_msg(str(err))

    def error_msg(self, msg: str):
        self.addr_entry.delete(0, 'end')
        self.addr_entry.insert(tk.END, msg)

    def build_gui(self):
        self.addr_entry = tk.Entry(self)
        self.addr_entry.config(exportselection='false')
        self.addr_entry.place(anchor='nw', relx='0.4', rely='0.4', width='200')

        self.connect_btn = tk.Button(self)
        self.connect_btn.config(text='connect')
        self.connect_btn.place(anchor='nw', relx='0.45', rely='0.45', width='100')
        self.connect_btn.configure(command=self.on_connect)

        self.addr_lbl = tk.Label(self)
        self.addr_lbl.config(text='Server IPv4 and port:')
        self.addr_lbl.place(anchor='nw', relx='0.25', rely='0.4')

        self.config(height='600', width='1000')
        self.place(anchor='nw')
