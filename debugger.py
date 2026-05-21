import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext

class DebugConsole(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Debug Console")
        self.geometry("600x400")
        self.config = config

        self.text_area = scrolledtext.ScrolledText(self, wrap="word")
        self.text_area.pack(fill="both", expand=True)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(fill="x")
        self.input_entry = tk.Entry(self.entry_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_input)
        self.send_button.pack(side="right", padx=5, pady=5)

        self.process = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def write_output(self, text):
        self.text_area.insert("end", text)
        self.text_area.see("end")

    def send_input(self):
        cmd = self.input_entry.get()
        if cmd and self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
                self.input_entry.delete(0, "end")
            except:
                self.write_output("Process not running.\n")

    def on_close(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.destroy()

class Debugger:
    def __init__(self, master, config, status_callback):
        self.master = master
        self.config = config
        self.status_callback = status_callback
        self.console = None

    def start_debug(self, filepath, lang="python"):
        if not filepath:
            self.status_callback("No file to debug")
            return
        cmd_template = self.config["debugger"].get(lang, "")
        if not cmd_template:
            cmd_template = "python3"
        cmd = f"{cmd_template} {filepath}"
        self.status_callback(f"Running: {cmd}")

        if self.console is None or not self.console.winfo_exists():
            self.console = DebugConsole(self.master, self.config)
        else:
            self.console.lift()
        self.console.write_output(f"> {cmd}\n")

        def run():
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                        text=True)
                self.console.process = proc
                for line in iter(proc.stdout.readline, ''):
                    self.console.write_output(line)
                for line in iter(proc.stderr.readline, ''):
                    self.console.write_output(line)
                proc.wait()
                self.console.write_output(f"\nProcess finished with exit code {proc.returncode}\n")
                self.console.process = None
            except Exception as e:
                self.console.write_output(f"Error: {e}\n")

        threading.Thread(target=run, daemon=True).start()