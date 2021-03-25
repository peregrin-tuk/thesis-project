from src.datatypes import melody_data
from src.datatypes.melody_data import AdaptationMelodyData, MelodyData
from src.io.conversion import pretty_midi_to_music21
# CHECK should this be a class? (= are there any settings to be made for an analysis module instance, as with adaptation and evaluation or not?)

def analyze(melody: AdaptationMelodyData, methods: set or list):
    result = {}
    for method in methods:
        result[method.__name__] = method(melody.sequence)
    return result

def analyze_md(melody: MelodyData, methods: set or list):
    result = {}
    stream = pretty_midi_to_music21(melody.sequence)
    for method in methods:
        result[method.__name__] = method(stream)
    return result
