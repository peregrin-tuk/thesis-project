from src.db import reference_sets as ref_db
from pretty_midi import PrettyMIDI
from visual_midi.visual_midi import Plotter
from src.io.conversion import pretty_midi_to_music21
import plotly.express as px


def pianoRoll(midi: PrettyMIDI):
    """
    docstring
    """
    stream = pretty_midi_to_music21(midi)
    return stream.plot()


def evaluation_radar(evaluation_values):
    pass
    # delete # df = ref_db.ref_set_stats_to_dataframe(1).T
    # fig = px.line_polar(df, r='0.5', theta=df.index, line_close=True)