from datetime import datetime,timezone

def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    if isinstance(text, str):
        stripped = text.strip()
        # fromisoformat only accepts the trailing 'Z' offset on Python 3.11+.
        if stripped[-1:] in ("Z", "z"):
            stripped = stripped[:-1] + "+00:00"
        parsed = datetime.fromisoformat(stripped)
    else:
        parsed = text
    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        # Naive input is assumed to already be UTC.
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
