# ==========================================
# MADDY V3.6.2 - DYNAMIC APP DISCOVERY
# ==========================================

import os
import subprocess
import psutil
import win32gui
import win32process
import win32con

from difflib import get_close_matches
from voice import speak


# ==========================================
# KNOWN APPLICATIONS
# ==========================================

APPS = {

    "chrome": {
        "process": "chrome.exe",
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    },

    "vscode": {
        "process": "Code.exe",
        "paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        ]
    },

    "notepad": {
        "process": "notepad.exe",
        "paths": [
            r"C:\Windows\System32\notepad.exe"
        ]
    },

    "calculator": {
        "process": "CalculatorApp.exe",
        "paths": [
            r"C:\Windows\System32\calc.exe"
        ]
    },
    "device manager": {
    "process": "mmc.exe",
    "paths": [
        r"C:\Windows\System32\devmgmt.msc"
    ]
},
}


# ==========================================
# DYNAMIC APP DISCOVERY
# ==========================================

def discover_apps():

    discovered_apps = {}

    # ==========================================
    # 1. DISCOVER NORMAL START MENU .LNK APPS
    # ==========================================

    start_menu_paths = [

        os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"
        ),

        os.path.expandvars(
            r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"
        )

    ]

    for start_menu in start_menu_paths:

        if not os.path.exists(start_menu):
            continue

        for root, dirs, files in os.walk(start_menu):

            for file in files:

                if not file.lower().endswith(".lnk"):
                    continue

                app_name = os.path.splitext(file)[0].strip()

                if not app_name:
                    continue

                key = app_name.lower()

                if key not in discovered_apps:

                    shortcut_path = os.path.join(
                        root,
                        file
                    )

                    discovered_apps[key] = shortcut_path

    # ==========================================
    # 2. DISCOVER WINDOWS STORE / MSIX APPS
    # ==========================================

    try:

        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Get-StartApps | Select-Object Name, AppID | ConvertTo-Json -Compress"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.stdout.strip():

            import json

            start_apps = json.loads(result.stdout)

            # If only one app is returned, PowerShell gives a dictionary
            if isinstance(start_apps, dict):
                start_apps = [start_apps]

            for app in start_apps:

                app_name = app.get("Name")
                app_id = app.get("AppID")

                if not app_name or not app_id:
                    continue

                key = app_name.lower().strip()

                if key not in discovered_apps:

                    discovered_apps[key] = (
                        "STARTAPP:" + app_id
                    )

    except Exception as e:

        print(f"Start Apps discovery error: {e}")

    return discovered_apps

# ==========================================
# FIND APPLICATION
# ==========================================

def find_app(app_name):

    app_name = app_name.lower().strip()

    # --------------------------------------
    # 1. Known applications
    # --------------------------------------

    if app_name in APPS:
        return APPS[app_name]

    # --------------------------------------
    # 2. Discover Windows applications
    # --------------------------------------

    discovered_apps = discover_apps()

    # --------------------------------------
    # 3. Exact match
    # --------------------------------------

    if app_name in discovered_apps:

        return discovered_apps[app_name]

    # --------------------------------------
    # 4. Partial match
    # --------------------------------------

    for name, path in discovered_apps.items():

        if app_name in name or name in app_name:

            return path

    # --------------------------------------
    # 5. Fuzzy / typo matching
    # --------------------------------------

    matches = get_close_matches(
        app_name,
        discovered_apps.keys(),
        n=1,
        cutoff=0.65
    )

    if matches:

        matched_name = matches[0]

        print(
            f"Fuzzy match: '{app_name}' -> '{matched_name}'"
        )

        return discovered_apps[matched_name]

    return None
# ==========================================
# FIND_START_APP APPLICATION
# ==========================================
def find_start_app(app_name):
    """
    Find a Windows Start Menu / Store / MSIX app.
    Returns (display_name, app_id) or None.
    """

    try:
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                f"Get-StartApps | Where-Object {{ $_.Name -like '*{app_name}*' }} | Select-Object -First 1 Name, AppID"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        lines = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        # Skip PowerShell table headers/separators
        data_lines = [
            line for line in lines
            if not line.startswith("Name")
            and not line.startswith("----")
        ]

        if not data_lines:
            return None

        parts = data_lines[0].split()

        if len(parts) >= 2:

            display_name = parts[0]
            app_id = parts[-1]

            return display_name, app_id

    except Exception as e:
        print(f"Start app discovery error: {e}")

    return None
# ==========================================
# OPEN APPLICATION
# ==========================================

def open_app(app_name):

    app_name = app_name.lower().strip()

    # ==========================================
    # WHATSAPP FALLBACK
    # ==========================================

    if app_name == "whatsapp":

        try:

            os.startfile("whatsapp:")

            speak("Opening WhatsApp.")
            print("Opened: WhatsApp")

            return True

        except Exception as e:

            print(f"WhatsApp URI launch failed: {e}")


    # ==========================================
    # FIND APP
    # ==========================================

    app_path = find_app(app_name)

    if not app_path:

        speak(
            f"I couldn't find {app_name} on your computer."
        )

        print(f"App not found: {app_name}")

        return False


    # ==========================================
    # KNOWN APP DICTIONARY
    # ==========================================

    if isinstance(app_path, dict):

        paths = app_path.get("paths", [])

        for path in paths:

            path = os.path.expandvars(path)

            if os.path.exists(path):

                try:

                    if path.lower().endswith(".msc"):

                        os.startfile(path)

                    else:

                        subprocess.Popen(
                            path,
                            shell=False
                        )

                    speak(f"Opening {app_name}.")
                    print(f"Opened: {app_name}")

                    return True

                except Exception as e:

                    print(f"Known app launch error: {e}")


    # ==========================================
    # WINDOWS STORE / MSIX APP
    # ==========================================

    if isinstance(app_path, str) and app_path.startswith("STARTAPP:"):

        app_id = app_path.replace(
            "STARTAPP:",
            "",
            1
        )

        try:

            subprocess.Popen([
                "explorer.exe",
                f"shell:AppsFolder\\{app_id}"
            ])

            speak(f"Opening {app_name}.")
            print(f"Opened Store app: {app_name}")
            print(f"AppID: {app_id}")

            return True

        except Exception as e:

            print(f"Store app launch error: {e}")

            speak(
                f"I couldn't open {app_name}."
            )

            return False


    # ==========================================
    # NORMAL .EXE / .LNK APP
    # ==========================================

    try:

        if isinstance(app_path, str) and app_path.lower().endswith(".lnk"):

            os.startfile(app_path)

        else:

            subprocess.Popen(
                app_path,
                shell=False
            )

        speak(f"Opening {app_name}.")
        print(f"Opened: {app_name}")

        return True

    except Exception as e:

        print(f"Open app error: {e}")

        speak(
            f"I couldn't open {app_name}."
        )

        return False

# ==========================================
# CHECK IF APP IS RUNNING
# ==========================================

def is_app_running(app_name):

    app_name = app_name.lower().strip()

    # Find the application
    app_path = find_app(app_name)

    if not app_path:
        print(f"App not found: {app_name}")
        return False

    # --------------------------------------
    # Known application
    # --------------------------------------
    if app_name in APPS:

        process_name = APPS[app_name]["process"]

        for process in psutil.process_iter(["name"]):

            try:
                current_name = process.info["name"]

                if current_name:
                    if current_name.lower() == process_name.lower():
                        return True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

        return False

    # --------------------------------------
    # Dynamic application
    # --------------------------------------
    discovered_apps = discover_apps()

    matched_name = None

    # Exact match
    if app_name in discovered_apps:
        matched_name = app_name

    # Partial match
    if not matched_name:

        for name in discovered_apps:

            if app_name in name or name in app_name:
                matched_name = name
                break

    # Fuzzy match
    if not matched_name:

        matches = get_close_matches(
            app_name,
            discovered_apps.keys(),
            n=1,
            cutoff=0.65
        )

        if matches:
            matched_name = matches[0]

    if not matched_name:
        return False

    # --------------------------------------
    # Compare with running processes
    # --------------------------------------
    for process in psutil.process_iter(["name"]):

        try:

            process_name = process.info["name"]

            if not process_name:
                continue

            process_base = os.path.splitext(
                process_name
            )[0].lower()

            if (
                matched_name in process_base
                or process_base in matched_name
            ):

                print(
                    f"Process match: "
                    f"{matched_name} -> {process_name}"
                )

                return True

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            continue

    return False
# ==========================================
# GET RUNNING DISCOVERED APPS
# ==========================================
def get_running_apps():

    discovered_apps = discover_apps()
    running_apps = []

    for process in psutil.process_iter(["name"]):

        try:

            process_name = process.info["name"]

            if not process_name:
                continue

            process_base = os.path.splitext(
                process_name
            )[0].lower()

            for app_name in discovered_apps:

                if (
                    app_name in process_base
                    or process_base in app_name
                ):

                    if app_name not in running_apps:

                        running_apps.append(app_name)

                    break

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):
            continue

    return running_apps


# ==========================================
# SWITCH TO RUNNING APPLICATION
# ==========================================
def switch_to_app(app_name):

    app_name = app_name.lower().strip()

    # ======================================
    # APP ALIASES
    # ======================================

    aliases = {
        "vs code": "visual studio code",
        "vscode": "visual studio code",
        "chrome": "google chrome",
        "google chrome": "google chrome",
        "win rar": "winrar",
        "winrar": "winrar",
        "whatsapp": "whatsapp"
    }

    search_name = aliases.get(app_name, app_name)

    # ======================================
    # WINDOWS API
    # ======================================

    try:

        import win32gui
        import win32process

    except ImportError:

        speak(
            "I need one additional Windows library "
            "to switch application windows."
        )

        return False

    # ======================================
    # FIND KNOWN/DISCOVERED APPLICATION
    # ======================================

    app_path = find_app(search_name)

    # ======================================
    # FIND POSSIBLE PROCESS IDS
    # ======================================

    possible_pids = []

    # --------------------------------------
    # Known application
    # --------------------------------------

    if search_name in APPS:

        process_name = APPS[search_name]["process"].lower()

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                current_name = process.info["name"]

                if (
                    current_name
                    and current_name.lower() == process_name
                ):

                    possible_pids.append(
                        process.info["pid"]
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

    # --------------------------------------
    # Dynamic application
    # --------------------------------------

    elif app_path:

        discovered_apps = discover_apps()

        matched_name = None

        if search_name in discovered_apps:

            matched_name = search_name

        else:

            for name in discovered_apps:

                if (
                    search_name in name
                    or name in search_name
                ):

                    matched_name = name
                    break

        if matched_name:

            normalized_app = (
                matched_name
                .replace(" ", "")
                .replace("-", "")
                .replace("_", "")
                .lower()
            )

            for process in psutil.process_iter(
                ["pid", "name"]
            ):

                try:

                    process_name = process.info["name"]

                    if not process_name:
                        continue

                    process_base = os.path.splitext(
                        process_name
                    )[0].lower()

                    normalized_process = (
                        process_base
                        .replace(" ", "")
                        .replace("-", "")
                        .replace("_", "")
                    )

                    if (
                        normalized_app in normalized_process
                        or normalized_process in normalized_app
                    ):

                        possible_pids.append(
                            process.info["pid"]
                        )

                        print(
                            f"Process found: "
                            f"{matched_name} -> "
                            f"{process_name} "
                            f"(PID {process.info['pid']})"
                        )

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied
                ):
                    continue

    # --------------------------------------
    # FALLBACK:
    # SEARCH RUNNING PROCESSES DIRECTLY
    # --------------------------------------

    if not possible_pids:

        normalized_search = (
            search_name
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .lower()
        )

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                process_name = process.info["name"]

                if not process_name:
                    continue

                process_base = os.path.splitext(
                    process_name
                )[0].lower()

                normalized_process = (
                    process_base
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                if (
                    normalized_search in normalized_process
                    or normalized_process in normalized_search
                ):

                    possible_pids.append(
                        process.info["pid"]
                    )

                    print(
                        f"Running process found: "
                        f"{process_name} "
                        f"(PID {process.info['pid']})"
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

    # ======================================
    # NO PROCESS FOUND
    # ======================================

    if not possible_pids:

        speak(
            f"I couldn't find {app_name} running."
        )

        print(
            f"Running process not found: {app_name}"
        )

        return False

    # ======================================
    # FIND VISIBLE WINDOW
    # ======================================

    target_hwnd = None
    target_pid = None

    def find_window(hwnd, extra):

        nonlocal target_hwnd
        nonlocal target_pid

        try:

            if not win32gui.IsWindowVisible(hwnd):
                return True

            _, window_pid = (
                win32process.GetWindowThreadProcessId(hwnd)
            )

            if window_pid not in possible_pids:
                return True

            title = win32gui.GetWindowText(hwnd)

            if title:

                target_hwnd = hwnd
                target_pid = window_pid

                return False

        except Exception:

            pass

        return True

    try:

        win32gui.EnumWindows(
            find_window,
            None
        )

    except Exception as e:

        print(
            f"EnumWindows warning: {e}"
        )

    # ======================================
    # SECOND ATTEMPT
    # ======================================

    if not target_hwnd:

        try:

            win32gui.EnumWindows(
                find_window,
                None
            )

        except Exception as e:

            print(
                f"Second EnumWindows attempt failed: {e}"
            )

  
    # ======================================
    # WINDOW TITLE FALLBACK
    # ======================================

    if not target_hwnd:

        try:

            # Try exact window title
            target_hwnd = win32gui.FindWindow(
                None,
                "WhatsApp"
            )

            if target_hwnd:

                target_pid = (
                    win32process.GetWindowThreadProcessId(
                        target_hwnd
                    )[1]
                )

                print(
                    f"Window found by title: WhatsApp "
                    f"(PID {target_pid})"
                )

        except Exception as e:

            print(
                f"Window title search failed: {e}"
            )


    # ======================================
    # WINDOW STILL NOT FOUND
    # ======================================

    if not target_hwnd:

        speak(
            f"I found {app_name} running, "
            f"but couldn't find its window."
        )

        print(
            f"Could not locate window for {app_name}."
        )

        return False
    #=====================
    # BRING WINDOW TO FRONT
    # ======================================

    try:

        if win32gui.IsIconic(target_hwnd):

            win32gui.ShowWindow(
                target_hwnd,
                9
            )

        win32gui.SetForegroundWindow(
            target_hwnd
        )

        title = win32gui.GetWindowText(
            target_hwnd
        )

        speak(
            f"Switching to {app_name}."
        )

        print(
            f"Process PID: {target_pid}"
        )

        print(
            f"Switched to: {title}"
        )

        return True

    except Exception as e:

        print(
            f"Window activation error: {e}"
        )

        speak(
            f"I couldn't switch to {app_name}."
        )

        return False

# ==========================================
# MINIMIZE RUNNING APPLICATION
# ==========================================
def minimize_app(app_name):

    app_name = app_name.lower().strip()

    aliases = {
        "vs code": "visual studio code",
        "vscode": "visual studio code",
        "chrome": "google chrome",
        "google chrome": "google chrome",
        "win rar": "winrar",
        "winrar": "winrar",
        "whatsapp": "whatsapp"
    }

    search_name = aliases.get(app_name, app_name)

    try:
        import win32gui
        import win32process
    except ImportError:
        speak("I need the Windows window control library.")
        return False

    app_path = find_app(search_name)

    possible_pids = []

    # ======================================
    # KNOWN APPLICATION
    # ======================================

    if search_name in APPS:

        process_name = APPS[search_name]["process"].lower()

        for process in psutil.process_iter(["pid", "name"]):

            try:

                current_name = process.info["name"]

                if (
                    current_name
                    and current_name.lower() == process_name
                ):

                    possible_pids.append(
                        process.info["pid"]
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

    # ======================================
    # DISCOVERED / RUNNING APPLICATION
    # ======================================

    else:

        discovered_apps = discover_apps()

        matched_name = None

        if search_name in discovered_apps:

            matched_name = search_name

        else:

            for name in discovered_apps:

                if (
                    search_name in name
                    or name in search_name
                ):

                    matched_name = name
                    break

        normalized_search = (
            search_name
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .lower()
        )

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                process_name = process.info["name"]

                if not process_name:
                    continue

                process_base = os.path.splitext(
                    process_name
                )[0].lower()

                normalized_process = (
                    process_base
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                if (
                    normalized_search in normalized_process
                    or normalized_process in normalized_search
                ):

                    possible_pids.append(
                        process.info["pid"]
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

    # ======================================
    # NO PROCESS
    # ======================================

    if not possible_pids:

        speak(
            f"I couldn't find {app_name} running."
        )

        print(
            f"Running process not found: {app_name}"
        )

        return False

    # ======================================
    # FIND WINDOW
    # ======================================

    target_hwnd = None
    target_pid = None

    def find_window(hwnd, extra):

        nonlocal target_hwnd
        nonlocal target_pid

        try:

            if not win32gui.IsWindowVisible(hwnd):
                return True

            _, window_pid = (
                win32process.GetWindowThreadProcessId(hwnd)
            )

            if window_pid not in possible_pids:
                return True

            title = win32gui.GetWindowText(hwnd)

            if title:

                target_hwnd = hwnd
                target_pid = window_pid

                return False

        except Exception:
            pass

        return True

    try:

        win32gui.EnumWindows(
            find_window,
            None
        )

    except Exception as e:

        print(
            f"EnumWindows warning: {e}"
        )

    # ======================================
    # SECOND ATTEMPT
    # ======================================

    if not target_hwnd:

        try:

            win32gui.EnumWindows(
                find_window,
                None
            )

        except Exception:
            pass

    # ======================================
    # WINDOW TITLE FALLBACK
    # ======================================

    if not target_hwnd:

        try:

            # Try exact window title
            target_hwnd = win32gui.FindWindow(
                None,
                "WhatsApp"
            )

            if target_hwnd:

                target_pid = (
                    win32process.GetWindowThreadProcessId(
                        target_hwnd
                    )[1]
                )

                print(
                    f"Window found by title: WhatsApp "
                    f"(PID {target_pid})"
                )

        except Exception as e:

            print(
                f"Window title search failed: {e}"
            )


    # ======================================
    # WINDOW STILL NOT FOUND
    # ======================================

    if not target_hwnd:

        speak(
            f"I found {app_name} running, "
            f"but couldn't find its window."
        )

        print(
            f"Could not locate window for {app_name}."
        )

        return False

    # ======================================
    # MINIMIZE WINDOW
    # ======================================

    try:

        win32gui.ShowWindow(
            target_hwnd,
            6
        )

        title = win32gui.GetWindowText(
            target_hwnd
        )

        speak(
            f"Minimizing {app_name}."
        )

        print(
            f"Minimized: {title}"
        )

        return True

    except Exception as e:

        print(
            f"Minimize error: {e}"
        )

        speak(
            f"I couldn't minimize {app_name}."
        )

        return False
def restore_app(app_name):

    app_info = find_app(app_name)

    if not app_info:
        speak(f"I couldn't find {app_name}.")
        return False

    process_name = app_info.get("process")

    target_hwnd = None
    target_pid = None

    # ======================================
    # FIND RUNNING PROCESS
    # ======================================

    try:

        for proc in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                if (
                    proc.info["name"]
                    and proc.info["name"].lower()
                    == process_name.lower()
                ):

                    target_pid = proc.info["pid"]

                    print(
                        f"Process found: {process_name} "
                        f"(PID {target_pid})"
                    )

                    break

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):
                continue

    except Exception as e:

        print(f"Process search error: {e}")


    # ======================================
    # FIND WINDOW
    # ======================================

    if target_pid:

        def enum_window_callback(hwnd, _):

            nonlocal target_hwnd

            try:

                if not win32gui.IsWindowVisible(hwnd):
                    return

                _, pid = win32process.GetWindowThreadProcessId(hwnd)

                if pid == target_pid:

                    title = win32gui.GetWindowText(hwnd)

                    if title:

                        target_hwnd = hwnd

            except Exception:
                pass


        try:
            win32gui.EnumWindows(
                enum_window_callback,
                None
            )

        except Exception as e:

            print(
                f"EnumWindows warning: {e}"
            )


    # ======================================
    # RESTORE WINDOW
    # ======================================

    if target_hwnd:

        try:

            win32gui.ShowWindow(
                target_hwnd,
                win32con.SW_RESTORE
            )

            win32gui.SetForegroundWindow(
                target_hwnd
            )

            speak(
                f"Restoring {app_name}."
            )

            print(
                f"Restored: "
                f"{win32gui.GetWindowText(target_hwnd)}"
            )

            return True

        except Exception as e:

            print(
                f"Restore error: {e}"
            )

            speak(
                f"I couldn't restore {app_name}."
            )

            return False


    # ======================================
    # WINDOW TITLE FALLBACK
    # ======================================

    title_map = {
        "whatsapp": "WhatsApp"
    }

    title = title_map.get(
        app_name.lower().strip()
    )

    if title:

        try:

            target_hwnd = win32gui.FindWindow(
                None,
                title
            )

            if target_hwnd:

                win32gui.ShowWindow(
                    target_hwnd,
                    win32con.SW_RESTORE
                )

                win32gui.SetForegroundWindow(
                    target_hwnd
                )

                speak(
                    f"Restoring {app_name}."
                )

                print(
                    f"Restored by title: {title}"
                )

                return True

        except Exception as e:

            print(
                f"Window title restore failed: {e}"
            )


    speak(
        f"I found {app_name} running, "
        f"but couldn't find its window."
    )

    print(
        f"Could not locate window for {app_name}."
    )

    return False


# ==========================================
# MAXIMIZE RUNNING APPLICATION
# ==========================================

def maximize_app(app_name):
    aliases = {
        "vs code": "vscode",
        "vscode": "vscode",
        "chrome": "chrome",
        "google chrome": "chrome",
        "win rar": "winrar",
        "winrar": "winrar",
        "whatsapp": "whatsapp"
    }

    search_name = aliases.get(
        app_name.lower().strip(),
        app_name.lower().strip()
    )

    try:
        # Find running process
        matching_pids = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                process_name = proc.info["name"]

                if not process_name:
                    continue

                normalized_process = (
                    process_name.lower()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                normalized_search = (
                    search_name.lower()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                if normalized_search in normalized_process:
                    matching_pids.append(proc.info["pid"])

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not matching_pids:
            speak(f"{app_name} is not running.")
            print(f"{app_name} is not running.")
            return False

        print(f"Running PIDs found: {matching_pids}")

        target_hwnd = None
        target_pid = None

        def callback(hwnd, extra):
            nonlocal target_hwnd, target_pid

            if not win32gui.IsWindowVisible(hwnd):
                return True

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            if pid in matching_pids:
                title = win32gui.GetWindowText(hwnd)

                if title.strip():
                    target_hwnd = hwnd
                    target_pid = pid
                    return False

            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"EnumWindows warning: {e}")

        # WhatsApp fallback
        if target_hwnd is None and search_name == "whatsapp":
            try:
                target_hwnd = win32gui.FindWindow(None, "WhatsApp")

                if target_hwnd:
                    _, target_pid = win32process.GetWindowThreadProcessId(
                        target_hwnd
                    )

            except Exception as e:
                print(f"Window title search failed: {e}")

        if target_hwnd is None:
            speak(
                f"I found {app_name} running, but couldn't find its window."
            )
            print(f"Could not locate window for {app_name}.")
            return False

        speak(f"Maximizing {app_name}.")

        print(f"Window found: {win32gui.GetWindowText(target_hwnd)}")
        print(f"Process PID: {target_pid}")

        # Maximize the window
        win32gui.ShowWindow(
            target_hwnd,
            win32con.SW_MAXIMIZE
        )

        print(f"Maximized: {win32gui.GetWindowText(target_hwnd)}")

        # Try to bring it to the front.
        # If Windows blocks this, maximizing has still succeeded.
        try:
            win32gui.SetForegroundWindow(target_hwnd)
        except Exception as e:
            print(f"Foreground warning: {e}")

        return True

    except Exception as e:
        print(f"Maximize error: {e}")
        speak(f"I couldn't maximize {app_name}.")
        return False
# ==========================================
# CLOSE APPLICATION
# ==========================================

def close_app(app_name):
    aliases = {
        "vs code": "vscode",
        "vscode": "vscode",
        "chrome": "chrome",
        "google chrome": "chrome",
        "win rar": "winrar",
        "winrar": "winrar",
        "whatsapp": "whatsapp"
    }

    search_name = aliases.get(
        app_name.lower().strip(),
        app_name.lower().strip()
    )

    try:
        matching_pids = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                process_name = proc.info["name"]

                if not process_name:
                    continue

                normalized_process = (
                    process_name.lower()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                normalized_search = (
                    search_name.lower()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

                if normalized_search in normalized_process:
                    matching_pids.append(proc.info["pid"])

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not matching_pids:
            speak(f"{app_name} is not running.")
            print(f"{app_name} is not running.")
            return False

        print(f"Running PIDs found: {matching_pids}")

        # Find the application's window
        target_hwnd = None
        target_pid = None

        def callback(hwnd, extra):
            nonlocal target_hwnd, target_pid

            if not win32gui.IsWindowVisible(hwnd):
                return True

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            if pid in matching_pids:
                title = win32gui.GetWindowText(hwnd)

                if title.strip():
                    target_hwnd = hwnd
                    target_pid = pid
                    return False

            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"EnumWindows warning: {e}")

        # WhatsApp fallback
        if target_hwnd is None and search_name == "whatsapp":
            try:
                target_hwnd = win32gui.FindWindow(
                    None,
                    "WhatsApp"
                )

                if target_hwnd:
                    _, target_pid = win32process.GetWindowThreadProcessId(
                        target_hwnd
                    )

            except Exception as e:
                print(f"Window title search failed: {e}")

        # If we found a window, close it normally
        if target_hwnd:

            title = win32gui.GetWindowText(target_hwnd)

            speak(f"Closing {app_name}.")
            print(f"Closing: {title}")

            win32gui.PostMessage(
                target_hwnd,
                win32con.WM_CLOSE,
                0,
                0
            )

            print(f"Closed: {title}")
            return True

        # If no window was found, terminate matching process
        if matching_pids:

            speak(f"Closing {app_name}.")
            print(f"No window found. Terminating process...")

            for pid in matching_pids:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    print(f"Terminated PID: {pid}")
                except Exception as e:
                    print(f"Could not terminate PID {pid}: {e}")

            return True

        speak(f"I couldn't find {app_name}.")
        return False

    except Exception as e:
        print(f"Close error: {e}")
        speak(f"I couldn't close {app_name}.")
        return False