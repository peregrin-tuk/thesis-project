import muspy
import music21
import mido
from pretty_midi import PrettyMIDI
from note_seq import NoteSequence, note_sequence_to_pretty_midi, midi_to_note_sequence

#   PrettyMIDI <-> Music21
def pretty_midi_to_music21(melody: PrettyMIDI):
    tmp = muspy.from_pretty_midi(melody)
    return muspy.to_music21(tmp)

def music21_to_pretty_midi(melody: music21.stream.Stream):
    tmp = muspy.from_music21(melody)
    return muspy.to_pretty_midi(tmp)


#   NoteSequence <-> Music21
def note_seq_to_music21(melody: NoteSequence):
    midi = note_sequence_to_pretty_midi(melody)
    tmp = muspy.from_pretty_midi(midi)
    return muspy.to_music21(tmp)

def music21_to_note_seq(melody: music21.stream.Stream):
    tmp = muspy.from_music21(melody)
    midi = muspy.to_pretty_midi(tmp)
    return midi_to_note_sequence(midi)


#   PrettyMIDI <-> Mido
def mido_to_pretty_midi(melody: mido.MidiFile):
    tmp = muspy.from_mido(melody)
    return muspy.to_pretty_midi(tmp)

def pretty_midi_to_mido(melody: PrettyMIDI):
    tmp = muspy.from_pretty_midi(melody)
    return muspy.to_mido(tmp)


#   PrettyMIDI <-> NoteSequence
def pretty_midi_to_note_seq(melody: PrettyMIDI):
    return midi_to_note_sequence(melody)

def note_seq_to_pretty_midi(melody: NoteSequence):
    return note_sequence_to_pretty_midi(melody)