from pretty_midi import PrettyMIDI
from ipywidgets import Output
from pypianoroll import Multitrack
import pandas as pd
import plotly.express as px
from plotly.offline import iplot, init_notebook_mode
import plotly.graph_objects as go
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
    df = pd.DataFrame(evaluation_values, index=['distance']).T
    fig = px.line_polar(df, r='distance', theta=df.index, line_close=True)

    if out is None:
        fig.show()
    else:
        with out:
            iplot([fig]) # TODO doesn't work that way


def evaluation_bars(evaluation_values, out: Output = None, color: str = 'lightseagreen'):
    df = pd.DataFrame(evaluation_values, index=['distance']).T
    df['distance'] = pd.to_numeric(df['distance'], downcast='float')
    fig = go.Bar(x=df.index, y=df['distance'], marker_color=color)

    if out is None:
        fig = go.Figure([fig])
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot([fig])

def multi_evaluation_bars(evaluation_data: list, out: Output = None, names: list = None, color: list = None):
    
    data = []
    
    i = 0
    for values in evaluation_data:
        df = pd.DataFrame(values, index=['distance']).T
        df['distance'] = pd.to_numeric(df['distance'], downcast='float')

        if names is None:
            name = 'Similarity of Sequence' + str(i+1)
        else:
            name = names[i]

        if color is None:
            bar = go.Bar(x=df.index, y=df['distance'], name=name)
        else:
            bar = go.Bar(x=df.index, y=df['distance'], name=name, marker_color=color[i % len(color)])
        data.append(bar)
        i += 1

    fig = go.Figure(data=data)
    fig.update_layout(barmode='group')

    if out is None:
        fig = go.Figure(fig)
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)

