import tkinter as tk
from tkinter import ttk

THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "selectbg": "#cce8ff",
        "selectfg": "#000000",
        "insert": "#000000",
        "line_bg": "#f0f0f0",
        "line_fg": "#808080",
        "tree_bg": "#ffffff",
        "tree_fg": "#000000",
        "tree_select": "#cce8ff"
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#d4d4d4",
        "selectbg": "#264f78",
        "selectfg": "#ffffff",
        "insert": "#ffffff",
        "line_bg": "#1e1e1e",
        "line_fg": "#858585",
        "tree_bg": "#252526",
        "tree_fg": "#cccccc",
        "tree_select": "#3e3e42"
    }
}

def apply_theme(widget, theme_name):
    """递归应用主题到所有子组件（简化版，仅设置关键组件）"""
    theme = THEMES.get(theme_name, THEMES["light"])
    # 注意：tk.Tk需要单独配置，这里只供参考
    try:
        widget.configure(bg=theme["bg"], fg=theme["fg"])
    except:
        pass
    try:
        widget.configure(selectbackground=theme["selectbg"], selectforeground=theme["selectfg"])
    except:
        pass
    try:
        widget.configure(insertbackground=theme["insert"])
    except:
        pass

def get_theme(theme_name):
    return THEMES.get(theme_name, THEMES["light"])