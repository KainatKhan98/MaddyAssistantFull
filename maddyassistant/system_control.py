# ==========================================
# MADDY V3.3 - SYSTEM CONTROL
# ==========================================

import os
import time
import subprocess
import pyautogui

from voice import speak


# ==========================================
# VOLUME CONTROL
# ==========================================

def increase_volume():

    pyautogui.press("volumeup")

    speak("Volume increased.")

    print("System: Volume increased.")


def decrease_volume():

    pyautogui.press("volumedown")

    speak("Volume decreased.")

    print("System: Volume decreased.")


def mute_volume():

    pyautogui.press("volumemute")

    speak("Volume muted.")

    print("System: Volume muted.")


# ==========================================
# WINDOW CONTROL
# ==========================================

def minimize_window():

    pyautogui.hotkey("win", "down")

    speak("Window minimized.")

    print("System: Window minimized.")


def maximize_window():

    pyautogui.hotkey("win", "up")

    speak("Window maximized.")

    print("System: Window maximized.")


# ==========================================
# LOCK COMPUTER
# ==========================================

def lock_computer():

    speak("Locking your computer.")

    print("System: Locking computer.")

    os.system("rundll32.exe user32.dll,LockWorkStation")


# ==========================================
# RESTART COMPUTER
# ==========================================

def restart_computer(delay=10):

    speak(
        f"Your computer will restart in {delay} seconds."
    )

    print(
        f"System: Restarting in {delay} seconds."
    )

    os.system(
        f"shutdown /r /t {delay}"
    )


# ==========================================
# SHUTDOWN COMPUTER
# ==========================================

def shutdown_computer(delay=10):

    speak(
        f"Your computer will shut down in {delay} seconds."
    )

    print(
        f"System: Shutting down in {delay} seconds."
    )

    os.system(
        f"shutdown /s /t {delay}"
    )


# ==========================================
# CANCEL SHUTDOWN / RESTART
# ==========================================

def cancel_shutdown():

    os.system("shutdown /a")

    speak("The scheduled shutdown has been cancelled.")

    print(
        "System: Shutdown or restart cancelled."
    )


# ==========================================
# SCREENSHOT
# ==========================================

def take_screenshot():

    try:

        speak("Taking a screenshot.")

        screenshot = pyautogui.screenshot()

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"screenshot_{timestamp}.png"
        )

        path = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            filename
        )

        screenshot.save(path)

        speak("Screenshot saved.")

        print(
            f"Screenshot saved to: {path}"
        )

        return True

    except Exception as e:

        print(
            f"Screenshot error: {e}"
        )

        speak(
            "I couldn't take the screenshot."
        )

        return False