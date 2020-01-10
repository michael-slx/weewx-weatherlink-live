"""
Common utilities
"""


def is_string(o):
    """Test if object is a string"""
    return isinstance(o, str)


def to_list(o):
    """Wrap object in list, if it isn't one"""

    # Strings are iterable too
    if (not is_string(o)):
        try:
            return list(o)
        except TypeError:
            pass

    return [o]
