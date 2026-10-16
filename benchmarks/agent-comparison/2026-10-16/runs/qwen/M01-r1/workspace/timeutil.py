from datetime import datetime,timezone

def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    text = text.strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
