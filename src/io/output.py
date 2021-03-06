# general class for all types of output OR should visual/auditive/file output be separated?

# GLOBAL VARS
# default_path
# midi_output_path
# audio_output_path ?
# evaluation_ ?
# playback_device
# midi_output_port

# FUNCTIONS FILE OUTPUT ( exports )
# ✔ exportMIDI(internal midi datastructure, string: path = default, string: file_name)
    #  if path == undefined, use default path (but then default path must ALWAYS be defined - e.g. in constructor of output class)
# exportOTHERTYPE etc.

# FUNCTIONS LIVE OUTPUT
# ✔ playMIDI(data, instrument = default, volume = default)   
    #  // should that maybe go to midi class OR midi_output analogue to midi_input ?
    #  rename to playAudio(mididata) and also provide playAudio(audiodata) ?
    #  playPureMidi() & playExpressiveMidi ?  => now only implement pure, but expressive would be interesting for Call-Response output
# ✔ showPianoRoll(data, settings?)
    #  // using bokeeh or magenta output
# showMetaData()
    #  for testing and evaluation
# sendMidiToDevice(port = default, mididata)
    # sends timed midi events to external device (e.g. to support output via my Roland Piano or Bösendorfer CEUS)


# maybe also add scheduled playAudio and sendMidi functions

from typing import List

from IPython.display import display, Audio, FileLink
from pretty_midi import PrettyMIDI
from visual_midi import Plotter, Preset
from note_seq import NoteSequence, note_sequence_to_pretty_midi



def pianoRoll(midi: PrettyMIDI):
    """
    docstring
    """
    plotter = Plotter(show_velocity=True)
    plotter.show_notebook(midi)


def pianoRollFromNoteSeq(note_seq: NoteSequence):
    """
    docstring
    """
    pm = note_sequence_to_pretty_midi(note_seq)
    pianoRoll(pm)


def pianoRollGrid(midis: List[PrettyMIDI]):
    preset = Preset(plot_width=500, plot_height=300)
    for midi in midis:
        plotter = Plotter(preset, show_velocity=True)
        plotter.show_notebook(midi)


def pianoRollGridFromNoteSeq(note_seqs: List[NoteSequence]):
    pms = []
    for note_seq in note_seqs:
        pms.append(note_sequence_to_pretty_midi(note_seq))
    pianoRollGrid(pms)


def pianoRollToHTML(midi: PrettyMIDI, html_file_path: str):
    """
    docstring
    """
    plotter = Plotter()
    plotter.show(midi, html_file_path)


def synthesizeMidi(midi: PrettyMIDI):
    """
    docstring
    """
    if midi is not None:
        display(Audio(midi.fluidsynth(fs=16000), rate=16000))
    else:
        print('[IO] Output error: The midi object is empty.')


def saveMidiFile(midi: PrettyMIDI, file_path: str, log: bool = True):
    """
    docstring
    """
    midi.write(file_path)
    if log: print('[IO] file saved to:')
    if log: showFileLink(file_path)

def saveNoteSeqToMidiFile(note_seq: NoteSequence, file_path: str):
    """
    docstring
    """
    midi = note_sequence_to_pretty_midi(note_seq)
    midi.write(file_path)
    print('[IO] file saved to:')
    showFileLink(file_path)


def showFileLink(file_path: str):
    """
    docstring
    """
    try:
        display(FileLink(file_path))
    except TypeError:
        print('[IO] Output error: The path must be a string')