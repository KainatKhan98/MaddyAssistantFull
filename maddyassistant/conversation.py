# ==========================================
# MADDY V3.4 - CONVERSATION MODE
# ==========================================

import time

from voice import listen, speak
from commands import process_command


# ==========================================
# SETTINGS
# ==========================================

CONVERSATION_TIMEOUT = 15


# ==========================================
# CONVERSATION MODE
# ==========================================

def start_conversation():

    speak("Yes, how can I help?")

    print("\n" + "=" * 50)
    print("MADDY CONVERSATION MODE")
    print("=" * 50)
    print("Say 'goodbye', 'stop listening', or stay silent")
    print(f"for {CONVERSATION_TIMEOUT} seconds to exit.")
    print("=" * 50)

    last_activity = time.time()

    while True:

        # ----------------------------------
        # Check timeout
        # ----------------------------------

        if time.time() - last_activity >= CONVERSATION_TIMEOUT:

            speak("I'll wait until you need me.")

            print("\nConversation mode ended.")

            return True


        # ----------------------------------
        # Listen
        # ----------------------------------

        command = listen()

        if not command:
            continue

        print(f"\nConversation Heard: {command}")

        last_activity = time.time()

        # ----------------------------------
        # Exit conversation
        # ----------------------------------

        cleaned = command.lower().strip()

        exit_phrases = [
            "goodbye",
            "bye",
            "stop listening",
            "that's enough",
            "thats enough",
            "go to sleep",
            "sleep",
            "exit conversation"
        ]

        if any(
            phrase in cleaned
            for phrase in exit_phrases
        ):

            speak("Okay. I'll wait.")

            print("Conversation mode ended.")

            return True

        # ----------------------------------
        # Process command
        # ----------------------------------

        should_continue = process_command(command)

        if not should_continue:

            return False

        last_activity = time.time()