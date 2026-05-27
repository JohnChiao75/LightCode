import tkinter as tk
from tkinter import font as tkfont

class LineNumberText(tk.Text):
    def __init__(self, master, theme, font_size, **kwargs):
        self.theme = theme
        self.font_size = font_size
        self.font = tkfont.Font(family="Consolas", size=font_size)
        super().__init__(master, wrap="none", undo=True, font=self.font,
                         bg=theme["bg"], fg=theme["fg"],
                         selectbackground=theme["selectbg"],
                         selectforeground=theme["selectfg"],
                         insertbackground=theme["insert"], **kwargs)
        self.bind("<KeyRelease>", self._on_change)
        self.bind("<ButtonRelease-1>", self._on_change)
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Configure>", self._on_change)

    def _on_change(self, event=None):
        self.master.update_line_numbers()

    def _on_scroll(self, event):
        self.master.on_text_scroll(event)
        return None

    def get_line_count(self):
        return int(self.index('end-1c').split('.')[0])

    def update_line_numbers(self):
        pass  # 实际由容器调用

class LineNumberedEditor(tk.Frame):
    def __init__(self, master, theme, font_size, initial_text="", filepath=None):
        super().__init__(master, bg=theme["bg"])
        self.theme = theme
        self.font_size = font_size
        self.filepath = filepath
        self.modified = False

        # 行号区域
        self.line_numbers = tk.Text(self, width=5, padx=3, takefocus=0, border=0,
                                    background=theme["line_bg"], foreground=theme["line_fg"],
                                    font=("Consolas", font_size), wrap="none",
                                    state="disabled")
        self.line_numbers.pack(side="left", fill="y")

        # 文本区域
        self.text = LineNumberText(self, theme, font_size)
        self.text.pack(side="right", fill="both", expand=True)

        # 插入初始文本
        if initial_text:
            self.text.insert("1.0", initial_text)
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<Key>", self._on_modified)
        self._update_line_numbers()

        # 滚动同步
        self.text.vbar = None  # 将在外部设置滚动条时关联

    def _on_modified(self, event=None):
        self.modified = self.text.edit_modified()
        self.text.edit_modified(False)
        self._update_line_numbers()

    def _update_line_numbers(self):
        line_count = int(self.text.index('end-1c').split('.')[0])
        line_numbers_str = "\n".join(str(i) for i in range(1, line_count+1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers_str)
        self.line_numbers.config(state="disabled")
        # 同步滚动
        self.line_numbers.yview_moveto(self.text.yview()[0])

    def update_theme(self, theme, font_size):
        self.theme = theme
        self.font_size = font_size
        self.config(bg=theme["bg"])
        self.line_numbers.config(bg=theme["line_bg"], fg=theme["line_fg"],
                                 font=("Consolas", font_size))
        self.text.config(bg=theme["bg"], fg=theme["fg"],
                         selectbackground=theme["selectbg"],
                         selectforeground=theme["selectfg"],
                         insertbackground=theme["insert"],
                         font=("Consolas", font_size))
        self._update_line_numbers()

    def get_text(self):
        return self.text.get("1.0", "end-1c")

    def set_text(self, content):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_modified(False)
        self.modified = False
        self._update_line_numbers()

    def on_text_scroll(self, event):
        self.line_numbers.yview_moveto(self.text.yview()[0])
        return None

    def attach_scrollbar(self, vbar):
        self.text.config(yscrollcommand=vbar.set)
        vbar.config(command=self._scroll_text)
        self.text.vbar = vbar

    def _scroll_text(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)