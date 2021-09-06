from music21.analysis import metrical
from music21.stream import Stream


def thomassen_melodic_accent(stream: Stream):
    """
    Calculates the melodic accent of each note in a melody based on Joseph M. Thomassen, “Melodic accent: Experiments and a tentative model” (1982)

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        list of floats: melodic accent values per note
    """
    melodic_accent = []
    metrical.thomassenMelodicAccent(stream.flat.notes)
    for n in stream.flat.notes:
        melodic_accent.append(n.melodicAccent)
    return melodic_accent


def beat_strength(stream: Stream):
    """
    Returns the beat strength of each note in the sequence.

    Args:
        stream (music21.stream.Stream): sequence to be analyzed

    Returns:
        list of floats: beat strength values per note
    """
    beat_strengths = []
    for n in stream.flat.notes:
        beat_strengths.append(n.beatStrength)
    return beat_strengths


def note_offsets_per_beat(stream: Stream):
    """
    Extracts the offset of each note in relation to the closest preceding beat position. Returns a list of observed note offsets for each beat position.
    Values of different measures are consolidated. E.g. all offsets related to beat 0 in every bar are written into the same list and returned at index 0 of the returned list.
    That means for a melody with a time signature of 4/4, the returned list will have a length of 4 with each index holding a list of observed offset values at those positions.

    Args:
        stream (music21.stream.Stream): sequence to be analyzed

    Returns:
        list of int lists: 2-dimensional list holding a list of observed offsets in reference to each beat position.
    """
    offset_list = []

    if stream.timeSignature is not None:
        beat_count = stream.timeSignature.numerator
    else:
        beat_count = 4 

    for i in range(0, beat_count):
        empty_set = set()
        offset_list.append(empty_set)

    for n in stream.flat.notes:
        beat = int(n.offset) % beat_count
        relative_offset = float(n.offset % 1)
        offset_list[beat].add(relative_offset)

    for i in range(0, beat_count):
        offset_list[i] = sorted(offset_list[i])
 
    return offset_list
