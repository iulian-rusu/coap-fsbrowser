import tkinter as tk

from src.command.command import NewFileCommand, NewDirCommand
from src.file_system.file_system import File, Directory


class CreationBox(tk.Toplevel):
    """
    Window that appears when the user wants to create a new file or directory.
    Creating the component requires confirmation from the server.
    """

    def __init__(self, title: str, is_file: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.is_file = is_file
        self.geometry('500x150')
        self.resizable(False, False)
        self.build_gui()

    def on_create(self):
        name = self.name_entry.get().strip()
        if len(name) == 0:
            return
        if self.is_file:
            cmd = NewFileCommand(new_file_name=name, callback=lambda: self.master.insert_component(File(name)))
        else:
            cmd = NewDirCommand(new_dir_name=name, callback=lambda: self.master.insert_component(Directory(name)))
        self.master.send_to_client(cmd)
        self.destroy()

    def build_gui(self):
        self.main_frame = tk.Frame(master=self)
        self.name_entry = tk.Entry(self.main_frame)
        self.name_entry.place(anchor='nw', height='40', width='400', relx='0.1', rely='0.1')

        self.create_btn = tk.Button(self.main_frame)
        self.create_btn.config(activebackground='#5cff5c', background='#91ff98', text='create')
        self.create_btn.place(anchor='nw', height='50', relx='0.3', rely='0.5', width='200')
        self.create_btn.configure(command=self.on_create)

        self.main_frame.config(height='150', width='500')
        self.main_frame.place(anchor='nw')
