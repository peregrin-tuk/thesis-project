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

        # CHECK maybe shift this + creation of allowed offset list to input analysis
        if base.sequence.timeSignature is not None:
            beat_count = base.sequence.timeSignature.numerator
        else:
            beat_count = 4

        bar_count = round( float(control.sequence.duration.quarterLength) / beat_count )
        allowed_offsets = []

        # create list with allowed offsets
        beat = 0
        for beat_set in control.analysis[note_offsets_per_beat.__name__]:
            for relative_offset in beat_set:
                for i in range(0, bar_count):
                    allowed_offsets.append(i*beat_count + beat + relative_offset)
            beat += 1
        allowed_offsets.sort()

        # change offsets to closests allowed
        for p in base.sequence.parts:
            for n in p.notes:
                offset = float(n.offset)
                closest_allowed_offset = find_closest(allowed_offsets, offset)
                n.offset = closest_allowed_offset

        
        # Spread simultaneous notes
        # print("### Spread notes with same offset ###")
        for p in base.sequence.parts:
            notes_to_delete = []
            taken_offsets = []
            for index, note in enumerate(p.notes):
                offset = float(note.offset)
                # print("note " + str(index) + " - offset " + str(offset))
                rounding_temp = find_closest(allowed_offsets, offset)
                offset_idx = allowed_offsets.index(rounding_temp)
                for other in p.notes[index+1:]:
                    if float(other.offset) == offset:
                        if allowed_offsets[offset_idx-1] not in taken_offsets:
                            note.offset = allowed_offsets[offset_idx-1]
                            # print("# note " + str(p.index(note)-1) + " moved left to offset " + str(float(note.offset)))
                            # print(float(p.notes[p.index(note)-1].offset))
                        elif offset_idx < len(allowed_offsets) - 1 and allowed_offsets[offset_idx+1] not in taken_offsets:
                            other.offset = allowed_offsets[offset_idx+1]
                            taken_offsets.append(other.offset)
                            # print("# note " + str(p.index(other)-1) + " moved right to offset " + str(float(other.offset)))
                            # print(p.notes[p.index(other)-1].offset)
                        else:
                            notes_to_delete.append(other)
                            # print("# note " + str(p.index(other)-1) + " offset " + str(float(other.offset)) + " added to remove list.")
                taken_offsets.append(note.offset)
            p.remove(notes_to_delete)


        # shorten note length of overlapping notes
        for p in base.sequence.parts:
            p = p.sorted
            # for n in p.notes:
            for index, note in enumerate(p.notes.elements):
                if index < (len(p.notes.notes) - 1):
                    next_offset = p.notes.elements[index+1].offset
                if index < (len(p.notes.notes) - 1) and note.offset + note.quarterLength > next_offset and next_offset > note.offset:
                    note.quarterLength = next_offset - note.offset
                    # print('# new length for note ' + str(index) + ': ' + str(note.quarterLength))
 
        t2 = time.time()
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, base.sequence, {})
