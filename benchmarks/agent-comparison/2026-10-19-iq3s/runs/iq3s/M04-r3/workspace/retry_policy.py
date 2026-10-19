def should_retry(method,status,attempt):
    """Retry GET/HEAD only, on 429 or 503, and only while attempt < 3. attempt starts at 1."""
    if method is None or str(method).strip().upper() not in ("GET", "HEAD"):
        return False
    if status not in (429, 503):
        return False
    try:
        return int(attempt) < 3
    except (TypeError, ValueError):
        return False
