from typing import List
from pretty_midi import PrettyMIDI
from ipywidgets import Output
from pypianoroll import Multitrack
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
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
    
    if names is None:
        names = []
        for i in range(0, len(evaluation_data)):
            names.append('Similarity of Sequence' + str(i+1))

    fig = __create_evaluation_bar_fig(evaluation_data, names, color)

    if out is None:
        fig = go.Figure(fig)
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)

# CHECK could abstract to x plots (list with data, nameslist, title) -> for loop, create row for each
def two_multibar_plots(left_data: list, left_names: List[str], left_title: str, right_data: list, right_names: List[str], right_title: str, headline: str = None, out: Output = None):
    fig = make_subplots(rows=1, cols=2, subplot_titles=[left_title, right_title])

    left_fig = __create_evaluation_bar_fig(left_data, left_names)
    fig.add_trace(
        left_fig,
        row=1, col=1
    )

    right_fig = __create_evaluation_bar_fig(right_data, right_names)
    fig.add_trace(
        right_fig,
        row=1, col=2
    )

    if headline is not None:
        fig.update_layout(title_text=headline)

    if out is None:
        fig = go.Figure(fig)
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)


def __create_evaluation_bar_fig(data: list, names: list, color: list = None):
    data = []
    
    i = 0
    for values in data:
        df = pd.DataFrame(values, index=['distance']).T
        df['distance'] = pd.to_numeric(df['distance'], downcast='float')

        name = names[i]

        if color is None:
            bar = go.Bar(x=df.index, y=df['distance'], name=name)
        else:
            bar = go.Bar(x=df.index, y=df['distance'], name=name, marker_color=color[i % len(color)])
        data.append(bar)
        i += 1

    fig = go.Figure(data=data)
    fig.update_layout(barmode='group')

    return fig