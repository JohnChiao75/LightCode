import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path

class FileTree(tk.Frame):
    def __init__(self, master, theme, open_file_callback):
        super().__init__(master, bg=theme["tree_bg"])
        self.theme = theme
        self.open_file_callback = open_file_callback
        self.tree = ttk.Treeview(self, selectmode="browse")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        # 滚动条
        vbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vbar.set)

    def set_theme(self, theme):
        self.theme = theme
        self.config(bg=theme["tree_bg"])
        # ttk treeview 样式需单独配置，简化处理
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"],
                        fieldbackground=theme["tree_bg"])
        style.map('Treeview', background=[('selected', theme["tree_select"])])

    def load_directory(self, path):
        self.tree.delete(*self.tree.get_children())
        self.root_path = Path(path).resolve()
        self._insert_node("", self.root_path)

    def _insert_node(self, parent, path):
        node = self.tree.insert(parent, "end", text=path.name, open=False)
        if path.is_dir():
            self.tree.insert(node, "end", text="dummy")  # 占位，用于懒加载
            self.tree.set(node, "type", "dir")
        else:
            self.tree.set(node, "type", "file")
        return node

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        path = self._get_full_path(item)
        if path.is_file():
            self.open_file_callback(str(path))
        elif path.is_dir():
            # 展开或加载子节点
            if self.tree.get_children(item) and self.tree.item(self.tree.get_children(item)[0], "text") == "dummy":
                self.tree.delete(self.tree.get_children(item)[0])
                for child in path.iterdir():
                    self._insert_node(item, child)
            self.tree.item(item, open=not self.tree.item(item, "open"))

    def _get_full_path(self, item):
        parts = []
        while item:
            parts.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return self.root_path.parent / Path(*parts)  # 小心根路径

class VCSPanel(tk.Frame):
    """VCS 简单占位面板"""
    def __init__(self, master, theme):
        super().__init__(master, bg=theme["bg"])
        self.label = tk.Label(self, text="Git integration (placeholder)", bg=theme["bg"], fg=theme["fg"])
        self.label.pack(padx=10, pady=10)

    def set_theme(self, theme):
        self.config(bg=theme["bg"])
        self.label.config(bg=theme["bg"], fg=theme["fg"])

class Sidebar(tk.Frame):
    def __init__(self, master, theme, open_file_callback):
        super().__init__(master, bg=theme["bg"], width=200)
        self.pack_propagate(False)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.file_tree = FileTree(self.notebook, theme, open_file_callback)
        self.vcs_panel = VCSPanel(self.notebook, theme)

        self.notebook.add(self.file_tree, text="Files")
        self.notebook.add(self.vcs_panel, text="VCS")

    def set_theme(self, theme):
        self.config(bg=theme["bg"])
        self.file_tree.set_theme(theme)
        self.vcs_panel.set_theme(theme)

    def load_directory(self, path):
        self.file_tree.load_directory(path)