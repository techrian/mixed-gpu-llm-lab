from datetime import datetime, timezone


def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    text = text.strip()
    if text.endswith(("Z", "z")):
        # fromisoformat accepts "Z" on 3.11+, but normalize for portability.
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        # Naive input: assume it is already UTC.
        return dt.replace(tzinfo=timezone.utc)
    # Offset-aware input: shift the instant to UTC (wall clock time changes).
    return dt.astimezone(timezone.utc)
