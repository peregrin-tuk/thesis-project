import time

from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData

from src.utils.melodies import find_closest
from src.analysis.harmonic import key
from src.analysis.melodic import pitch_span

class TransposeNotesOperation(AbstractAdaptationOperation):

    def __init__(self):
        super().__init__()
        self.required_analysis = { key }

    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData, control_analysis: dict):
        t1 = time.time()

        control_key = control_analysis[key.__name__]
        base_span = pitch_span(base.sequence)

        # get scale pitches in range of [lowest base note - 2 semitones; highest base note + 2 semitones]
        pitch_list = control_key.getPitches(base_span[0].transpose(-2), base_span[1].transpose(2))
        ps_list = [pitch.ps for pitch in pitch_list]

        # for each pitch in base get closest pitch in allowed pitches and transpose
        for n in base.sequence.flat.notes:
            if (n.pitch not in pitch_list):
                ps = find_closest(ps_list, n.pitch.ps)
                n.pitch.ps = ps

        t2 = time.time()
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, base.sequence)


        