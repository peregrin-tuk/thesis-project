import music21
from pretty_midi import PrettyMIDI
from definitions import SequenceType
from src.io.conversion import music21_to_pretty_midi, pretty_midi_to_music21


class AdaptationMelodyData():

    def __init__(self, sequence: music21.stream.Stream) -> None:
        self.sequence = sequence
        self.analysis = {}
        self.meta = {}


class MelodyData():

    def __init__(self, sequence: PrettyMIDI, sequence_type: SequenceType, meta: dict, analysis: dict = None, evaluation: dict = None) -> None:
        self.sequence = sequence
        self.sequence_type = sequence_type
        self.meta = meta
        self.analysis = analysis if analysis is not None else {}
        self.evaluation = evaluation if evaluation is not None else {}

    def to_adaptation_data(self):
        stream = pretty_midi_to_music21(self.sequence)
        return AdaptationMelodyData(stream)

    def update_sequence_from_adaptation_data(self, data: AdaptationMelodyData):
        self.sequence = music21_to_pretty_midi(data.sequence)
        self.analysis = {**self.analysis, **data.analysis}
        self.meta.setdefault('adaptation', {}).update(data.meta)