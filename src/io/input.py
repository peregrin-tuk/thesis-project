from pretty_midi import PrettyMIDI

def loadMidiFile(file_path: str):
    """
    opens midi file from path
    returns pretty_midi object
    """
    return PrettyMIDI(file_path)