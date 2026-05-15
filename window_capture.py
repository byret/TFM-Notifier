import ctypes
import win32gui
import win32ui
from PIL import Image


def find_window():
    found_tfm = []
    found_flash = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)

            if title == "TFM Notifier":
                return

            clean_title = title.strip()

            if clean_title == "Transformice":
                found_tfm.append(hwnd)
            # Usually only the version at the end of the name differs
            elif clean_title.startswith("Adobe Flash Player"):
                found_flash.append(hwnd)

    win32gui.EnumWindows(callback, None)

    if found_tfm:
        return found_tfm[0]
    elif found_flash:
        return found_flash[0]

    return None


def screenshot_window(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)

    image = Image.frombuffer(
        "RGB",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr,
        "raw",
        "BGRX",
        0,
        1
    )

    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result != 1:
        return None

    return image