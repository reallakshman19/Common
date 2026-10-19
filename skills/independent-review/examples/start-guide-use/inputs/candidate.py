def remove_first(values, item):
    remaining = list(values)
    if item in remaining:
        remaining.remove(item)
    return remaining
