from typing import List

import numpy as np
from pathlib import Path
from pretty_midi import PrettyMIDI
from sklearn.model_selection import LeaveOneOut
from note_seq import NoteSequence, note_sequence_to_pretty_midi, note_sequence_to_midi_file
import midi

from definitions import ROOT_DIR
from src.io.output import saveMidiFile
from dependencies.mgeval import core, utils


midi_file_cache = str(ROOT_DIR / Path('midi\\tmp\\mgeval_cache.mid'))

###############################
###      FULL ANALYSIS      ###
###############################

def analyze_sequence(note_seq: NoteSequence, length_in_bars: int = None):
    note_sequence_to_midi_file(note_seq, midi_file_cache)

    feature = {'pretty_midi': note_sequence_to_pretty_midi(note_seq),
               'midi_pattern': midi.read_midifile(midi_file_cache)}
    bpm = note_seq.tempos[0].qpm if note_seq.tempos[0].qpm != 0 else 120
    return __analyze(feature, bpm, length_in_bars)


def analyze_pretty_midi(pm: PrettyMIDI, length_in_bars: int = None):
    saveMidiFile(pm, midi_file_cache, log=False)

    feature = {'pretty_midi': pm,
               'midi_pattern': midi.read_midifile(midi_file_cache)}
    tempo_list = feature['pretty_midi'].get_tempo_changes()
    bpm = next((i for i, x in enumerate(tempo_list) if x != 0), 120)
    return __analyze(feature, bpm, length_in_bars)


def analyze_midi_file(midi_file: str, length_in_bars: int = None):
    feature = core.extract_feature(midi_file)
    tempo_list = feature['pretty_midi'].get_tempo_changes()
    bpm = next((i for i, x in enumerate(tempo_list) if x != 0), 120)
    return __analyze(feature, bpm, length_in_bars)



def __analyze(feature, bpm: int, length_in_bars: int = None, normalize: bool = False):
    try:
        feature['pretty_midi'].instruments[0]
    except IndexError:
        print('[EVAL] Error: Midi file is empty and can not be analyzed')
        return None

    metrics = core.metrics()

    return {
        'pitch_count': metrics.total_used_pitch(feature),
        # 'pitch_count_per_bar': metrics.bar_used_pitch(feature, 1, length_in_bars), # CHECK calculation in core seems to return wrong results
        'pitch_class_histogram': metrics.total_pitch_class_histogram(feature),
        # 'pitch_class_histogram_per_bar': metrics.bar_pitch_class_histogram(feature, 0, bpm, length_in_bars), # CHECK only works when length in bars is given, should have reliable calculation here
        'pitch_class_transition_matrix': metrics.pitch_class_transition_matrix(feature),
        'avg_pitch_interval': metrics.avg_pitch_shift(feature),
        'pitch_range': metrics.pitch_range(feature),

        'note_count': metrics.total_used_note(feature),
        # 'note_count_per_bar': metrics.bar_used_note(feature, 1, length_in_bars), # CHECK calculation in core seems to return wrong results
        'note_length_histogram': metrics.note_length_hist(feature, pause_event=True),
        'note_length_transition_matrix': metrics.note_length_transition_matrix(feature, pause_event=True),
        'avg_ioi': metrics.avg_IOI(feature),
    }


###############################
###   DISTANCE CALCULATION  ###
###############################

def calc_distances(metrics1: dict, metrics2: dict):
    distances = {}

    for key in metrics1:
        distances[key] = np.linalg.norm(metrics1[key] - metrics2[key])
    return distances


def calc_intra_set_distances(set_of_sequences: List[dict]):
    set_of_sequences = __list_of_dicts_to_dict_of_lists(set_of_sequences)
    max_key = max(set_of_sequences, key= lambda x: len(set(set_of_sequences[x])))

    num_samples = len(set_of_sequences[max_key])
    num_metrics = len(set_of_sequences)

    loo = LeaveOneOut()
    loo.get_n_splits(np.arange(num_samples))
    intra_set_distances = np.zeros((num_samples, num_metrics, num_samples-1))

    i = 0
    for key in set_of_sequences:
        for train_indexes, test_index in loo.split(np.arange(num_samples)):
            x = utils.c_dist(np.array(set_of_sequences[key])[test_index], np.array(set_of_sequences[key])[train_indexes])
            intra_set_distances[test_index[0]][i] = x
        i += 1
        
    return intra_set_distances



    loo = LeaveOneOut()
    loo.get_n_splits(np.arange(len(set_of_sequences)))
    intra_set_distances = np.zeros((len(set_of_sequences), len(set_of_sequences[0]), len(set_of_sequences)-1))
    i = 0
    for key in set_of_sequences[0]:
        for train_index, test_index in loo.split(np.arange(len(set_of_sequences))):
            x = utils.c_dist(set_of_sequences[test_index][key], set_of_sequences[train_index][key])
            intra_set_distances[test_index[0]][i] = x
        i += i

    return intra_set_distances



###############################
###        UTILITIES        ###
###############################

def __list_of_dicts_to_dict_of_lists(sequences: List[dict]):
    result = {}
    for dictionary in sequences:
        for key, value in dictionary.items():
            if key not in result.keys():
                result[key] = []
            result[key].append(value)
    return result