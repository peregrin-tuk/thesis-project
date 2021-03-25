import time
from music21.interval import Interval

from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData
from src.analysis.harmonic import key

class TransposeSequenceOperation(AbstractAdaptationOperation):

    def __init__(self):
        self._required_analysis = set(key)

    @property
    def required_analysis(self):
        return self._required_analysis

    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        t1 = time.time()

        base_key = key(base.sequence)
        control_key = control_analysis[key.__name__]

        i = Interval(base_key.tonic, control_key.tonic)
        adapted_sequence = base.sequence.transpose(i)

        t2 = time.time()
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, adapted_sequence)