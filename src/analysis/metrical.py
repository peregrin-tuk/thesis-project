from music21.analysis import metrical
from pretty_midi import PrettyMIDI

from src.io.conversion import pretty_midi_to_music21


def get_thomassen_melodic_accent(melody: PrettyMIDI):
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


def get_beat_strength(melody: PrettyMIDI):
    """
    Returns the beat strength of each note in the sequence.

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        list of floats: beat strength values per note
    """
    beat_strength = []
    stream = pretty_midi_to_music21(melody)
    metrical.labelBeatDepth(stream)
    for n in stream.flat.notes:
        beat_strength.append(n.beatStrength)
    return beat_strength