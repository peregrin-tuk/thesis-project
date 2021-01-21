from pretty_midi import PrettyMIDI

def loadMidiFile(file_path: str):
    """
    Opens a midi file from path.

    Args:
        file_path (str): Location fo the MIDI file

    Returns:
        PrettyMIDI: pretty_midi object
    """
    return PrettyMIDI(file_path)