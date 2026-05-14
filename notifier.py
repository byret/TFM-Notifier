import time
import winsound
import win32gui
import pytesseract
import os
import sys

from config import EVENT_KEYWORDS, TRADING_MAP_KEYWORD
from window_capture import find_window
from window_capture import screenshot_window


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


pytesseract.pytesseract.tesseract_cmd = resource_path(
    r"tesseract\tesseract.exe"
)


class EventNotifier:
    def __init__(self, log_callback, status_callback):
        self.running = False
        self.keyword = None
        self.log = log_callback
        self.set_status = status_callback
        self.last_state = None
        self.notify_trading_map = False

    def start(self):
        self.running = True
        self.loop()

    def stop(self):
        self.running = False

    def set_notify_trading_map(self, value):
        self.notify_trading_map = value

    def loop(self):
        while self.running:
            hwnd = find_window()

            if not hwnd:
                self.set_status("Transformice window not found")

                if self.last_state != "window_not_found":
                    self.log("Transformice window not found", "error")
                    self.last_state = "window_not_found"

                time.sleep(5)
                continue

            if self.last_state == "window_not_found":
                self.log("Transformice window found", "success")

            if win32gui.IsIconic(hwnd):
                self.set_status("Transformice is minimized")

                if self.last_state != "minimized":
                    self.log("Window is minimized - scanning paused", "error")
                    self.last_state = "minimized"

                time.sleep(1)
                continue

            if self.last_state in ("window_not_found", "minimized"):
                self.log("Scanning resumed", "success")

            self.last_state = None

            image = screenshot_window(hwnd)

            if image is None:
                self.set_status("Capture failed")
                self.log("Could not capture Transformice window", "error")
                time.sleep(2)
                continue

            text = pytesseract.image_to_string(image, lang="eng")
            normalized_text = text.lower().strip()
            found_keyword = None

            keywords_to_check = list(EVENT_KEYWORDS)

            if self.notify_trading_map:
                keywords_to_check.append(TRADING_MAP_KEYWORD)

            for keyword in keywords_to_check:
                normalized_keyword = keyword.lower().strip()

                if normalized_keyword in normalized_text:
                    found_keyword = keyword
                    break

            if found_keyword:
                self.set_status("EVENT STARTED")
                self.log(f"EVENT STARTED", "success")

                winsound.Beep(1000, 700)
                winsound.Beep(1300, 700)
                winsound.Beep(1000, 700)

                self.set_status("Cooldown: 10 minutes")
                self.log("Scanning paused for 10 minutes")

                time.sleep(600)
            else:
                self.set_status("Scanning...")

            time.sleep(1)

        self.log("Scanning stopped")