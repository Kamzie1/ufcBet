cyfry = "0123456789."


def is_number(x) -> bool:
    if isinstance(x, int) or isinstance(x, float):
        return True
    if not isinstance(x, str):
        return False
    if x == "":
        return False
    for idx, i in enumerate(x):
        if i not in cyfry:
            return False
        if i == "." and idx + 1 < len(x) and x[idx + 1] == ".":
            return False
    return True
