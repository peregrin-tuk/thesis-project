from pprint import pprint
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


###############################
###      OLD PIANOROLLS     ###
###############################

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

###############################
###     EVALUATION BARS     ###
###############################

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

    traces = __create_evaluation_bar_traces(evaluation_data, names, color)

    fig = go.Figure(data=traces)
    fig.update_layout(barmode='group')

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

    left_traces = __create_evaluation_bar_traces(left_data, left_names)
    for trace in left_traces:
        fig.add_trace(
            trace,
            row=1, col=1
        )

    right_traces = __create_evaluation_bar_traces(right_data, right_names) 
    for trace in right_traces:
        fig.add_trace(
            trace,
            row=1, col=2
        )

    # TODO Test
    fig.update_yaxes(matches='y')

    if headline is not None:
        fig.update_layout(title_text=headline)

    if out is None:
        fig = go.Figure(fig)
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)


def __create_evaluation_bar_traces(data: list, names: list, color: list = None):
    traces = []
    
    i = 0
    for values in data:
        df = pd.DataFrame(values, index=['distance']).T
        df['distance'] = pd.to_numeric(df['distance'], downcast='float')

        name = names[i]

        if color is None:
            traces.append(go.Bar(x=df.index, y=df['distance'], name=name))
        else:
            traces.append(go.Bar(x=df.index, y=df['distance'], name=name, marker_color=color[i % len(color)]))
        i += 1

    return traces


###############################
###     CUSTOM PIANOROLL    ###
###############################

def plotly_pianoroll(sequence: PrettyMIDI, title: str = None, out: Output = None, pitch_range: List[int] = None, args: dict = None):

    px._core.process_dataframe_timeline = my_process_dataframe_timeline_patch

    # pretty midi to dataframe
    df = pd.DataFrame(columns=['start', 'end', 'pitch', 'velocity'])
    for i, note in enumerate(sequence.instruments[0].notes):
        df.loc[i] = [note.start, note.end, note.pitch, note.velocity]

    if args is None: args = {}
    fig = px.timeline(df, x_start="start", x_end="end", y="pitch", color="velocity", range_y=pitch_range, range_color=[0, 127], title=title, labels={'pitch': "Pitch", 'velocity': "Velocity"}, **args)
    fig.layout.xaxis.type = 'linear'
    fig.update_yaxes(dtick=1, showgrid=True)
    fig.update_xaxes(title_text='Time in Bars')
    fig.update_traces(width=1)

    if out is None:
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)

# CHECK no funciona! (colors are wrong, items sometimes get incorrect widths, which is strange)
def multitrack_plotly_pianoroll(sequences: List[PrettyMIDI], names: List[str], title: str = None, out: Output = None, pitch_range: List[int] = None, args: dict = None):
    
    px._core.process_dataframe_timeline = my_process_dataframe_timeline_patch

    df = pd.DataFrame(columns=['Sequence', 'Start', 'End', 'Pitch', 'Velocity'])
    i = 0
    for s, sequence in enumerate(sequences):
        for note in sequence.instruments[0].notes:
            df.loc[i] = [names[s], note.start, note.end, note.pitch, note.velocity]
            i += 1

    if args is None: args = {}
    fig = px.timeline(df, facet_row="Sequence", color="Sequence", x_start="Start", x_end="End", y="Pitch", range_y=pitch_range, title=title, height=800, **args)
    fig.layout.xaxis.type = 'linear'
    fig.update_yaxes(dtick=1, showgrid=True)
    fig.update_traces(width=1)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    

    if out is None:
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)



def animated_plotly_pianoroll(sequences: List[PrettyMIDI], step_names: List[str], title: str = None, out: Output = None, pitch_range: List[int] = None, args: dict = None):
    px._core.process_dataframe_timeline = my_process_dataframe_timeline_patch

    df = pd.DataFrame(columns=['step', 'start', 'end', 'pitch', 'velocity'])
    i = 0
    for s, sequence in enumerate(sequences):
        for note in sequence.instruments[0].notes:
            df.loc[i] = [step_names[s], note.start, note.end, note.pitch, note.velocity]
            i += 1

    if args is None: args = {}
    fig = px.timeline(df, animation_frame="step", x_start="start", x_end="end", y="pitch", range_y=pitch_range, title=title, labels={'pitch': "Pitch", 'velocity': "Velocity"}, **args)
    fig.layout.xaxis.type = 'linear'
    fig.update_yaxes(dtick=1, showgrid=True)
    fig.update_xaxes(title_text='Time in Bars')
    fig.update_traces(width=1)

    if out is None:
        fig.show()
    else:
        with out:
            init_notebook_mode()
            iplot(fig)


def my_process_dataframe_timeline_patch(args):
    """
    Massage input for bar traces for px.timeline()
    Allows differnt colors to be used on integer timeline plots such as the piano roll above.
    """
    args["is_timeline"] = True
    if args["x_start"] is None or args["x_end"] is None:
        raise ValueError("Both x_start and x_end are required")

    x_start = args["data_frame"][args["x_start"]]
    x_end = args["data_frame"][args["x_end"]]

    # note that we are not adding any columns to the data frame here, so no risk of overwrite
    args["data_frame"][args["x_end"]] = (x_end - x_start)
    args["x"] = args["x_end"]
    del args["x_end"]
    args["base"] = args["x_start"]
    del args["x_start"]
    return args