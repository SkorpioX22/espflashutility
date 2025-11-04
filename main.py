import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import serial.tools.list_ports
import threading
import sys
import os
import webbrowser

class ESPFlashUtility:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP Flash Utility (ESPtool GUI)")
        self.root.geometry("700x540")
        self.root.configure(bg="white")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="white", foreground="black", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")

        # Title
        ttk.Label(root, text="ESP Flash Utility (ESPtool GUI)", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Port selection
        frame_top = ttk.Frame(root)
        frame_top.pack(pady=5)
        ttk.Label(frame_top, text="Serial Port:").grid(row=0, column=0, padx=5, pady=5)
        self.port_combo = ttk.Combobox(frame_top, width=25)
        self.refresh_ports()
        self.port_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_top, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)

        # Disclaimer below COM port selection
        ttk.Label(
            frame_top,
            text="⚠ Make sure you know the exact COM port your intended chip is in!",
            foreground="red",
            background="white",
            font=("Segoe UI", 9, "italic")
        ).grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky="w")

        # Action selection
        frame_action = ttk.Frame(root)
        frame_action.pack(pady=5)
        ttk.Label(frame_action, text="Action:").grid(row=0, column=0, padx=5, pady=5)
        self.action_combo = ttk.Combobox(frame_action, values=["Erase Flash", "Write Flash", "Get Chip Info"], width=25)
        self.action_combo.current(0)
        self.action_combo.grid(row=0, column=1, padx=5, pady=5)

        # File selection (for Write Flash)
        self.file_label = ttk.Label(root, text="Firmware File: None selected")
        self.file_label.pack(pady=5)
        ttk.Button(root, text="Select .bin File", command=self.select_file).pack(pady=5)

        # Run button
        ttk.Button(root, text="Run Command", command=self.run_command).pack(pady=10)

        # Output window
        ttk.Label(root, text="Output:").pack(pady=5)
        self.output_box = scrolledtext.ScrolledText(
            root,
            bg="#f9f9f9",
            fg="black",
            insertbackground="black",
            font=("Consolas", 10),
            height=15,
        )
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Repository link at the bottom
        self.repo_label = tk.Label(
            root,
            text="Created by SkorpioX22 — Go to Repository",
            fg="blue",
            bg="white",
            cursor="hand2",
            font=("Segoe UI", 10, "underline")
        )
        self.repo_label.pack(pady=5)
        self.repo_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/SkorpioX22/espflashutility"))

        self.bin_path = None

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if path:
            self.bin_path = path
            self.file_label.config(text=f"Firmware File: {os.path.basename(path)}")

    def run_command(self):
        port = self.port_combo.get()
        if not port:
            messagebox.showwarning("Warning", "Please select a port.")
            return

        action = self.action_combo.get()
        cmd = [sys.executable, "-m", "esptool", "--port", port]

        if action == "Erase Flash":
            cmd += ["erase_flash"]
        elif action == "Write Flash":
            if not self.bin_path:
                messagebox.showwarning("Warning", "Please select a .bin file first.")
                return
            cmd += ["--chip", "esp32", "write_flash", "-z", "0x1000", self.bin_path]
        elif action == "Get Chip Info":
            cmd += ["chip_id"]

        self.output_box.delete(1.0, tk.END)
        threading.Thread(target=self.run_subprocess, args=(cmd,), daemon=True).start()

    def run_subprocess(self, cmd):
        self.write_output(f"Running: {' '.join(cmd)}\n\n")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.write_output(line)
            process.wait()
            self.write_output(f"\n\n[Process exited with code {process.returncode}]\n")
        except Exception as e:
            self.write_output(f"\nError: {e}\n")

    def write_output(self, text):
        self.output_box.insert(tk.END, text)
        self.output_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ESPFlashUtility(root)
    root.mainloop()
