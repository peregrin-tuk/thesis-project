from typing import List
from ipywidgets.widgets.widget_output import Output

import music21
from IPython.display import display, Audio, FileLink
from pretty_midi import PrettyMIDI
from visual_midi import Plotter, Preset
from note_seq import NoteSequence, note_sequence_to_pretty_midi
from src.io.conversion import pretty_midi_to_music21



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


def play_button(midi: PrettyMIDI, out: Output = None):
    """
    docstring
    """
    if midi is not None:
        if out is None:
            display(Audio(midi.fluidsynth(fs=16000), rate=16000))
        else:
            with out:
                display(Audio(midi.fluidsynth(fs=16000), rate=16000))
        
    else:
        print('[IO] Output error: The midi object is empty.')

def playStream(stream: music21.stream.Stream):
    """
    docstring
    """
    sp = music21.midi.realtime.StreamPlayer(stream)
    sp.play()

def playPrettyMidi(midi: PrettyMIDI):
    """
    docstring
    """
    stream = pretty_midi_to_music21(midi)
    sp = music21.midi.realtime.StreamPlayer(stream)
    sp.play()


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