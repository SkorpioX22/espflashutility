"""
ESP Flash Utility (ESPtool GUI) — v1.0 Dark Edition
Author: SkorpioX22
Repository: https://github.com/SkorpioX22/espflashutility

A sleek dark GUI for flashing ESP chips using esptool with Python -m.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import subprocess
import threading
import serial.tools.list_ports
import sys
import os
import webbrowser

APP_TITLE = "ESP Flash Utility (ESPtool GUI) — v1.0"
REPO_URL = "https://github.com/SkorpioX22/espflashutility"

FONT = ("JetBrains Mono", 10)
FONT_BOLD = ("JetBrains Mono", 11, "bold")

BG_COLOR = "#0f0f0f"
FG_COLOR = "#e0e0e0"
ACCENT = "#00ff9d"
ERROR_COLOR = "#ff5555"
STATUS_BG = "#1a1a1a"


class SlideStatusBar(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.configure(style="Status.TFrame")
        self.msg = tk.StringVar(value="")
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠏"]
        self._spin = 0
        self._run = False

        self.columnconfigure(1, weight=1)
        self.lbl_spin = ttk.Label(self, text="", style="Status.TLabel", font=FONT)
        self.lbl_text = ttk.Label(self, textvariable=self.msg, style="Status.TLabel", font=FONT)
        self.lbl_spin.grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.lbl_text.grid(row=0, column=1, sticky="w")

        self._visible = False
        self._y_show = None
        self._y_hide = None

    def show(self, text, spin=False):
        self.msg.set(text)
        if not self._visible:
            self._slide_in()
        self._run = spin
        if spin:
            self._animate()

    def clear(self):
        self._run = False
        self.msg.set("")
        if self._visible:
            self._slide_out()

    def _animate(self):
        if not self._run:
            self.lbl_spin.config(text="")
            return
        self.lbl_spin.config(text=self.spinner_chars[self._spin % len(self.spinner_chars)])
        self._spin += 1
        self.after(100, self._animate)

    def place_bottom(self, height=30):
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        y_show = h - height - 5
        y_hide = h + 10
        self._y_show, self._y_hide = y_show, y_hide
        self.place(x=0, y=y_hide, width=w, height=height)

    def _slide_in(self):
        if self._y_show is None:
            self.place_bottom()
        start, end = self._y_hide, self._y_show
        step = (end - start) / 15
        def anim(i=0):
            y = int(start + step * i)
            self.place(y=y)
            if i < 15:
                self.after(10, anim, i + 1)
            else:
                self.place(y=end)
                self._visible = True
        anim()

    def _slide_out(self):
        start, end = self._y_show, self._y_hide
        step = (end - start) / 15
        def anim(i=0):
            y = int(start + step * i)
            self.place(y=y)
            if i < 15:
                self.after(10, anim, i + 1)
            else:
                self.place(y=end)
                self._visible = False
        anim()


class ESPFlashUtility:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.configure(bg=BG_COLOR)
        root.minsize(760, 540)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
        style.configure("TButton", background="#1a1a1a", foreground=FG_COLOR, font=FONT, padding=6)
        style.map("TButton", background=[("active", ACCENT)], foreground=[("active", BG_COLOR)])
        style.configure("TCombobox", fieldbackground="#1a1a1a", background="#1a1a1a", foreground=FG_COLOR)
        style.configure("Status.TFrame", background=STATUS_BG)
        style.configure("Status.TLabel", background=STATUS_BG, foreground=FG_COLOR)

        frame = ttk.Frame(root)
        frame.pack(fill="both", expand=True, padx=10, pady=8)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="ESP Flash Utility (ESPtool GUI)", font=FONT_BOLD, foreground=ACCENT).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10)
        )

        ttk.Label(frame, text="Serial Port:").grid(row=1, column=0, sticky="w")
        self.port = ttk.Combobox(frame, width=30)
        self.port.grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Refresh COM", command=self.refresh_ports).grid(row=1, column=2, sticky="w", padx=5)

        ttk.Label(frame, text="Make sure you know the exact COM port your intended chip is in!",
                  foreground=ERROR_COLOR, font=("JetBrains Mono", 9, "italic")).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(6, 10)
        )

        ttk.Label(frame, text="Chip Type:").grid(row=3, column=0, sticky="w")
        self.chip = ttk.Combobox(frame, values=[
            "esp32", "esp32s2", "esp32s3", "esp32c2", "esp32c3",
            "esp32c6", "esp32h2", "esp32p4", "esp8266"
        ], width=30)
        self.chip.set("esp32")
        self.chip.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Action:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.action = ttk.Combobox(frame, values=["Erase Flash", "Write Flash", "Get Chip Info"], width=30)
        self.action.current(0)
        self.action.grid(row=4, column=1, sticky="w", pady=(10, 0))

        ttk.Label(frame, text="Firmware:").grid(row=5, column=0, sticky="w", pady=(10, 0))
        self.file_lbl = ttk.Label(frame, text="No file selected")
        self.file_lbl.grid(row=5, column=1, sticky="w")
        ttk.Button(frame, text="Select .bin", command=self.select_file).grid(row=5, column=2, sticky="w", padx=5)

        ttk.Button(frame, text="Run Command", command=self.run).grid(row=6, column=0, sticky="w", pady=(14, 0))
        ttk.Label(frame, text="v1.0", font=("JetBrains Mono", 9)).grid(row=6, column=1, sticky="w", pady=(14, 0))

        ttk.Label(frame, text="Output:").grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.output = scrolledtext.ScrolledText(
            frame, font=("Consolas", 10), height=14,
            bg="#101010", fg=FG_COLOR, insertbackground=FG_COLOR, borderwidth=0
        )
        self.output.grid(row=8, column=0, columnspan=3, sticky="nsew")
        frame.rowconfigure(8, weight=1)

        repo = ttk.Label(frame, text="Repository", foreground=ACCENT, cursor="hand2", font=("JetBrains Mono", 9, "underline"))
        repo.grid(row=9, column=0, sticky="w", pady=(8, 0))
        repo.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))

        self.status = SlideStatusBar(root)
        root.update_idletasks()
        self.status.place_bottom()

        self.bin_path = None
        self.refresh_ports()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port["values"] = ports
        if ports:
            self.port.current(0)
            self.status.show(f"Detected {len(ports)} COM port(s).", spin=False)
        else:
            self.port.set("")
            self.status.show("No COM ports found.", spin=False)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if path:
            self.bin_path = path
            self.file_lbl.config(text=os.path.basename(path))
            self.status.show(f"Selected {os.path.basename(path)}", spin=False)

    def run(self):
        port = self.port.get().strip()
        if not port:
            self.status.show("Select a COM port.", spin=False)
            return

        chip = self.chip.get().strip()
        action = self.action.get()

        cmd = [sys.executable, "-m", "esptool", "--port", port]
        if action == "Erase Flash":
            cmd += ["--chip", chip, "erase_flash"]
        elif action == "Write Flash":
            if not self.bin_path or not os.path.isfile(self.bin_path):
                self.status.show("Select a valid .bin file.", spin=False)
                return
            cmd += ["--chip", chip, "write_flash", "-z", "0x1000", self.bin_path]
        else:
            cmd += ["--chip", chip, "chip_id"]

        self.output.delete("1.0", tk.END)
        self.status.show("Running command...", spin=True)

        threading.Thread(target=self._run_cmd, args=(cmd,), daemon=True).start()

    def _run_cmd(self, cmd):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self._append(line)
            proc.wait()
            code = proc.returncode
            msg = "Done." if code == 0 else f"Exited with code {code}"
            self.status.show(msg, spin=False)
        except Exception as e:
            self._append(str(e))
            self.status.show("Error running command.", spin=False)

    def _append(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)


def main():
    root = tk.Tk()
    app = ESPFlashUtility(root)

    def resize(event=None):
        app.status.place_bottom()
    root.bind("<Configure>", resize)

    root.mainloop()


if __name__ == "__main__":
    main()
