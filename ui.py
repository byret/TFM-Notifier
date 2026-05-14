import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from notifier import EventNotifier


class TransformiceNotifierApp:
    def __init__(self, root):
        self.clear_button = None
        self.log_box = None
        self.stop_button = None
        self.start_button = None
        self.status_label = None
        self.trading_map_checkbox = None

        self.root = root
        self.root.title("TFM Notifier")
        self.root.geometry("560x500")
        self.root.resizable(False, False)

        self.notify_trading_map_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready to monitor")

        self.notifier = EventNotifier(
            log_callback=self.log,
            status_callback=self.set_status
        )

        self.worker_thread = None

        self.build_ui()

        self.log("Application started")
        self.log("Click Start monitoring to begin")

    def build_ui(self):
        self.root.configure(bg="#F4F6F8")

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#F4F6F8")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")

        style.configure(
            "Title.TLabel",
            background="#F4F6F8",
            foreground="#1F2937",
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#F4F6F8",
            foreground="#6B7280",
            font=("Segoe UI", 9)
        )

        style.configure(
            "Status.TLabel",
            background="#FFFFFF",
            foreground="#1F2937",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Section.TLabel",
            background="#F4F6F8",
            foreground="#374151",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "CardText.TLabel",
            background="#FFFFFF",
            foreground="#374151",
            font=("Segoe UI", 9)
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=8
        )

        style.configure(
            "TCheckbutton",
            background="#FFFFFF",
            foreground="#374151",
            font=("Segoe UI", 9)
        )

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame,
            text="TFM Event Notifier",
            style="Title.TLabel"
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            main_frame,
            text="Monitors the Transformice window and alerts when an event starts.\n"
                 "Transformice can stay behind other windows, but the game window must not be minimized.\n",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(anchor="w", pady=(4, 16))

        settings_frame = ttk.Frame(main_frame, padding=14, style="Card.TFrame")
        settings_frame.pack(fill="x", pady=(0, 16))

        settings_label = ttk.Label(
            settings_frame,
            text="Notification options",
            style="CardText.TLabel",
            font=("Segoe UI", 10, "bold")
        )
        settings_label.pack(anchor="w", pady=(0, 8))

        self.trading_map_checkbox = ttk.Checkbutton(
            settings_frame,
            text="Notify about trading map",
            variable=self.notify_trading_map_var
        )
        self.trading_map_checkbox.pack(anchor="w")

        status_frame = ttk.Frame(main_frame, padding=14, style="Card.TFrame")
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=500
        )
        self.status_label.pack(anchor="w")

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(0, 16))

        self.start_button = ttk.Button(
            buttons_frame,
            text="Start monitoring",
            command=self.start_search
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.stop_button = ttk.Button(
            buttons_frame,
            text="Stop",
            command=self.stop_search
        )
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(6, 6))
        self.stop_button.config(state="disabled")

        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear logs",
            command=self.clear_logs
        )
        self.clear_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

        log_label = ttk.Label(
            main_frame,
            text="Logs",
            style="Section.TLabel"
        )
        log_label.pack(anchor="w", pady=(0, 6))

        self.log_box = ScrolledText(
            main_frame,
            height=12,
            state="disabled",
            wrap="word",
            bg="#111827",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            relief="flat",
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        self.log_box.pack(fill="both", expand=True)

        self.log_box.tag_config("normal", foreground="#E5E7EB")
        self.log_box.tag_config("error", foreground="#F87171")
        self.log_box.tag_config("success", foreground="#34D399")

    def log(self, message, level="normal"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        self.log_box.configure(state="normal")
        self.log_box.insert("end", line, level)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def set_status(self, message):
        self.status_var.set(message)

    def start_search(self):
        self.notifier.set_notify_trading_map(
            self.notify_trading_map_var.get()
        )

        self.worker_thread = threading.Thread(
            target=self.notifier.start,
            daemon=True
        )
        self.worker_thread.start()

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.trading_map_checkbox.config(state="disabled")

        self.set_status("Monitoring events...")
        self.log("Started event monitoring")

        if self.notify_trading_map_var.get():
            self.log("Trading map notifications enabled")
        else:
            self.log("Trading map notifications disabled")

    def stop_search(self):
        self.notifier.stop()

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.trading_map_checkbox.config(state="normal")

        self.set_status("Stopped")
        self.log("Stopping notifier...")