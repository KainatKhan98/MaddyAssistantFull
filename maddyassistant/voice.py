# ==========================================
# MADDY V2 - VOICE SYSTEM
# ==========================================

import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import scipy.io.wavfile as wav
import os
import tempfile

from config import (
    SAMPLE_RATE,
    RECORD_SECONDS,
    VOICE_RATE,
    VOICE_VOLUME
)

recognizer = sr.Recognizer()

engine = pyttsx3.init()

engine.setProperty("rate", VOICE_RATE)
engine.setProperty("volume", VOICE_VOLUME)


# ==========================================
# TEXT TO SPEECH
# ==========================================

def speak(text):
    print(f"Maddy: {text}")

    engine.say(text)
    engine.runAndWait()


# ==========================================
# RECORD AUDIO
# ==========================================

def record_audio():

    print("\n Listening...")
    print("[MADDY DEBUG] Starting microphone recording...")

    try:

        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        return audio

    except Exception as e:

        print("Microphone error:", e)

        return None


# ==========================================
# SPEECH RECOGNITION
# ==========================================

def listen():

    audio_data = record_audio()

    if audio_data is None:
        return ""

    temp_filename = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:

            temp_filename = temp_file.name

        wav.write(
            temp_filename,
            SAMPLE_RATE,
            audio_data
        )

        with sr.AudioFile(temp_filename) as source:

            audio = recognizer.record(source)

        print(" Recognizing...")

        command = recognizer.recognize_google(audio)

        print(f"You: {command}")

        return command.lower()

    except sr.UnknownValueError:

        print("Maddy: I couldn't understand that.")

        return ""

    except sr.RequestError:

        speak(
            "I cannot connect to the speech recognition service."
        )

        return ""

    except Exception as e:

        print("Speech error:", e)

        return ""

    finally:

        if (
            temp_filename
            and os.path.exists(temp_filename)
        ):

            os.remove(temp_filename)