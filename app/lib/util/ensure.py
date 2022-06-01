def ensure_list(value):
    """
    Takes a value, if it's a list return it
    Otherwise make it a list
    """
    if isinstance(value, list):
        return value
    else:
        return [value]
