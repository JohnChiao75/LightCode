import tkinter as tk
from tkinter import ttk
from editor import LineNumberedEditor
from dialogs import NewFileDialog

class EditorNotebook(tk.Frame):
    def __init__(self, master, theme, font_size, open_file_callback, status_callback):
        super().__init__(master)
        self.theme = theme
        self.font_size = font_size
        self.open_file_callback = open_file_callback
        self.status_callback = status_callback

        # 主框架：左侧Notebook，右侧+按钮
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side="left", fill="both", expand=True)

        self.plus_button = tk.Button(self, text="+", width=3,
                                     command=self._new_tab_dialog,
                                     bg=theme["bg"], fg=theme["fg"])
        self.plus_button.pack(side="right", fill="y", padx=2, pady=2)

        # 存储每个tab对应的编辑器
        self.tabs = {}  # tab_id -> editor widget

    def set_theme(self, theme, font_size):
        self.theme = theme
        self.font_size = font_size
        self.plus_button.config(bg=theme["bg"], fg=theme["fg"])
        for editor in self.tabs.values():
            editor.update_theme(theme, font_size)

    def _new_tab_dialog(self):
        """弹出新建文件对话框"""
        dialog = NewFileDialog(self)
        self.wait_window(dialog)
        filename = dialog.filename
        if filename:
            self.new_tab(filename, content="")

    def new_tab(self, title, content="", filepath=None):
        """新建编辑器标签页"""
        frame = LineNumberedEditor(self.notebook, self.theme, self.font_size,
                                   initial_text=content, filepath=filepath)
        frame.pack(fill="both", expand=True)
        self.notebook.add(frame, text=title)
        self.tabs[frame] = frame
        self.notebook.select(frame)
        # 设置修改状态监听
        frame.text.bind("<<Modified>>", lambda e: self._update_tab_title(frame))
        return frame

    def _update_tab_title(self, editor):
        index = self.notebook.index(editor)
        if index is not None:
            title = self.notebook.tab(index, "text")
            if editor.modified and not title.endswith("*"):
                self.notebook.tab(index, text=title + "*")
            elif not editor.modified and title.endswith("*"):
                self.notebook.tab(index, text=title[:-1])

    def get_current_editor(self):
        current = self.notebook.select()
        if current:
            return self.notebook.nametowidget(current)
        return None

    def close_current_tab(self):
        current = self.get_current_editor()
        if current:
            self.notebook.forget(current)
            del self.tabs[current]
            current.destroy()

    def save_current(self):
        editor = self.get_current_editor()
        if editor:
            if editor.filepath:
                with open(editor.filepath, "w", encoding="utf-8") as f:
                    f.write(editor.get_text())
                editor.modified = False
                self._update_tab_title(editor)
                self.status_callback(f"Saved: {editor.filepath}")
            else:
                self.save_as_current()

    def save_as_current(self):
        editor = self.get_current_editor()
        if editor:
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(defaultextension=".py",
                                                    filetypes=[("Python", "*.py"), ("All files", "*.*")])
            if filepath:
                editor.filepath = filepath
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(editor.get_text())
                editor.modified = False
                idx = self.notebook.index(editor)
                self.notebook.tab(idx, text=filepath.split("/")[-1])
                self._update_tab_title(editor)
                self.status_callback(f"Saved: {filepath}")
