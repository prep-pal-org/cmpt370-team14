import re

# -----------------------------
# Extract duration from a step
# -----------------------------
def extract_duration(text: str) -> int | None:
    """
    Extracts a duration (in seconds) from a step.
    Returns None if no time is found.
    """
    text = text.lower()

    patterns = [
        (r"(\d+)\s*(?:hours|hrs|hr|hr)", 3600),
        (r"(\d+)\s*(?:mins|minutes|minute|min)", 60),
        (r"(\d+)\s*(?:secs|seconds|sec|second)", 1),
    ]

    total_seconds = 0
    found = False

    for pattern, multiplier in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if m.isdigit():
                total_seconds += int(m) * multiplier
                found = True

    return total_seconds if found else None


# -----------------------------
# Convert block of instructions → list of steps
# -----------------------------
def split_into_steps(instructions: str):
    """
    Splits instructions by:
    - newline
    - period
    - comma
    - semicolon

    Removes empty lines.
    Returns list of clean steps.
    """
    raw_parts = re.split(r"[.\n!;]+", instructions)
    steps = [p.strip() for p in raw_parts if p.strip()]
    return steps
