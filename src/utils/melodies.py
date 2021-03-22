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