"""
LifeSync Agent — Personal AI Concierge
Built with Google ADK (Agent Development Kit) and Gemini.

This module defines the LifeSync agent and its tools.
The agent acts as a personal concierge that can help with
everyday tasks like checking the time, doing calculations,
getting weather info, and taking notes.
"""

import datetime
import math
import random


# ---------------------------------------------------------------------------
# Tool Definitions
# Each tool is a plain Python function with a docstring that the LLM reads
# to understand when and how to call it.
# ---------------------------------------------------------------------------

def get_current_datetime(timezone_offset: int = 0) -> dict:
    """Get the current date and time.

    Use this tool when the user asks what time or date it is,
    or needs any information about the current moment.

    Args:
        timezone_offset: UTC offset in hours (e.g., 5 for IST, -5 for EST).
                         Defaults to 0 (UTC).

    Returns:
        A dictionary with the current date, time, day of week, and timezone.
    """
    tz = datetime.timezone(datetime.timedelta(hours=timezone_offset))
    now = datetime.datetime.now(tz)
    return {
        "date": now.strftime("%B %d, %Y"),
        "time": now.strftime("%I:%M %p"),
        "day_of_week": now.strftime("%A"),
        "timezone": f"UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset}",
        "iso": now.isoformat(),
    }


def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression safely.

    Use this tool when the user asks you to calculate, compute,
    or do any math. Supports basic arithmetic (+, -, *, /, **),
    and common math functions (sqrt, sin, cos, tan, log, pi, e).

    Args:
        expression: A mathematical expression string, e.g. "2 + 3 * 4"
                    or "sqrt(144)" or "pi * 3**2".

    Returns:
        A dictionary containing the expression and its result,
        or an error message if the expression is invalid.
    """
    # Security: only allow safe math characters and functions
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
    }

    # Sanitize: reject anything that isn't math-related
    safe_chars = set("0123456789+-*/.() ,")
    cleaned = expression
    for name in allowed_names:
        cleaned = cleaned.replace(name, "")
    if not all(c in safe_chars for c in cleaned.strip()):
        return {"expression": expression, "error": "Invalid characters in expression. Only numbers, operators, and math functions are allowed."}

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
        return {"expression": expression, "result": str(result)}
    except Exception as e:
        return {"expression": expression, "error": f"Could not evaluate: {str(e)}"}


def get_weather(city: str) -> dict:
    """Get current weather information for a city.

    Use this tool when the user asks about the weather in any city.
    Note: This provides simulated weather data for demonstration purposes.

    Args:
        city: The name of the city to get weather for, e.g. "London" or "New York".

    Returns:
        A dictionary with weather information including temperature,
        conditions, humidity, and wind speed.
    """
    # Simulated weather data — deterministic based on city name
    # so the same city always returns consistent results within a session
    seed = sum(ord(c) for c in city.lower())
    rng = random.Random(seed + datetime.date.today().toordinal())

    conditions = ["Sunny ☀️", "Partly Cloudy ⛅", "Cloudy ☁️", "Rainy 🌧️", "Thunderstorm ⛈️", "Snowy ❄️", "Windy 💨", "Clear 🌤️"]
    temp_base = rng.randint(5, 38)

    return {
        "city": city.title(),
        "temperature_celsius": temp_base,
        "temperature_fahrenheit": round(temp_base * 9 / 5 + 32, 1),
        "condition": rng.choice(conditions),
        "humidity_percent": rng.randint(30, 90),
        "wind_speed_kmh": rng.randint(5, 45),
        "note": "⚠️ This is simulated weather data for demonstration purposes.",
    }


# In-memory note storage (per-process; resets on restart)
_notes_store: list[str] = []


def take_note(note: str) -> dict:
    """Save a note for the user.

    Use this tool when the user wants to remember something,
    save a note, or jot something down.

    Args:
        note: The text content of the note to save.

    Returns:
        A confirmation with the note number and content.
    """
    _notes_store.append(note)
    return {
        "status": "saved",
        "note_number": len(_notes_store),
        "content": note,
        "total_notes": len(_notes_store),
    }


def get_notes() -> dict:
    """Retrieve all saved notes.

    Use this tool when the user wants to see their notes,
    review what they've saved, or check their note list.

    Returns:
        A dictionary with the list of all saved notes.
    """
    if not _notes_store:
        return {"notes": [], "message": "No notes saved yet. Use 'take a note' to save one!"}
    return {
        "notes": [{"number": i + 1, "content": n} for i, n in enumerate(_notes_store)],
        "total": len(_notes_store),
    }


# ---------------------------------------------------------------------------
# Agent Definition
# ---------------------------------------------------------------------------

def create_agent():
    """Create and return the LifeSync ADK Agent.

    Uses lazy import so the module can be loaded even if google-adk
    is not installed (useful for tests / linting).
    """
    from google.adk.agents import Agent  # noqa: E402

    agent = Agent(
        name="lifesync",
        model="gemini-2.5-flash",
        instruction=(
            "You are **LifeSync**, a friendly and helpful personal concierge AI agent. "
            "Your purpose is to assist users with everyday tasks and make their life easier.\n\n"
            "## Your Personality\n"
            "- Warm, approachable, and concise\n"
            "- Use emojis sparingly but effectively to add personality\n"
            "- Give direct, helpful answers — don't be overly verbose\n"
            "- If you don't know something, say so honestly\n\n"
            "## Your Capabilities (Tools)\n"
            "You have access to these tools — use them when relevant:\n"
            "1. **get_current_datetime** — Check the current date and time in any timezone\n"
            "2. **calculate** — Perform math calculations\n"
            "3. **get_weather** — Check weather for any city (simulated data)\n"
            "4. **take_note** / **get_notes** — Save and retrieve notes for the user\n\n"
            "## Guidelines\n"
            "- Always use your tools when the user's request matches a tool's purpose\n"
            "- Format responses nicely with markdown when appropriate\n"
            "- Keep responses concise but complete\n"
            "- When showing weather, format it in a readable way\n"
            "- When doing calculations, show both the expression and result\n"
        ),
        tools=[get_current_datetime, calculate, get_weather, take_note, get_notes],
    )
    return agent
