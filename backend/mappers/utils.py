def extract_id(value) -> int | None:

    if isinstance(value, (list, tuple)):
        return value[0]
    if value is False:
        return None
    return value