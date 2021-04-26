# (1)
# simply shift note_offsets to closest allowed note_offset (to beat)
# (2)
# Take only into account the note_offsets to the closest previous beat position in the measure => 4 bar input gives min. 4 possible values
# (3)
# like 1 but instead of choosing the closest introduce weights by occurance

# make sure notes don't start at the same time

# flaws: will probably not recreate rhythmical feel / structure
# note: should probably run same note value adaptation step first

import time

from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData

from src.utils.melodies import find_closest
from src.analysis.metrical import note_offsets_per_beat

class SameNoteOffsetsOperation(AbstractAdaptationOperation):
    """Changes all note offsets at a certain beat position to a note offset that also occures in the control sequence at that beat position."""

    def __init__(self):
        super().__init__()
        self.required_analysis = { note_offsets_per_beat }

    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData):
        t1 = time.time()

        if base.sequence.timeSignature is not None:
            beat_count = base.sequence.timeSignature.numerator
        else:
            beat_count = 4

        for p in base.sequence.parts:
            for n in p.notes:
                beat = int(n.offset) % beat_count
                relative_offset = float(n.offset % 1)
                closest_allowed_offset = find_closest(control.analysis[note_offsets_per_beat.__name__][beat], relative_offset)
                n.offset = int(n.offset) + closest_allowed_offset
        
        # Handle Overlaps
        for p in base.sequence.parts:
            taken_offsets = []
            for n in p.notes:
                if n.offset in taken_offsets:
                    idx = p.index(n)
                    p.pop(idx)
                else:
                    taken_offsets.append(n.offset)
        
 
        t2 = time.time()
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, base.sequence, {})