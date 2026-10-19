from datetime import datetime, timezone


def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    if isinstance(text, str):
        stripped = text.strip()
        # Accept the "Z" (Zulu) suffix on Python versions whose fromisoformat
        # does not understand it.
        candidate = stripped
        if candidate.endswith(("Z", "z")):
            candidate = candidate[:-1] + "+00:00"
        parsed = datetime.fromisoformat(candidate)
    else:
        parsed = text

    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        # Naive timestamp: assume it is already UTC.
        return parsed.replace(tzinfo=timezone.utc)

    # Offset-aware timestamp: convert the instant to UTC.
    return parsed.astimezone(timezone.utc)
