import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import subprocess

from config import load_config, save_config, DEFAULT_CONFIG
from theme import get_theme
from sidebar import Sidebar
from notebook import EditorNotebook
from dialogs import FindReplaceDialog
from debugger import Debugger

class LightCode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LightCode Editor")
        self.root.geometry("1200x700")

        # 加载配置
        self.config = load_config()
        self.current_theme = self.config["theme"]
        self.font_size = self.config["font_size"]
        self.theme = get_theme(self.current_theme)

        # 设置全局样式
        self.root.configure(bg=self.theme["bg"])

        # 菜单栏
        self.create_menu()

        # 主布局：PanedWindow 分割侧栏和编辑区
        self.main_pane = tk.PanedWindow(self.root, orient="horizontal", bg=self.theme["bg"])
        self.main_pane.pack(fill="both", expand=True)

        # 侧栏
        self.sidebar = Sidebar(self.main_pane, self.theme, self.open_file)
        self.main_pane.add(self.sidebar, width=250)

        # 编辑区域（多标签）
        self.notebook = EditorNotebook(self.main_pane, self.theme, self.font_size,
                                       self.open_file, self.update_status)
        self.main_pane.add(self.notebook, width=800)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken",
                                   anchor="w", bg=self.theme["bg"], fg=self.theme["fg"])
        self.status_bar.pack(side="bottom", fill="x")

        # 调试器
        self.debugger = Debugger(self.root, self.config, self.update_status)

        # 默认打开一个空白标签
        self.notebook.new_tab("untitled", content="")

        # 绑定快捷键
        self.bind_shortcuts()

        # 关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_file_dialog, accelerator="Ctrl+O")
        file_menu.add_command(label="打开目录", command=self.open_directory)
        file_menu.add_command(label="保存", command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self.save_as_current, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="编辑 Config.json", command=self.edit_config)
        file_menu.add_separator()
        file_menu.add_command(label="关闭", command=self.close_current_tab)
        file_menu.add_command(label="退出", command=self.on_exit)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="剪切", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="查找", command=self.find, accelerator="Ctrl+F")
        edit_menu.add_command(label="替换", command=self.replace, accelerator="Ctrl+H")

        # 调试菜单
        debug_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="调试", menu=debug_menu)
        debug_menu.add_command(label="启动调试", command=self.start_debug, accelerator="F5")
        debug_menu.add_command(label="设置调试命令", command=self.set_debug_command)

        # 主题菜单（视图）
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="亮色主题", command=lambda: self.switch_theme("light"))
        view_menu.add_command(label="暗色主题", command=lambda: self.switch_theme("dark"))
        view_menu.add_separator()
        view_menu.add_command(label="增大字体", command=self.increase_font)
        view_menu.add_command(label="减小字体", command=self.decrease_font)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.root.bind("<Control-s>", lambda e: self.save_current())
        self.root.bind("<Control-S>", lambda e: self.save_as_current())
        self.root.bind("<Control-x>", lambda e: self.cut())
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-f>", lambda e: self.find())
        self.root.bind("<Control-h>", lambda e: self.replace())
        self.root.bind("<F5>", lambda e: self.start_debug())

    def update_status(self, msg):
        self.status_var.set(msg)

    def get_current_editor(self):
        return self.notebook.get_current_editor()

    # ---- 文件操作 ----
    def new_file(self):
        self.notebook.new_tab("untitled", content="")

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.open_file(filepath)

    def open_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            title = os.path.basename(filepath)
            self.notebook.new_tab(title, content=content, filepath=filepath)
            self.update_status(f"Opened: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

    def open_directory(self):
        dirpath = filedialog.askdirectory()
        if dirpath:
            self.sidebar.load_directory(dirpath)
            self.update_status(f"Loaded directory: {dirpath}")

    def save_current(self):
        self.notebook.save_current()

    def save_as_current(self):
        self.notebook.save_as_current()

    def edit_config(self):
        config_path = os.path.expanduser("~/.lightcode/config.json")
        self.open_file(config_path)

    def close_current_tab(self):
        editor = self.get_current_editor()
        if editor and editor.modified:
            res = messagebox.askyesnocancel("Save", "File has been modified. Save?")
            if res is True:
                self.save_current()
            elif res is None:
                return
        self.notebook.close_current_tab()

    # ---- 编辑操作 ----
    def cut(self):
        editor = self.get_current_editor()
        if editor:
            editor.text.event_generate("<<Cut>>")

    def copy(self):
        editor = self.get_current_editor()
        if editor:
            editor.text.event_generate("<<Copy>>")

    def paste(self):
        editor = self.get_current_editor()
        if editor:
            editor.text.event_generate("<<Paste>>")

    def undo(self):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.text.edit_undo()
            except:
                pass

    def redo(self):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.text.edit_redo()
            except:
                pass

    def find(self):
        editor = self.get_current_editor()
        if editor:
            FindReplaceDialog(self.root, editor, replace=False)

    def replace(self):
        editor = self.get_current_editor()
        if editor:
            FindReplaceDialog(self.root, editor, replace=True)

    # ---- 调试 ----
    def start_debug(self):
        editor = self.get_current_editor()
        if editor and editor.filepath:
            self.debugger.start_debug(editor.filepath, lang="python")
        else:
            messagebox.showwarning("Debug", "Please save the current file before debugging.")

    def set_debug_command(self):
        from tkinter import simpledialog
        new_cmd = simpledialog.askstring("Debug Command", "Python debug command:", initialvalue=self.config["debugger"].get("python", "python3"))
        if new_cmd:
            self.config["debugger"]["python"] = new_cmd
            save_config(self.config)
            self.update_status("Debug command updated")

    # ---- 主题与字体 ----
    def switch_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme = get_theme(theme_name)
        self.root.configure(bg=self.theme["bg"])
        self.status_bar.config(bg=self.theme["bg"], fg=self.theme["fg"])
        self.sidebar.set_theme(self.theme)
        self.notebook.set_theme(self.theme, self.font_size)
        self.config["theme"] = theme_name
        save_config(self.config)
        self.update_status(f"Theme switched to {theme_name}")

    def increase_font(self):
        self.font_size += 1
        self.update_font_size()

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 1
            self.update_font_size()

    def update_font_size(self):
        self.notebook.set_theme(self.theme, self.font_size)
        self.config["font_size"] = self.font_size
        save_config(self.config)
        self.update_status(f"Font size: {self.font_size}")

    def on_exit(self):
        # 检查所有未保存文件
        for editor in self.notebook.tabs.values():
            if editor.modified:
                res = messagebox.askyesnocancel("Save", "Some files are modified. Save before exit?")
                if res is True:
                    self.save_current()
                elif res is None:
                    return
                break
        save_config(self.config)
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LightCode()
    app.run()