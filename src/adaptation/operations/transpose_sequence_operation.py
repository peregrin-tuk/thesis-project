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
        base_key = key(base.sequence)
        control_key = control_analysis[key.__name__]

        