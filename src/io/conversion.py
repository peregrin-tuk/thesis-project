import muspy
import music21
import mido
from pretty_midi import PrettyMIDI
from note_seq import NoteSequence, note_sequence_to_pretty_midi, midi_to_note_sequence

#   PrettyMIDI <-> Music21
def pretty_midi_to_music21(melody: PrettyMIDI):
    tmp = muspy.from_pretty_midi(melody, melody.resolution)
    return muspy.to_music21(tmp)

def music21_to_pretty_midi(melody: music21.stream.Stream):
    tmp = muspy.from_music21(melody)
    return muspy.to_pretty_midi(tmp)


#   NoteSequence <-> Music21
def note_seq_to_music21(melody: NoteSequence):
    midi = note_sequence_to_pretty_midi(melody)
    tmp = muspy.from_pretty_midi(midi, midi.resolution)
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
    tmp = muspy.from_pretty_midi(melody, melody.resolution)
    return muspy.to_mido(tmp)


#   PrettyMIDI <-> NoteSequence
def pretty_midi_to_note_seq(melody: PrettyMIDI):
    return midi_to_note_sequence(melody)

def note_seq_to_pretty_midi(melody: NoteSequence):
    return note_sequence_to_pretty_midi(melody)




###    MONKEY PATCHES for muspy   ###

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
            m21_note.offset = note.time / (float) (music.resolution)
            m21_note.quarterLength = note.duration / (float) (music.resolution)
            m21_note.volume = note.velocity
            part.append(m21_note)

        # Append the part to the score
        score.append(part)

        # Make measures
        score.makeMeasures()

        return score

muspy.to_music21 = _patched_to_music21


def _from_pretty_midi_wrapper(midi: PrettyMIDI, resolution: int = 480):
    music = muspy.from_pretty_midi(midi, resolution)
    music.resolution  = resolution
    return music

def _patched_from_pretty_midi(midi: PrettyMIDI, resolution: int = None):
    if resolution is None:
        resolution = midi.resolution

    tempo_realtimes, tempi = midi.get_tempo_changes()
    assert len(tempi) > 0

    tempos = [
        muspy.Tempo(time=time, qpm=tempo)
        for time, tempo in zip(tempo_realtimes, tempi)
    ]

    key_signatures = [
        muspy.inputs.midi.from_pretty_midi_key_signature(key_signature)
        for key_signature in midi.key_signature_changes
    ]
    time_signatures = [
        muspy.inputs.midi.from_pretty_midi_time_signature(time_signature)
        for time_signature in midi.time_signature_changes
    ]
    lyrics = [muspy.inputs.midi.from_pretty_midi_lyric(lyric) for lyric in midi.lyrics]
    tracks = [muspy.inputs.midi.from_pretty_midi_instrument(track) for track in midi.instruments]
    music = muspy.Music(
        metadata=muspy.Metadata(source_format="midi"),
        tempos=tempos,
        key_signatures=key_signatures,
        time_signatures=time_signatures,
        lyrics=lyrics,
        tracks=tracks,
    )

    # convert all the timings into metrical timing
    def map_time(time):
        return midi.time_to_tick(time)
    music.adjust_time(func=map_time)

    return music

# muspy.from_pretty_midi = _patched_from_pretty_midi



# use muspy template
# make sure time codes / resolution are correct
# make sure start time is correct
# write velocity into volume

# TODO we probably also need a new music21 to pretty midi
# CHECK + the notesequence to music21 methods should then use this internally
# => muspy will only be left in mido to pretty_midi conversion and in reference data preparation