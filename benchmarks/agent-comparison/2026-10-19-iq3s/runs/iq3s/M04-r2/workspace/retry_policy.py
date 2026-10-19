def should_retry(method,status,attempt):
    """Retry GET/HEAD only, on 429 or 503, and only while attempt < 3. attempt starts at 1."""
    if not isinstance(method, str) or method.upper() not in ("GET", "HEAD"):
        return False
    if status not in (429, 503):
        return False
    try:
        return attempt < 3
    except TypeError:
        return False
