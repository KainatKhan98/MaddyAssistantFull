# ==========================================
# MADDY V2 - COMPUTER ACTIONS
# ==========================================

import subprocess
import webbrowser
import os
import datetime
import pyautogui
import pyperclip
import psutil
import time

from voice import speak


# ==========================================
# APPLICATIONS
# ==========================================

def open_chrome():

    chrome_paths = [

        r"C:\Program Files\Google\Chrome\Application\chrome.exe",

        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",

        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        )
    ]

    for path in chrome_paths:

        if os.path.exists(path):

            speak("Opening Chrome.")

            subprocess.Popen(path)

            return

    speak("I couldn't find Chrome.")


def open_vscode():

    speak("Opening Visual Studio Code.")

    subprocess.Popen(
        "code",
        shell=True
    )


def open_notepad():

    speak("Opening Notepad.")

    subprocess.Popen(
        "notepad.exe"
    )


def open_calculator():

    speak("Opening Calculator.")

    subprocess.Popen(
        "calc.exe"
    )


# ==========================================
# WEBSITES
# ==========================================

def open_google():

    speak("Opening Google.")

    webbrowser.open(
        "https://www.google.com"
    )


def open_youtube():

    speak("Opening YouTube.")

    webbrowser.open(
        "https://www.youtube.com"
    )


# ==========================================
# GOOGLE SEARCH
# ==========================================

def google_search(query):

    speak(
        f"Searching Google for {query}."
    )

    url = (
        "https://www.google.com/search?q="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)


# ==========================================
# YOUTUBE SEARCH
# ==========================================

def youtube_search(query):

    speak(
        f"Searching YouTube for {query}."
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)


# ==========================================
# FOLDERS
# ==========================================

def open_downloads():

    downloads = os.path.join(
        os.path.expanduser("~"),
        "Downloads"
    )

    speak("Opening Downloads.")

    os.startfile(downloads)


def open_documents():

    documents = os.path.join(
        os.path.expanduser("~"),
        "Documents"
    )

    speak("Opening Documents.")

    os.startfile(documents)


def open_desktop():

    desktop = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    speak("Opening Desktop.")

    os.startfile(desktop)


# ==========================================
# TIME
# ==========================================

def tell_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The time is {current_time}."
    )


# ==========================================
# DATE
# ==========================================

def tell_date():

    current_date = datetime.datetime.now().strftime(
        "%B %d, %Y"
    )

    speak(
        f"Today's date is {current_date}."
    )


# ==========================================
# SCREENSHOT
# ==========================================

def take_screenshot():

    speak("Taking a screenshot.")

    screenshot = pyautogui.screenshot()

    filename = datetime.datetime.now().strftime(
        "screenshot_%Y%m%d_%H%M%S.png"
    )

    path = os.path.join(
        os.path.expanduser("~"),
        "Pictures",
        filename
    )

    screenshot.save(path)

    speak("Screenshot saved.")

    print(f"Screenshot: {path}")


# ==========================================
# TYPE TEXT
# ==========================================

def type_text(text):

    speak("Typing.")

    pyperclip.copy(text)

    pyautogui.hotkey(
        "ctrl",
        "v"
    )


# ==========================================
# VOLUME
# ==========================================

def increase_volume():

    speak("Increasing volume.")

    for _ in range(5):

        pyautogui.press(
            "volumeup"
        )


def decrease_volume():

    speak("Decreasing volume.")

    for _ in range(5):

        pyautogui.press(
            "volumedown"
        )


def mute_volume():

    speak("Muting volume.")

    pyautogui.press(
        "volumemute"
    )


# ==========================================
# WINDOWS
# ==========================================

def minimize_window():

    speak("Minimizing window.")

    pyautogui.hotkey(
        "win",
        "down"
    )


def maximize_window():

    speak("Maximizing window.")

    pyautogui.hotkey(
        "win",
        "up"
    )


# ==========================================
# CLOSE APPLICATION
# ==========================================

def close_chrome():

    speak("Closing Chrome.")

    for process in psutil.process_iter(
        ["name"]
    ):

        try:

            if process.info["name"]:

                if process.info["name"].lower() == "chrome.exe":

                    process.terminate()

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):

            pass


# ==========================================
# COMPUTER LOCK
# ==========================================

def lock_computer():

    speak("Locking your computer.")

    subprocess.run(
        "rundll32.exe user32.dll,LockWorkStation",
        shell=True
    )


# ==========================================
# RESTART
# ==========================================

def restart_computer():

    speak(
        "Restarting your computer in ten seconds."
    )

    subprocess.Popen(
        "shutdown /r /t 10",
        shell=True
    )


# ==========================================
# CANCEL SHUTDOWN
# ==========================================

def cancel_shutdown():

    speak("Cancelling shutdown.")

    subprocess.Popen(
        "shutdown /a",
        shell=True
    )