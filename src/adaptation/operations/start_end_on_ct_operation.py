import time

from src.adaptation.abstract_adaptation_operation import AbstractAdaptationOperation
from src.datatypes.melody_data import AdaptationMelodyData

from src.utils.melodies import find_closest
from src.analysis.harmonic import key
from src.analysis.melodic import pitch_span

class StartAndEndOnCTOperation(AbstractAdaptationOperation):
    """Creates a chord based on the estimated key of the control sequence and transposes the first and last note of the base sequence so they are chord tones (e.g. 'c', 'e' or 'g' for a C major chord)."""

    def __init__(self):
        super().__init__()
        self.required_analysis = { key }


    def execute(self, base: AdaptationMelodyData, control: AdaptationMelodyData):
        t1 = time.time()

        control_key = control.analysis[key.__name__]
        base_span = pitch_span(base.sequence)

        # get the chord of the control_key at a range around the span of the base sequence
        # NOTE: if instead just root and fifth should be used [control_key.getTonic().name, control_key.getDominant().name] would do and the first line of this segment could be deleted
        chord = control_key.getChord(control_key.getTonic())
        scale = control_key.getChord(base_span[0].transpose(-5), base_span[1].transpose(5))
        chord_pitches = [note.pitch.ps for note in scale if note.pitch.name in (chord.root().name, chord.third.name, chord.fifth.name)] 

        # calculate the closest chord tone for the first and the last note
        notes = base.sequence.flat.notes
        print('CHORD', chord)
        print('CHORD PITCHES', chord_pitches)

        first_ps = find_closest(chord_pitches, notes[0].pitch.ps)
        last_ps = find_closest(chord_pitches, notes[-1].pitch.ps)

        adapted_sequence= base.sequence
        adapted_sequence.flat.notes[0].pitch.ps = first_ps
        adapted_sequence.flat.notes[-1].pitch.ps = last_ps

        t2 = time.time()
        base_analysis = { pitch_span.__name__: base_span }
        return super().create_meta_and_update_base(base, self.__class__.__name__, t2-t1, adapted_sequence, base_analysis)