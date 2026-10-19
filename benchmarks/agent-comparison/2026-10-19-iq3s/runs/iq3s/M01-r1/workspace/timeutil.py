from datetime import datetime, timezone


def as_utc(text):
    """Parse ISO-8601, assume UTC for naive timestamps, return aware UTC datetime."""
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        # Fallback for older Python versions that reject a trailing "Z"/"z".
        if text.endswith(("Z", "z")):
            parsed = datetime.fromisoformat(text[:-1] + "+00:00")
        else:
            raise

    if parsed.tzinfo is None:
        # Naive input: assume it is already UTC.
        return parsed.replace(tzinfo=timezone.utc)

    # Offset-aware input: convert the instant to UTC.
    return parsed.astimezone(timezone.utc)
