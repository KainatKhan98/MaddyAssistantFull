# ==========================================
# MADDY V3.5 - MEMORY & CONTEXT
# ==========================================

import json
import os


MEMORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "memory.json"
)


# ==========================================
# DEFAULT MEMORY
# ==========================================

DEFAULT_MEMORY = {
    "last_command": None,
    "last_intent": None,
    "last_target": None,
    "last_query": None,
    "last_app": None,
    "last_website": None,
    "conversation_active": False
}


# ==========================================
# CREATE MEMORY FILE
# ==========================================

def ensure_memory_file():

    folder = os.path.dirname(MEMORY_FILE)

    os.makedirs(folder, exist_ok=True)

    if not os.path.exists(MEMORY_FILE):

        save_memory(DEFAULT_MEMORY.copy())


# ==========================================
# LOAD MEMORY
# ==========================================

def load_memory():

    ensure_memory_file()

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            memory = json.load(file)

        return memory

    except (
        json.JSONDecodeError,
        OSError
    ):

        return DEFAULT_MEMORY.copy()


# ==========================================
# SAVE MEMORY
# ==========================================

def save_memory(memory):

    ensure_memory_folder = os.path.dirname(
        MEMORY_FILE
    )

    os.makedirs(
        ensure_memory_folder,
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4
        )


# ==========================================
# UPDATE MEMORY
# ==========================================

def update_memory(
    command=None,
    intent=None,
    target=None,
    query=None
):

    memory = load_memory()

    if command is not None:
        memory["last_command"] = command

    if intent is not None:
        memory["last_intent"] = intent

    if target is not None:
        memory["last_target"] = target

    if query is not None:
        memory["last_query"] = query

    if intent == "OPEN_APP":
        memory["last_app"] = target

    if intent == "OPEN_WEBSITE":
        memory["last_website"] = target

    save_memory(memory)


# ==========================================
# GET MEMORY VALUE
# ==========================================

def get_memory(key):

    memory = load_memory()

    return memory.get(key)


# ==========================================
# CLEAR MEMORY
# ==========================================

def clear_memory():

    save_memory(DEFAULT_MEMORY.copy())

    print("Memory cleared.")


# ==========================================
# SHOW MEMORY
# ==========================================

def show_memory():

    memory = load_memory()

    print("\n========== MADDY MEMORY ==========")

    for key, value in memory.items():

        print(f"{key}: {value}")

    print("==================================\n")