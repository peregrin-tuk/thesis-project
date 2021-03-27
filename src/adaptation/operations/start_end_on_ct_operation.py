from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData

from src.analysis.harmonic import key

class StartEncOnCTOperation(AbstractAdaptationOperation):

    def __init__(self):
        super().__init__()
        self.required_analysis = { key }


    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        control_key = control_analysis[key.__name__]

        # use getChord() to get the chord of the control_key at a range around the start/end tone of the base sequence

        # use chord.notes to get the notes

        # use note.pitch.ps to calculate the closest chord tone