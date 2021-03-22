import numpy as np

from pretty_midi.pretty_midi import PrettyMIDI
from src.utils.melodies import get_pitch_class


# RATINGS

stability = (6, 2, 4, 2, 5, 4, 2, 5, 2, 4, 2, 4, 6) # index = pitch relative to root note
proximity = (24, 36, 32, 25, 20, 16, 12, 9, 6, 4, 2, 1, 0.25) # index = interval in semitones; mobility factor (* 2/3 for repetition) is already included at index 0
direction_continuation = (6, 20, 12, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0) # index = previous interval in semitones
direction_reversal = (0, 0, 0, 0, 0, 6, 12, 25, 36, 52, 75, 75, 75) # index = previous interval in semitones



def calc_expectancy_rating_for_pitch(candidate: int, prev: int, prevprev: int, single_ratings = False):
    
    prev_interval = abs(prev-prevprev)
    current_interval = abs(candidate-prev)
    prev_direction = np.sign(prev-prevprev)
    current_direction = np.sign(candidate-prev)

    # cap intervals at 12
    prev_interval = prev_interval if prev_interval <= 12 else 12
    current_interval = current_interval if current_interval <= 12 else 12

    # calculate whether the current direction is a continuation
    continuation = current_direction != 0 and current_direction == prev_direction

    s = stability[get_pitch_class(candidate)]
    p = proximity[current_interval]
    d = direction_continuation[prev_interval] if continuation else direction_reversal[prev_interval]

    if current_direction == 0:
        d /= 3

    if prev == 11 and candidate == 9:
        s = 6

    if single_ratings:
        return s, p, d
    else:
        return (s * p) + d

def get_expectancy_ratings_for_sequence(melody: PrettyMIDI):
    track = melody.instruments[0]
    expectancy_ratings = [None, None] #  Expectancy cannot be calcualted for the first 2 notes in a melody

    # iterate over all notes except for the first 2
    for n in range(2,len(track.notes)):
        pitch = track.notes[n].pitch
        prev_pitch = track.notes[n-1].pitch
        prevprev_pitch = track.notes[n-2].pitch
        e = calc_expectancy_rating_for_pitch(pitch, prev_pitch, prevprev_pitch)
        expectancy_ratings.append(e)

    return expectancy_ratings
