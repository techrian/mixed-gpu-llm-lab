def should_retry(method, status, attempt):
    """Retry GET/HEAD only, on 429 or 503, and only while attempt < 3. attempt starts at 1."""
    if not isinstance(method, str):
        return False
    if not isinstance(attempt, (int, float)) or isinstance(attempt, bool):
        return False
    return method.upper() in ("GET", "HEAD") and status in (429, 503) and attempt < 3
