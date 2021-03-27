"""
Utility functions for melodic operations.

"""

def get_pitch_class(pitch: int):
    """
    Returns the pitch class as integer.

    Args:
        pitch (int): source pitch

    Returns:
        int: pitch class between 0 and 12
    """
    return pitch % 12


def find_closest(allowed_values: list, given_value: int or float):
    """
    Given a list of numbers, it returns the number that is closest to the input value.

    Args:
        allowed_values (list): list of allowed values
        given_value (int or float): the value that has to be compared against the list

    Returns:
        int: closest allowed value
    """
    absolute_difference = lambda list_value : abs(list_value - given_value)
    return min(allowed_values, key=absolute_difference)