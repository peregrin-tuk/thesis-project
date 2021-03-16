"""
Utility functions for string operations.

"""


def remove_prefix(text, prefix):
    """
    Removes a prefix from a string, if the given text string starts with that prefix.

    Args:
        text (str): source string
        prefix (str): the prefix to be removed

    Returns:
        str: source string without prefix
    """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text, suffix):
    """
    Removes a suffix from a string, if the given text string ends with that prefix.

    Args:
        text (str): source string
        suffix (str): the suffix to be removed

    Returns:
        str: source string without suffix
    """
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text