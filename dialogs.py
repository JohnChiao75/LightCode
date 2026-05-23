import tkinter as tk
from tkinter import simpledialog, messagebox

class NewFileDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New File")
        self.geometry("300x100")
        self.filename = None

        tk.Label(self, text="File name:").pack(pady=5)
        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda e: self.ok())

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="OK", command=self.ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left")

        self.grab_set()
        self.entry.focus()

    def ok(self):
        name = self.entry.get().strip()
        if name:
            self.filename = name
            self.destroy()

class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, editor, replace=False):
        super().__init__(parent)
        self.title("Find" + (" and Replace" if replace else ""))
        self.editor = editor
        self.replace = replace
        self.geometry("400x150")

        tk.Label(self, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.find_entry = tk.Entry(self, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)
        self.find_entry.focus()

        if replace:
            tk.Label(self, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.replace_entry = tk.Entry(self, width=30)
            self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Find Next", command=self.find_next).pack(side="left", padx=5)
        if replace:
            tk.Button(btn_frame, text="Replace", command=self.replace_one).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Replace All", command=self.replace_all).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Close", command=self.destroy).pack(side="left", padx=5)

    def find_next(self):
        find_str = self.find_entry.get()
        if not find_str:
            return
        pos = self.editor.text.search(find_str, "insert", "end-1c")
        if not pos:
            pos = self.editor.text.search(find_str, "1.0", "end-1c")
        if pos:
            end = f"{pos}+{len(find_str)}c"
            self.editor.text.tag_remove(tk.SEL, "1.0", "end")
            self.editor.text.tag_add(tk.SEL, pos, end)
            self.editor.text.mark_set("insert", end)
            self.editor.text.see(pos)
        else:
            messagebox.showinfo("Find", "No more occurrences")

    def replace_one(self):
        find_str = self.find_entry.get()
        replace_str = self.replace_entry.get()
        if self.editor.text.tag_ranges(tk.SEL):
            sel_start = self.editor.text.index(tk.SEL_FIRST)
            sel_end = self.editor.text.index(tk.SEL_LAST)
            if self.editor.text.get(sel_start, sel_end) == find_str:
                self.editor.text.delete(sel_start, sel_end)
                self.editor.text.insert(sel_start, replace_str)
        self.find_next()

    def replace_all(self):
        find_str = self.find_entry.get()
        replace_str = self.replace_entry.get()
        content = self.editor.get_text()
        new_content = content.replace(find_str, replace_str)
        if new_content != content:
            self.editor.set_text(new_content)
            self.editor.modified = True
            self.editor.text.edit_modified(True)
            self.editor.text.event_generate("<<Modified>>")
            messagebox.showinfo("Replace All", f"Replaced all occurrences of '{find_str}'")