import tkinter as tk
import tkinter.ttk as ttk

from src.command.command import FSCommand, OpenCommand, BackCommand, DeleteCommand
from src.file_system.file_system import FSNamedComponent, File, Directory, FSComponent, FileContent
from src.gui.creation_box import CreationBox
from src.gui.base_page import BasePage
from src.gui.file_editor import FileEditor


class BrowserPage(BasePage):
    BUTTONS_RELY = '0.91'

    def __init__(self, title: str, *args, **kwargs):
        BasePage.__init__(self, title, *args, **kwargs)
        self.entries.append(self.path_entry)
        self.components = []
        self.selected_component = None

    def reset(self):
        super().reset()
        self.path_entry.insert(tk.END, '')

    def display_message(self, msg: str, duration: int = 2, color: str = 'red'):
        self._display_message_impl(msg, duration, color, anchor='nw', relx='0.1', width='880', height='30')

    def send_to_client(self, cmd: FSCommand):
        self.master.send_to_client(cmd)

    def on_component_select(self, event):
        component_iid = self.component_view.identify_row(event.y)
        if component_iid != '':
            component_data = self.component_view.item(component_iid)['values']
            component_name = component_data[0]
            component = next((comp for comp in self.components if comp.name == component_name), None)
            self.selected_component = component

    def open_component(self, component: FSComponent, callback_data: FSComponent):
        if isinstance(callback_data, FileContent):
            if isinstance(component, File):
                component.content = callback_data
                FileEditor(master=self, target=component)
            else:
                self.display_message('Incorrect server data: Received file content', duration=5)
        elif isinstance(callback_data, Directory):
            self.open_dir(callback_data)

    def open_dir(self, directory: Directory):
        if not isinstance(directory, Directory):
            self.display_message('Incorrect server data: Expected directory', duration=5)
            return
        self.components = directory.children
        self.component_view.delete(*self.component_view.get_children())
        for comp in self.components:
            row = (comp.name, comp.get_type())
            self.component_view.insert('', 'end', values=row)
        self.path_entry.delete(0, 'end')
        self.path_entry.insert(tk.END, directory.name)

    def remove_component(self, component: FSNamedComponent):
        self.components.remove(component)
        self.component_view.delete(*self.component_view.get_children())
        for comp in self.components:
            row = (comp.name, comp.get_type())
            self.component_view.insert('', 'end', values=row)
        self.selected_component = None

    def insert_component(self, component: FSNamedComponent):
        row = (component.name, component.get_type())
        self.component_view.insert('', 'end', values=row)
        self.components.append(component)

    def on_set_path(self):
        dir_path = self.path_entry.get()
        cmd = OpenCommand(dir_path, callback=self.open_dir)
        self.send_to_client(cmd)

    def on_open(self):
        if self.selected_component:
            cmd = OpenCommand(self.selected_component.name,
                              callback=lambda data: self.open_component(self.selected_component, data))
            self.send_to_client(cmd)

    def on_back(self):
        cmd = BackCommand(self.path_entry.get(), callback=self.open_dir)
        self.send_to_client(cmd)

    def on_new_dir(self):
        CreationBox(master=self, title='New Directory', is_file=False)

    def on_new_file(self):
        CreationBox(master=self, title='New File', is_file=True)

    def on_delete(self):
        if self.selected_component:
            cmd = DeleteCommand(self.selected_component.name,
                                callback=lambda: self.remove_component(self.selected_component))
            self.send_to_client(cmd)

    def on_confirmation_toggle(self):
        self.master.set_message_confirmation(bool(self.is_confirmable.get()))

    def build_gui(self):
        self.path_lbl = tk.Label(self)
        self.path_lbl.config(text='Path:', font='bold')
        self.path_lbl.place(anchor='nw', height='30', relx='0.03')

        self.path_entry = tk.Entry(self)
        self.path_entry.config(exportselection='false')
        self.path_entry.place(anchor='nw', relx='0.1', width='880', height='30')
        self.path_entry.bind('<Return>', lambda e: self.on_set_path())

        self.component_view = ttk.Treeview(self, columns=(1, 2), show='headings')
        self.component_view.heading(1, text='Name')
        self.component_view.heading(2, text='Type')
        self.component_view.place(anchor='nw', height='500', width='1000', rely='0.05')
        self.component_view.bind('<Button 1>', self.on_component_select)

        self.back_btn = ttk.Button(self)
        self.back_btn.config(text='Back')
        self.back_btn.place(anchor='nw', height='40', relx='0.01', rely=self.BUTTONS_RELY, width='150')
        self.back_btn.configure(command=self.on_back)

        self.open_btn = ttk.Button(self)
        self.open_btn.config(text='Open')
        self.open_btn.place(anchor='nw', height='40', relx='0.16', rely=self.BUTTONS_RELY, width='150')
        self.open_btn.configure(command=self.on_open)

        self.new_dir_btn = ttk.Button(self)
        self.new_dir_btn.config(text='New Directory')
        self.new_dir_btn.place(anchor='nw', height='40', relx='0.31', rely=self.BUTTONS_RELY, width='150')
        self.new_dir_btn.configure(command=self.on_new_dir)

        self.new_file_btn = ttk.Button(self)
        self.new_file_btn.config(text='New File')
        self.new_file_btn.place(anchor='nw', height='40', relx='0.46', rely=self.BUTTONS_RELY, width='150')
        self.new_file_btn.configure(command=self.on_new_file)

        self.delete_btn = tk.Button(self)
        self.delete_btn.config(activebackground='#ff2326', background='#ff5e60', text='Delete')
        self.delete_btn.place(anchor='nw', height='40', relx='0.84', rely=self.BUTTONS_RELY, width='150')
        self.delete_btn.configure(command=self.on_delete)

        self.is_confirmable = tk.IntVar()
        self.confirmable_chk = tk.Checkbutton(self, text='Confirmable', variable=self.is_confirmable,
                                              onvalue=1, offvalue=0, command=self.on_confirmation_toggle)
        self.confirmable_chk.place(anchor='nw', height='40', relx='0.62', rely=self.BUTTONS_RELY, )

        self.config(height='600', width='1000')
        self.place(anchor='nw', x='0', y='0')
