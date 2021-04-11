from pretty_midi import PrettyMIDI
from ipywidgets import Output
from pypianoroll import Multitrack
from visual_midi.visual_midi import Plotter
import plotly.express as px
from src.io.conversion import pretty_midi_to_music21, pretty_midi_to_pianoroll_track



def pianoRoll_music21(midi: PrettyMIDI, out: Output = None):
    """
    docstring
    """
    stream = pretty_midi_to_music21(midi)
    if out is None:
        stream.plot()
    else:
        with out:
            stream.plot()


def pianoroll(midi: PrettyMIDI, out: Output = None, args: dict = None):
    """
    docstring
    """
    track = pretty_midi_to_pianoroll_track(midi)
    if args is None:
        args = {'xtick': 'beat', 'resolution': 100, 'ytick': 'octave'}

    if out is None:
        track.plot(**args)
    else:
        with out:
            track.plot(**args)

def multitrack_pianoroll(midis: list, names: list = None, out: Output = None, args: dict = None):
    """
    Takes a list of single track pretty midi objects, converts them to a pypianoroll Mutlitrack objects and plots the resulting object.
    The resolution o

    Args:
        midis: list of pretty midi objects with one track each
        names: list of strings, one corresponding to each midi track
        out: ipywidget.Output object to which the plot shall be printed
        args: dict of optional args passed to the plotter
    """
    tracks = []
    print('midis', midis)
    print('names', names)
    for name, midi in zip(names, midis):
        track = pretty_midi_to_pianoroll_track(midi)
        if name is not None:
            track.name = name
        tracks.append(track)

    multitrack = Multitrack(name='Multitrack', resolution=100, tracks=tracks)
    if args is None:
        args = {'xtick': 'beat', 'ytick': 'octave'}

    if out is None:
        multitrack.plot(**args)
    else:
        with out:
            multitrack.plot(**args)


def evaluation_radar(evaluation_values, out: Output = None):
    # delete # df = ref_db.ref_set_stats_to_dataframe(1).T
    # fig = px.line_polar(df, r='0.5', theta=df.index, line_close=True)

    if out is None:
        pass
    else:
        with out:
            pass