from music21.stream import Stream
from music21.analysis.discrete import Ambitus

def ambitus(stream: Stream):
    """
    Returns the ambitus of a sequence

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed

    Returns:
        music21.interval.Interval: an interval object in the size of the sequence's ambitus
    """
    return stream.analyze('ambitus') 

def pitch_span(stream: Stream):
    """
    Returns the highest and the lowest pitch in the sequence

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed

    Returns:
        tuple containing:
            music21.pitch.Pitch: lowest pitch in the sequence
            music21.pitch.Pitch: highest pitch in the sequence
    """
    a = Ambitus()
    return a.getPitchSpan(stream)