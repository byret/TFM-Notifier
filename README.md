# TFM Event Notifier

Detects Transformice event keywords directly from the game window using OCR and plays a sound notification when an event starts.

Currently supported ONLY lua events.

Features:

* OCR-based detection from the Transformice window
* Works while the game is in the background (window must stay open, not minimized)
* Sound alerts when an event is detected
* Cooldown after detection to avoid repeated notifications
* Portable build with bundled Tesseract OCR

Technologies:

* Python
* Tesseract OCR
* PyInstaller
* Win32 window capture
