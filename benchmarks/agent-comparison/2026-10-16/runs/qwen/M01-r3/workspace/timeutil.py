from datetime import datetime,timezone

def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    text=text.strip()
    # datetime.fromisoformat() rejects a trailing 'Z' before 3.11; normalise it.
    if text.endswith(("Z","z")):
        text=text[:-1]+"+00:00"
    parsed=datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        # Naive input: assume it already denotes UTC.
        return parsed.replace(tzinfo=timezone.utc)
    # Offset-aware input: convert the same instant to UTC.
    return parsed.astimezone(timezone.utc)
