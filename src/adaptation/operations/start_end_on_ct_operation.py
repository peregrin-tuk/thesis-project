from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody import Melody

from src.analysis.harmonic import key

class StartEncOnCTOperation(AbstractAdaptationOperation):

    def __init__(self):
        self._required_analysis = set(key)

    @property
    def required_analysis(self):
        return self._required_analysis

    def execute(self, base: Melody, control: Melody, control_analysis: dict):
        control_key = control_analysis[key.__name__]