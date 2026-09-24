# ==========================================
# MADDY V3.6.1 - SMART LISTENING
# ==========================================

from voice import listen, speak
from commands import process_command



# ==========================================
# SMART LISTENING MODE
# ==========================================

SMART_LISTENING = False


def main():

    global SMART_LISTENING

    print("=" * 60)
    print("                    MADDY V3.6.1")
    print("             Voice Computer Assistant")
    print("=" * 60)

    speak("Hello. I am Maddy. How can I help you?")

    while True:

        # ==========================================
        # LISTEN FOR COMMAND
        # ==========================================

        command = listen()

        if not command:
            continue

        print(f"\nHeard: {command}")

        command_lower = command.lower().strip()

        # ==========================================
        # SMART LISTENING MODE
        # ==========================================

        if SMART_LISTENING:

            # Commands that stop smart listening
            sleep_phrases = [
                "go to sleep",
                "stop listening",
                "stop listening maddy",
                "that's enough",
                "thats enough",
                "sleep",
                "exit listening mode"
            ]

            if any(
                phrase in command_lower
                for phrase in sleep_phrases
            ):

                speak("Okay. I'll wait until you need me.")

                SMART_LISTENING = False

                print("\nSmart Listening: OFF")

                continue

            # Process command without requiring wake word
            should_continue = process_command(command)

            if not should_continue:
                break

            continue

        # ==========================================
        # WAKE WORD DETECTION
        # ==========================================

        wake_words = [
            "maddy",
            "mary",
            "meri",
            "buddy",
            "muddy",
            "lady",
            "madam",
            "baby"
        ]

        if any(
            word in command_lower
            for word in wake_words
        ):

            cleaned_command = command_lower

            for wake_word in [
                "hey maddy",
                "hello maddy",
                "hi maddy",
                "maddy",

                "hey buddy",
                "hello buddy",
                "hi buddy",
                "buddy",

                "hey muddy",
                "hello muddy",
                "hi muddy",
                "muddy",

                "hey lady",
                "hello lady",
                "hi lady",
                "lady",

                "hey mary",
                "hello mary",
                "hi mary",
                "mary",

                "hey meri",
                "hello meri",
                "hi meri",
                "meri"
                
                "hey baby",
                "hello baby",
                "hi baby",
                "baby"
                
                "hey madam",
                "hello madam",
                "hi madam",
                "madam"
            ]:

                cleaned_command = cleaned_command.replace(
                    wake_word,
                    ""
                )

            cleaned_command = cleaned_command.strip()

            # ==========================================
            # ONLY WAKE WORD
            # ==========================================

            if not cleaned_command:

                speak(
                    "I'm listening. What would you like me to do?"
                )

                SMART_LISTENING = True

                print("\nSmart Listening: ON")

                continue

            # ==========================================
            # COMMAND WITH WAKE WORD
            # ==========================================

            should_continue = process_command(command)

            if not should_continue:
                break

        else:

            print("Wake word not detected.")


if __name__ == "__main__":
    main()