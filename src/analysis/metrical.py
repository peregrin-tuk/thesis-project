from music21.analysis import metrical
from music21.stream import Stream
from pretty_midi import PrettyMIDI

from src.io.conversion import pretty_midi_to_music21


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


# CHECK a a bissl unnötig oder?
def beat_strength(stream: Stream):
    """
    Returns the beat strength of each note in the sequence.

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        list of floats: beat strength values per note
    """
    beat_strengths = []
    for n in stream.flat.notes:
        beat_strengths.append(n.beatStrength)
    return beat_strengths


#############################################################################################
#  CHECK legacy code for direct analysis from PrettyMIDI - delete at the end if not needed  #

def thomassen_melodic_accent_from_pm(melody: PrettyMIDI):
    """
    Calculates the melodic accent of each note in a melody based on Joseph M. Thomassen, “Melodic accent: Experiments and a tentative model” (1982)

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        list of floats: melodic accent values per note
    """
    melodic_accent = []
    stream = pretty_midi_to_music21(melody)
    metrical.thomassenMelodicAccent(stream.flat.notes)
    for n in stream.flat.notes:
        melodic_accent.append(n.melodicAccent)
    return melodic_accent


def beat_strength_from_pm(melody: PrettyMIDI):
    """
    Returns the beat strength of each note in the sequence.

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        list of floats: beat strength values per note
    """
    beat_strengths = []
    stream = pretty_midi_to_music21(melody)
    for n in stream.flat.notes:
        beat_strengths.append(n.beatStrength)
    return beat_strengths