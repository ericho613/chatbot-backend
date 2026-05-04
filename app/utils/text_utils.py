def truncate_text(text: str, max_chars: int) -> str:
    """
    Truncate large text inputs to reduce model overrun risk.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars]