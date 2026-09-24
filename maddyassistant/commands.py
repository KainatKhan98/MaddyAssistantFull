# ==========================================
# MADDY V3 - COMMAND HANDLER
# ==========================================

from intents import detect_intent
from app_manager import (
    open_app,
    close_app,
    is_app_running,
    get_running_apps,
    switch_to_app,
    minimize_app,
    restore_app,
    maximize_app
)
from actions import *
from voice import speak
from memory import (
    update_memory,
    get_memory,
    show_memory,
    clear_memory
)
from system_control import (
    increase_volume,
    decrease_volume,
    mute_volume,
    minimize_window,
    maximize_window,
    lock_computer,
    restart_computer,
    shutdown_computer,
    cancel_shutdown,
    take_screenshot
)

def process_command(command):

    result = detect_intent(command)

    intent = result["intent"]
    target = result["target"]
    query = result["query"]
    
    # ======================================
    # SAVE ONLY REAL ACTIONS
    # ======================================

    memory_intents = [
        "OPEN_APP",
        "CLOSE_APP",
        "OPEN_WEBSITE",
        "GOOGLE_SEARCH",
        "YOUTUBE_SEARCH",
        "OPEN_FOLDER",
        "TIME",
        "DATE",
        "SCREENSHOT",
        "VOLUME_UP",
        "VOLUME_DOWN",
        "MUTE",
        "MINIMIZE",
        "MAXIMIZE",
        "LOCK",
        "RESTART",
        "SHUTDOWN",
        "CANCEL_SHUTDOWN",
        "TYPE"
    ]

    if intent in memory_intents:

        update_memory(
            command=command,
            intent=intent,
            target=target,
            query=query
        )
    
    # ======================================
    # DEBUG INFORMATION
    # ======================================

    print(f"Intent: {intent}")
    print(f"Target: {target}")
    print(f"Query: {query}")

    # ==========================================
    # CONVERSATION
    # ==========================================

    if intent == "GREETING":

        speak("Hello! How can I help you?")

    elif intent == "HOW_ARE_YOU":

        speak("I'm doing great. Ready to help.")

    elif intent == "THANKS":

        speak("You're welcome.")

    elif intent == "CAPABILITIES":

        speak(
            "I can open and close applications, "
            "search Google and YouTube, control "
            "your computer, manage volume, take "
            "screenshots, and much more."
        )
    # ==========================================
    # CHECK APP STATUS
    # ==========================================

    elif intent == "CHECK_APP_STATUS":

        app_name = target

        if is_app_running(app_name):

            speak(
                f"Yes, {app_name} is currently running."
            )

            print(
                f"Status: {app_name} is running."
            )

        else:

            speak(
                f"No, {app_name} is not currently running."
            )

            print(
                f"Status: {app_name} is not running."
            )


    # ==========================================
    # LIST RUNNING APPS
    # ==========================================

    elif intent == "LIST_RUNNING_APPS":

        running_apps = get_running_apps()

        if running_apps:

            print("\nRunning apps:")

            for app in running_apps:
                print(f"- {app}")

            app_list = ", ".join(running_apps)

            speak(
                f"The currently running applications are: "
                f"{app_list}."
            )

        else:

            speak(
                "I couldn't find any recognized applications running."
            )

            print(
                "No recognized applications are running."
            )
    # ==========================================
    # OPEN APPLICATION
    # ==========================================

    elif intent == "OPEN_APP":

        open_app(target)

    # ==========================================
    # MINIMIZE APPLICATION
    # ==========================================
    elif intent == "MINIMIZE_APP":

     minimize_app(target)
    # ==========================================
    # SWITCH APPLICATION
    # ==========================================
    elif intent == "SWITCH_APP":

        switch_to_app(target)

    # ==========================================
    # RESTORE APPLICATION
    # ==========================================
    elif intent == "RESTORE_APP":
        restore_app(target)

    # ==========================================
    # MAXIMIZE APPLICATION
    # ==========================================
    elif intent == "MAXIMIZE_APP":
        maximize_app(target)    
    # ==========================================
    # CLOSE APPLICATION
    # ==========================================

    elif intent == "CLOSE_APP":

        close_app(target)

    # ==========================================
    # WEBSITE
    # ==========================================

    elif intent == "OPEN_WEBSITE":

        if target == "youtube":

            open_youtube()

        elif target == "google":

            open_google()

    # ==========================================
    # GOOGLE SEARCH
    # ==========================================

    elif intent == "GOOGLE_SEARCH":

        google_search(query)

    # ==========================================
    # YOUTUBE SEARCH
    # ==========================================

    elif intent == "YOUTUBE_SEARCH":

        youtube_search(query)

    # ==========================================
    # FOLDERS
    # ==========================================

    elif intent == "OPEN_FOLDER":

        if target == "downloads":

            open_downloads()

        elif target == "documents":

            open_documents()

        elif target == "desktop":

            open_desktop()

    # ==========================================
    # TIME
    # ==========================================

    elif intent == "TIME":

        tell_time()

    # ==========================================
    # DATE
    # ==========================================

    elif intent == "DATE":

        tell_date()

    # ==========================================
    # SCREENSHOT
    # ==========================================

    elif intent == "SCREENSHOT":

        take_screenshot()

    # ==========================================
    # VOLUME
    # ==========================================

    elif intent == "VOLUME_UP":

        increase_volume()

    elif intent == "VOLUME_DOWN":

        decrease_volume()

    elif intent == "MUTE":

        mute_volume()

    # ==========================================
    # WINDOW CONTROL
    # ==========================================

    elif intent == "MINIMIZE":

        minimize_window()

    elif intent == "MAXIMIZE":

        maximize_window()

    # ==========================================
    # SYSTEM CONTROL
    # ==========================================

    elif intent == "LOCK":

        lock_computer()

    elif intent == "RESTART":

        restart_computer()

    elif intent == "SHUTDOWN":

        shutdown_computer()

    elif intent == "CANCEL_SHUTDOWN":

        cancel_shutdown()

    # ==========================================
    # MEMORY
    # ==========================================

    elif intent == "SHOW_MEMORY":

        show_memory()

        speak(
            "I displayed what I currently remember."
        )

    elif intent == "CLEAR_MEMORY":

        clear_memory()

        speak(
            "My memory has been cleared."
        )

    elif intent == "LAST_COMMAND":

        last_command = get_memory("last_command")

        if last_command:

            speak(
                f"Your last command was {last_command}."
            )

            print(
                f"Last command: {last_command}"
            )

        else:

            speak(
                "I don't remember your previous command."
            )

    elif intent == "LAST_ACTION":

        last_intent = get_memory("last_intent")
        last_target = get_memory("last_target")

        if last_intent:

            if last_target:

                speak(
                    f"My last action was {last_intent.replace('_', ' ').lower()} "
                    f"{last_target}."
                )

            else:

                speak(
                    f"My last action was "
                    f"{last_intent.replace('_', ' ').lower()}."
                )

        else:

            speak(
                "I don't remember my previous action."
            )

    # ==========================================
    # CONTEXT COMMANDS
    # ==========================================

    elif intent == "REOPEN_LAST_APP":

        last_app = get_memory("last_app")

        if last_app:

            speak(
                f"Opening {last_app} again."
            )

            open_app(last_app)

        else:

            speak(
                "I don't remember the last application."
            )

    elif intent == "REPEAT_LAST":

        last_command = get_memory("last_command")

        if last_command:

            # Prevent infinite recursion
            if last_command.lower().strip() == command.lower().strip():

                speak(
                    "I can't repeat that command because "
                    "it would create a loop."
                )

            else:

                speak(
                    "Repeating the last command."
                )

                process_command(last_command)

        else:

            speak(
                "I don't have a previous command to repeat."
            )

    elif intent == "SIMILAR_SEARCH":

        last_query = get_memory("last_query")

        if last_query:

            new_query = f"similar to {last_query}"

            speak(
                f"Searching for something similar to {last_query}."
            )

            google_search(new_query)

        else:

            speak(
                "I don't have a previous search."
            )

    # ==========================================
    # TYPE TEXT
    # ==========================================

    elif intent == "TYPE":

        if query:

            type_text(query)

        else:

            speak(
                "What would you like me to type?"
            )

    # ==========================================
    # EXIT
    # ==========================================

    elif intent == "EXIT":

        speak("Goodbye.")

        return False

    # ==========================================
    # UNKNOWN
    # ==========================================

    else:

        speak(
            "I'm not sure what you want me to do."
        )

        print(
            f"Unknown command: {query}"
        )

    return True

