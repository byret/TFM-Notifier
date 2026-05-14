import time
import winsound
import win32gui
import pytesseract
import os
import sys

from config import EVENT_KEYWORDS
from window_capture import find_window
from window_capture import screenshot_window

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
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

    def start(self):
        self.running = True
        self.loop()

    def stop(self):
        self.running = False

    def loop(self):
        while self.running:
            hwnd = find_window()

            if not hwnd:
                self.set_status("Transformice window not found")
                self.log("Transformice window not found", "error")
                time.sleep(5)
                continue

            if win32gui.IsIconic(hwnd):

                if self.last_state != "minimized":
                    self.set_status("Window is minimized")
                    self.log("Window is minimized - OCR cannot read it", "error")
                    self.last_state = "minimized"

                time.sleep(1)
                continue

            self.last_state = None
            image = screenshot_window(hwnd)

            if image is None:
                self.set_status("Could not capture window")
                self.log("Could not capture window", "error")
                time.sleep(2)
                continue

            text = pytesseract.image_to_string(image, lang="eng")
            normalized_text = text.lower().strip()
            found_keyword = None

            for keyword in EVENT_KEYWORDS:
                normalized_keyword = keyword.lower().strip()

                if normalized_keyword in normalized_text:
                    found_keyword = keyword
                    break

            if found_keyword:
                self.set_status(f"EVENT STARTED")
                self.log(f"EVENT STARTED", "success")

                winsound.Beep(1000, 700)
                winsound.Beep(1300, 700)
                winsound.Beep(1000, 700)

                self.set_status("Found event. Waiting 10 minutes...")
                time.sleep(600)
            else:
                self.set_status("Waiting...")

            time.sleep(1)

        self.log("Waiting loop stopped")