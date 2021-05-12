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

        bar_count = round( float(control.sequence.duration.quarterLength) / beat_count )
        allowed_offsets = []

        beat = 0
        for beat_set in control.analysis[note_offsets_per_beat.__name__]:
            for relative_offset in beat_set:
                for i in range(0, bar_count):
                    allowed_offsets.append(i*beat_count + beat + relative_offset)
            beat += 1
        allowed_offsets.sort()

        for p in base.sequence.parts:
            for n in p.notes:
                offset = float(n.offset)
                closest_allowed_offset = find_closest(allowed_offsets, offset)
                n.offset = closest_allowed_offset

        # for p in base.sequence.parts:
        #     for n in p.notes:
        #         beat = int(n.offset) % beat_count
        #         relative_offset = float(n.offset % 1)
        #         closest_allowed_offset = find_closest(control.analysis[note_offsets_per_beat.__name__][beat], relative_offset)
        #         n.offset = int(n.offset) + closest_allowed_offset
        
        # Spread simultaneous notes
        for p in base.sequence.parts:
            taken_offsets = []
            for n in p.notes:
                offset = float(n.offset)
                if offset in taken_offsets:
                    note_idx = p.index(n)
                    offset_idx = allowed_offsets.index(offset)
                    if allowed_offsets[offset_idx-2] not in taken_offsets:
                        p.notes[note_idx-1].offset = allowed_offsets[offset_idx-2]
                        taken_offsets.append(n.offset)
                    elif offset_idx < len(allowed_offsets) - 1 and allowed_offsets[offset_idx+1] not in taken_offsets:
                        n.offset = allowed_offsets[offset_idx+1]
                        taken_offsets.append(n.offset)
                    else:
                        p.pop(note_idx)
                else:
                    taken_offsets.append(n.offset)

        # shorten note length of overlapping notes
        for p in base.sequence.parts:
            print('part length', len(p.notes.notes))
            # for n in p.notes:
            for i in range(0, len(p.notes.elements)):
                n = p.notes.elements[i]
                note_idx = i
                print('----------')
                print('note index', note_idx)
                print('offset', n.offset)
                print('length', n.quarterLength)
                if note_idx < (len(p.notes.notes) - 1): print('next offset', p.notes.elements[note_idx].offset)
                if note_idx < (len(p.notes.notes) - 1) and n.offset + n.quarterLength > p.notes.elements[note_idx+1].offset:
                    n.quarterLength = p.notes[note_idx+1].offset - n.offset
                    print('new length for note ' + str(note_idx) + ': ' + str(n.quarterLength))
        
 
        t2 = time.time()
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, base.sequence, {})