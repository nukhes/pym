import os
import tkinter.filedialog
from tkinter import ttk

class FileExplorer(ttk.Treeview):
    def __init__(self, master, on_file_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.heading("#0", text="Project", anchor="w")
        self.on_file_click = on_file_click
        self.bind("<<TreeviewSelect>>", self._on_select)

    def populate_tree(self, path):
        self.delete(*self.get_children())
        self.insert("", "end", text=path, values=[path], open=True)
        self._populate_children("", path)

    def _populate_children(self, parent, path):
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                node = self.insert(parent, "end", text=item, values=[item_path], open=False)
                self._populate_children(node, item_path)
            else:
                self.insert(parent, "end", text=item, values=[item_path])

    def _on_select(self, event):
        if self.on_file_click:
            selected_item = self.selection()
            if not selected_item:
                return
            item_values = self.item(selected_item, "values")
            if item_values:
                item_path = item_values[0]
                if os.path.isfile(item_path):
                    self.on_file_click(item_path)

    def open_folder(self, event=None):
        path = tkinter.filedialog.askdirectory()
        if path:
            self.populate_tree(path)
