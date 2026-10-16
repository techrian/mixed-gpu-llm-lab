from datetime import datetime, timezone

def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
