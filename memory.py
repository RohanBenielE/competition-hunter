import json
import os


MEMORY_FILE = "memory.json"


def load_memory():
    """Load saved memory from memory.json."""

    if not os.path.exists(MEMORY_FILE):
        return {
            "user_profile": {},
            "past_recommendations": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {
            "user_profile": {},
            "past_recommendations": []
        }


def save_memory(memory):
    """Save memory to memory.json."""

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=4
        )


def save_user_profile(profile):
    """Store the user's profile in memory."""

    memory = load_memory()

    memory["user_profile"] = profile

    save_memory(memory)


def get_user_profile():
    """Retrieve the previously stored user profile."""

    memory = load_memory()

    return memory.get(
        "user_profile",
        {}
    )


def save_recommendations(recommendations):
    """Store recommended competitions in memory."""

    memory = load_memory()

    memory["past_recommendations"] = recommendations

    save_memory(memory)


def get_past_recommendations():
    """Retrieve previous recommendations."""

    memory = load_memory()

    return memory.get(
        "past_recommendations",
        []
    )