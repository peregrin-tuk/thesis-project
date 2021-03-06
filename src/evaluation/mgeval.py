# analysis of midi sequence with mgeval

# NOTE use np arrays for faster calculations afterwards?
# TODO normalize everything?
# TODO create analysis object with methods to nromalize etc? (object orientation always good idea)


# methods:
# analyse_sequence(pretty_midi): dict with all features
# get_pitch_count(pretty_midi): int
#   -> just wrapper around total_used_pitch
# get_pitch_count_per_bar(pretty_midi): list of int
#   -> get num_bars by time signature and tempo etc -> check returned object
# get_pitch_class_histogram(): list of float
# get_pitch_class_histograms_per_bar: np.array ?
#   -> can be normalized using note_count
# get_pitch_class_transition_matrix(): 12x12 n array
#   -> directly use normalized version?
# get_pitch_range(): interval in half tones as int
# get_avg_interval(): float - avg interval between notes

# get_note_count(): int
# get_note_count_per_bar(): list of int
# get_avg_ioi(): float - avg note length as IOI
# get_note_length_histogram(): list of float or int
#   -> TODO with pauses?
# get_note_length_transition_matrix():   12x12 np array
#   -> directly use normalized version? with pauses?

# distance calculations

from typing import List

import midi
import numpy as np
from pretty_midi import PrettyMIDI
from sklearn.model_selection import LeaveOneOut
from note_seq import NoteSequence, note_sequence_to_pretty_midi, note_sequence_to_midi_file
from dependencies.mgeval import core, utils


midi_file_cache = '../midi/tmp/mgeval_cache.mid'


#### FULL ANALYSIS ####

def analyze_sequence(note_seq: NoteSequence):
    note_sequence_to_midi_file(note_seq, midi_file_cache)

    feature = {'pretty_midi': note_sequence_to_pretty_midi(note_seq),
               'midi_pattern': midi.read_midifile(midi_file_cache)}
    bpm = note_seq.tempos[0].qpm
    return __analyze(feature, bpm)


def analyze_midi(midi_file: str):
    feature = core.extract_feature(midi_file)
    bpm = feature['pretty_midi'].get_tempo_changes()[0]
    return __analyze(feature, bpm)


def __analyze(feature, bpm, normalize=False):
    metrics = core.metrics()

    return {
        'pitch_count': metrics.total_used_pitch(feature),
        'pitch_count_per_bar': metrics.bar_used_pitch(feature),
        'pitch_class_histogram': metrics.total_pitch_class_histogram(feature),
        'pitch_class_histogram_per_bar': metrics.bar_pitch_class_histogram(feature, 0, bpm),
        'pitch_class_transition_matrix': metrics.pitch_class_transition_matrix(feature),
        'avg_pitch_interval': metrics.avg_pitch_shift(feature),
        'pitch_range': metrics.pitch_range(feature),

        'note_count': metrics.total_used_note(feature),
        'note_count_per_bar': metrics.bar_used_note(feature),
        'note_length_histogram': metrics.note_length_hist(feature, pause_event=True),
        'note_length_transition_matrix': metrics.note_length_transition_matrix(feature, pause_event=True),
        'avg_ioi': metrics.avg_IOI(feature),
    }


#### DISTANCE CALCULATION ####

def calc_distances(metrics1: dict, metrics2: dict):
    distances = {}

    for key in metrics1:
        distances[key] = np.linalg.norm(metrics1[key] - metrics2[key])
    return distances


def calc_intra_set_distances(set: List[dict]):
    loo = LeaveOneOut()
    loo.get_n_splits(np.arange(len(set)))
    intra_set_distances = np.zeros((len(set), len(set[0]), len(set)-1))
    i = 0
    for key in set[0]:
        for train_index, test_index in loo.split(np.arange(len(set))):
            intra_set_distances[test_index[0]][i] = utils.c_dist(set[test_index][key], set[train_index][key])
        i += i

    return intra_set_distances


#### SINGLE FEATURES ####

def __get_pitch_count(midi: PrettyMIDI):
    pass

def __get_pitch_count_per_bar(midi: PrettyMIDI):
    pass

def __get_pitch_class_histogram(midi: PrettyMIDI):
    pass

def __get_pitch_class_histogram_per_bar(midi: PrettyMIDI):
    pass

def __get_pitch_class_transition_matrix(midi: PrettyMIDI):
    # TODO normalization?
    pass

def __get_avg_pitch_interval(midi: PrettyMIDI):
    pass

def __get_pitch_range(midi: PrettyMIDI):
    # can also be seen from histogram
    pass



def __get_note_count(midi: PrettyMIDI):
    pass

def __get_note_count_per_bar(midi: PrettyMIDI):
    pass

def __get_note_length_histogram(midi: PrettyMIDI):
    pass

def __get_note_length_transition_matrix(midi: PrettyMIDI):
    # TODO normalize?
    pass

def __get_avg_ioi(midi: PrettyMIDI):
    pass

# def get_ioi_range() ?