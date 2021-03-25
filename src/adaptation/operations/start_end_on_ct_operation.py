from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData

from src.analysis.harmonic import key

class StartEncOnCTOperation(AbstractAdaptationOperation):

    def __init__(self):
        super().__init__()
        self.required_analysis = { key }


    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        control_key = control_analysis[key.__name__]