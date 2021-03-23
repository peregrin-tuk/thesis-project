from music21.analysis import floatingKey
from music21.stream import Stream
from pretty_midi import PrettyMIDI

from src.io.conversion import pretty_midi_to_music21

def key(stream: Stream):
    """
    Estimates the overall key of the sequence using the KrumhanslSchmickler algorithm.
    Use field .alternateInterpretations to list other possible interpretations and their correlation coefficients

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed

    Returns:
        music21.key.Key: a key object holding all information about the estimated key
    """
    return stream.analyze('key') # TODO try out different weights and see how they perform (see Journal 18.3.)    


def key_per_bar(stream: Stream, window_size_in_bars: int = 1):
    """
    Estimates the key for every bar of the sequence using the KrumhanslSchmickler algorithm.

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed
        window_size_in_bars (int): default 1. can be altered if windows with lengths greater than 1 bar should be used for the analysis.

    Returns:
        list of music21.key: a list of key objects holding all information about the estimated key per bar
    """
    ka = floatingKey.KeyAnalyzer(stream)
    ka.windowSize = window_size_in_bars
    return ka.run()


#############################################################################################
#  CHECK legacy code for direct analysis from PrettyMIDI - delete at the end if not needed  #

def key_from_pm(melody: PrettyMIDI):
    """
    Estimates the overall key of the sequence using the KrumhanslSchmickler algorithm.
    Use field .alternateInterpretations to list other possible interpretations and their correlation coefficients


    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        music21.key.Key: a key object holding all information about the estimated key
    """
    stream = pretty_midi_to_music21(melody)
    return stream.analyze('key')   


def key_per_bar_from_pm(melody: PrettyMIDI, window_size_in_bars: int = 1):
    """
    Estimates the key for every bar of the sequence using the KrumhanslSchmickler algorithm.

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed
        window_size_in_bars (int): default 1. can be altered if windows with lengths greater than 1 bar should be used for the analysis.

    Returns:
        list of music21.key: a list of key objects holding all information about the estimated key per bar
    """
    stream = pretty_midi_to_music21(melody)
    ka = floatingKey.KeyAnalyzer(stream)
    ka.windowSize = window_size_in_bars
    return ka.run()