from music21.analysis import floatingKey
from music21.stream import Stream
from pretty_midi import PrettyMIDI

from src.io.conversion import pretty_midi_to_music21


### MONKEY PATCH for measure recognition in floating key analysis:

def _patched_getRawKeyByMeasure(self):
    """
    Used to monkey patch music21's internal getRawKeyByMeasure() method, as the original one fails to correctly iterate over the measures in the score.
    Difference to the original method: ".getElementsByClass('Measure')[i]" is used instead of ".measure(i)"
    """
    keyByMeasure = []
    for i in range(self.numMeasures):
        m = self.stream.getElementsByClass('Measure')[i]
        if m is None or not m.recurse().notes:
            k = None
        else:
            k = m.analyze('key')
        keyByMeasure.append(k)
    self.rawKeyByMeasure = keyByMeasure
    return keyByMeasure

floatingKey.KeyAnalyzer.getRawKeyByMeasure = _patched_getRawKeyByMeasure


### METHODS

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


def smoothed_key_per_bar(stream: Stream, window_size_in_bars: int = 1):
    """
    Estimates the key for every bar of the sequence using the KrumhanslSchmickler algorithm.

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed
        window_size_in_bars (int): default 1. can be altered if windows with lengths greater than 1 bar should be used for the analysis.

    Returns:
        list of music21.key: a list of key objects holding all information about the estimated key per bar
    """
    if not stream.hasMeasures():
        stream.makeMeasures(inPlace=True)
    ka = floatingKey.KeyAnalyzer(stream)
    ka.windowSize = window_size_in_bars
    return ka.run()

def raw_key_per_bar(stream: Stream):
    """
    Estimates the key for every bar of the sequence using the KrumhanslSchmickler algorithm.

    Args:
        stream: (music21.stream.Stream): sequence to be analyzed
        window_size_in_bars (int): default 1. can be altered if windows with lengths greater than 1 bar should be used for the analysis.

    Returns:
        list of music21.key: a list of key objects holding all information about the estimated key per bar
    """
    if not stream.hasMeasures():
        stream.makeMeasures(inPlace=True)
    ka = floatingKey.KeyAnalyzer(stream)
    return ka.getRawKeyByMeasure()