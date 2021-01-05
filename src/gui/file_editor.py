import tkinter as tk

from src.command.command import SaveCommand
from src.file_system.file_system import File, FileContent


class FileEditor(tk.Toplevel):
    """
    Window that contains the content of a file. Apperas when opening a file.
    Allows the user to change the file content and save it.
    Saving changes requires confirmation from the server.
    """
    def __init__(self, target: File, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.title(target.name)
        self.geometry('1000x600')
        self.resizable(False, False)
        self.build_gui()

    def on_save(self):
        content = self.file_content.get('1.0', tk.END)
        cmd = SaveCommand(self.target.name, content, callback=lambda: self.set_file_content(content))
        self.master.send_to_client(cmd)
        self.destroy()

    def set_file_content(self, content: str):
        self.target.content = FileContent(content)

    def build_gui(self):
        self.main_frame = tk.Frame(master=self)
        self.file_content = tk.Text(self.main_frame)
        self.file_content.insert(tk.END, self.target.content.content)
        self.file_content.place(anchor='nw', height='550', width='1000')

        self.save_btn = tk.Button(self.main_frame)
        self.save_btn.config(activebackground='#5cff5c', background='#91ff98', text='save')
        self.save_btn.place(anchor='nw', height='40', relx='0.01', rely='0.925', width='150')
        self.save_btn.configure(command=self.on_save)

        self.main_frame.config(height='600', width='1000')
        self.main_frame.place(anchor='nw')
