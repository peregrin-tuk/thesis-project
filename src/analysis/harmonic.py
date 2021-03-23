from music21.key import Key
from music21.analysis import floatingKey
from pretty_midi import PrettyMIDI

from src.io.conversion import pretty_midi_to_music21


def key(melody: PrettyMIDI):
    """
    Estimates the overall key of the sequence using the KrumhanslSchmickler algorithm.
    Use field .alternateInterpretations to list other possible interpretations and their correlation coefficients


    Args:
        melody (PrettyMIDI): midi sequence to be analyzed

    Returns:
        music21.key.Key: a key object holding all information about the estimated key
    """
    stream = pretty_midi_to_music21(melody)
    return stream.analyze('key') # TODO try out different weights and see how they perform (see Journal 18.3.)


# TODO del? die Methode macht eigentlich kan Sinn - is doppelt gemoppelt (key objekt enthält schon alle infos)
def correlation_values(melody: PrettyMIDI, analyzed_key: Key = None):
    """
    Returns list of possible keys with correlation coefficients.

    Args:
        melody (PrettyMIDI): midi sequence to be analyzed
        analyzedKey (music21.key.Key): optional - a key object of a previously analyzed key

    Returns:
        music21.key: a list of possible keys and their correlation coefficients.
    """
    correlation_values = []
    if analyzed_key is None:
        stream = pretty_midi_to_music21(melody)
        analyzed_key = stream.analyze('key')
    correlation_values.append({'key': analyzed_key.asKey, 'corr': analyzed_key.correlationCoefficient} )
    for key in analyzed_key.alternateInterpretations:
        correlation_values.append({'key': key, 'corr': key.correlationCoefficient})
    return correlation_values
    


def key_per_bar(melody: PrettyMIDI, window_size_in_bars: int = 1):
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