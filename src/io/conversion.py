import muspy
import music21
import mido
import pretty_midi
from pretty_midi import PrettyMIDI
from note_seq import NoteSequence, note_sequence_to_pretty_midi, midi_to_note_sequence

from music21.stream import Score, Part, Stream
from music21.tempo import MetronomeMark
from music21.pitch import Pitch
from music21.key import Key
from music21.note import Note


### UTILS

def _seconds_to_quarterLength(seconds: float, qpm: int):
    return seconds * qpm / 60.0

def _quarterLength_to_seconds(quarterLength: float, qpm: int):
    return quarterLength * 60.0 / qpm



### NoteSequence <-> Music21
def note_seq_to_music21(melody: NoteSequence):
    midi = note_sequence_to_pretty_midi(melody)
    return pretty_midi_to_music21(midi)

def music21_to_note_seq(melody: music21.stream.Stream):
    midi = music21_to_pretty_midi(melody)
    return midi_to_note_sequence(midi)


### PrettyMIDI <-> Mido
def mido_to_pretty_midi(melody: mido.MidiFile):
    tmp = muspy.from_mido(melody)
    tmp.resolution = melody.ticks_per_beat
    pm = muspy.to_pretty_midi(tmp)
    bpm = pm.get_tempo_changes()[1][0]
    track_id = 0
    for inst in pm.instruments:
        note_id = 0
        for note in inst.notes:
            muspy_note = tmp.tracks[track_id].notes[note_id]
            # note.start = pm.tick_to_time(muspy_note.time)
            # note.end = pm.tick_to_time(muspy_note.time + muspy_note.duration)
            note.start = mido.tick2second(muspy_note.time, melody.ticks_per_beat, mido.bpm2tempo(bpm))
            note.end = mido.tick2second(muspy_note.time + muspy_note.duration, melody.ticks_per_beat, mido.bpm2tempo(bpm))
            note_id += 1
        track_id += 1
    return pm

def pretty_midi_to_mido(melody: PrettyMIDI):
    tmp = muspy.from_pretty_midi(melody)
    tmp.resolution = melody.resolution
    return muspy.to_mido(tmp)


### PrettyMIDI <-> NoteSequence
def pretty_midi_to_note_seq(melody: PrettyMIDI):
    return midi_to_note_sequence(melody)

def note_seq_to_pretty_midi(melody: NoteSequence):
    return note_sequence_to_pretty_midi(melody)


### PrettyMIDI --> Music21
def pretty_midi_to_music21(midi: PrettyMIDI):
    '''
    Note: Does currently not support multiple tempo changes

    '''

    # Create a new score
    score = Score()

    # Tracks
    for track in midi.instruments:
        # Create a new part
        part = Part()
        part.partName = track.name

        # Find instrument
        try:
            inst = music21.instrument.instrumentFromMidiProgram(4)
        except music21.exceptions21.InstrumentException:
            inst = music21.instrument.instrumentFromMidiProgram(0)
        part.instrument = inst

        # Tempo
        tempi = midi.get_tempo_changes()
        for time, tempo in zip(tempi[0], tempi[1]):
            metronome = MetronomeMark(number=tempo)
            metronome.offset = _seconds_to_quarterLength(time, tempo)
            part.append(metronome)

            qpm = tempo # to support multiple tempo changes make this a list and save time + tempo for later offset calculations
            break # to support multiple tempo changes this has to be removed
        
        # Key Signatures
        for key in midi.key_signature_changes:
            pitch = Pitch(key.key_number % 12)
            mode = 'major' if key.key_number < 12 else 'minor'
            key21 = Key(pitch, mode)
            key21.offset = _seconds_to_quarterLength(key.time, qpm)
            part.append(key21)

        # Time Signatures
        for ts in midi.time_signature_changes:
            ts21 = music21.meter.TimeSignature()
            ts21.numerator = ts.numerator
            ts21.denominator = ts.denominator
            ts21.offset = _seconds_to_quarterLength(ts.time, qpm)
            part.append(ts21)

        # Add Notes to Part
        for note in track.notes:
            note21 = Note(_get_pitch_name(note.pitch))
            note21.quarterLength = _seconds_to_quarterLength(note.get_duration(), qpm)
            note21.volume = note.velocity
            part.append(note21)
            part.notes[-1].offset = _seconds_to_quarterLength(note.start, qpm)

        score.append(part)
        score.makeMeasures()
    
    return score


### Music21 --> PrettyMIDI
def music21_to_pretty_midi(stream: Stream, resolution: int = 480):
    '''
    Note: 
    - Converts all features that could have previously been converted from PrettyMIDI to a music21 stream.
      Does not support advanced features of music21 such as note ties etc.
    - In PrettyMIDI, tempo changes are read-only and cannot be set manually, therefore only the first MetronomeMark is considered for the conversion and the tempo will stay the same for the whole sequence.

    '''
    # Get initial tempo and create PrettyMIDI object
    if len(stream.flat.metronomeMarkBoundaries()) > 0:
        initial_tempo = stream.flat.metronomeMarkBoundaries()[0][2].number
    else:
        initial_tempo = 120

    midi = PrettyMIDI(resolution=resolution, initial_tempo=initial_tempo)


    # Tracks
    for part in stream.parts:

        # Create Instrument
        if part.instrument.midiProgram is not None:
            program = part.instrument.midiProgram
        else:
            program = 0

        if part.instrument.midiChannel is not None:
            is_drum = part.instrument.midiChannel == 10
        else:
            is_drum = False

        instrument = pretty_midi.Instrument(program, is_drum, part.partName)


        # iterate over elements in part
        for el in part.secondsMap:

            # Add notes to instrument
            if isinstance(el['element'], Note):
                note = pretty_midi.Note(el['element'].volume.velocity, int(el['element'].pitch.ps), el['offsetSeconds'], el['endTimeSeconds'])
                instrument.notes.append(note)

            # Key Signatures
            elif isinstance(el['element'], music21.key.Key):
                ks = pretty_midi.KeySignature(el['element'].getTonic().ps, el['offsetSeconds'])
                midi.key_signature_changes.append(ks)

            # Time Signatures
            elif isinstance(el['element'], music21.meter.TimeSignature):
                ts = pretty_midi.TimeSignature(el['element'].numerator, el['element'].denominator, el['offsetSeconds'])
                midi.time_signature_changes.append(ts)

        midi.instruments.append(instrument)

    return midi





# CHECK legacy code, not used anymore in application code - delete?

###################################
###    MONKEY PATCH for muspy   ###
###################################


PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def _get_pitch_name(note_number: int) -> str:
    octave, pitch_class = divmod(note_number, 12)
    return PITCH_NAMES[pitch_class] + str(octave - 1)

def _patched_to_music21(music: muspy.Music):

    # Create a new score
    score = music21.stream.Score()

    # Tracks
    for track in music.tracks:
        # Create a new part
        part = music21.stream.Part()
        part.partName = track.name

        # Add tempos
        for tempo in music.tempos:
            part.append(muspy.outputs.music21.to_music21_metronome(tempo))

        # Add time signatures
        for time_signature in music.time_signatures:
            part.append(muspy.outputs.music21.to_music21_time_signature(time_signature))

        # Add key signatures
        for key_signature in music.key_signatures:
            part.append(muspy.outputs.music21.to_music21_key(key_signature))

        # Add notes to part - patched
        for note in track.notes:
            m21_note = music21.note.Note(_get_pitch_name(note.pitch))
            m21_note.quarterLength = note.duration / (float) (music.resolution)
            m21_note.volume = note.velocity
            part.append(m21_note)
            part.notes[-1].offset = note.time / (float) (music.resolution)

        # Append the part to the score
        score.append(part)

        # Make measures
        score.makeMeasures()

        return score

muspy.to_music21 = _patched_to_music21
