import os
import logging
import time
from pathlib import Path

import muspy
from tqdm.notebook import tqdm

from src.utils.strings import remove_prefix, remove_suffix


def extract_melodies_to_folder(song: muspy.Music, song_name: str or int, set_name: str, length_in_bars: int):
    """
    Separates a melody track from a Muspy Music object and splits it into call and response pairs.
    The track is selected based on it's name, which must be "melody", "vocals" or "mel" (case insensitive). If no such track is available, 0 is returned.
    If the melody track starts with a pause of multiple bars, those bars are skipped and the splitting into call and response sequences starts with the bar in which the melody starts. Long pauses later in the track are currently ignored.
    The resulting sequences are saved as MIDI files in the following directory: ../data/reference_data/{set_name}/{song_name}/.

    Args:
        song (muspy.Music): A Muspy Music object containing at least one track with melody
        song_name (str or int): The name of the song, will be used to create the folder structure. If no name is available an ID number can be used as well
        set_name (str): Name of the reference data set, will be used as the name for the root folder of the extracted melodies
        length_in_bars (int): How long the extracted sequences shall be. Measured in bars, based on the time signature provided in the muspy.Music object.

    Returns:
        int: count of full call-and-response pairs created if the operation was successful,
             0 if no track was found, 
             -1 if the midi track is not long enough to extract at least one call-and-response pair.
    """

    track = get_melody_track(song.tracks)

    if track is not None:
        end_time = track[-1].time / song.resolution
        quarters_per_bar = song.time_signatures[0].numerator * 4 / song.time_signatures[0].denominator

        # check if track is long enough to extract at least 1 call-and-response pair (>= 2x length of one sequence)
        if round(end_time / quarters_per_bar) >= length_in_bars * 2:
            is_call = True
            count = 1

            time_steps_per_bar = song.resolution * song.time_signatures[0].numerator * 4 / song.time_signatures[0].denominator
            starting_bar = round(track.notes[0].time / time_steps_per_bar)

            starting_time = starting_bar * time_steps_per_bar
            time_marker_start = starting_time
            time_marker_end = time_marker_start + time_steps_per_bar * length_in_bars

            base_path = '../data/reference_data/' + set_name + '/' + str(song_name) + '/'
            Path(base_path).mkdir(parents=True, exist_ok=True)

            excerpt = __create_new_empty_track(song)

            for note in track.notes:
                if (note.time < starting_time):
                    pass
                elif (note.time < time_marker_end):
                    excerpt.tracks[0].append(__extract_note(note, time_marker_start, song.tempos[0].qpm, song.resolution))
                else:
                    if (len(excerpt.tracks[0]) > 0):
                        # save excerpt
                        __save_excerpt(excerpt, base_path, is_call, count)

                        # increase count and toggle call/response
                        if not is_call:
                            count += 1
                        is_call = not is_call

                    # init new one
                    excerpt = __create_new_empty_track(song)

                    # change time markers (move window x bars)
                    time_marker_start = time_marker_end
                    time_marker_end = time_marker_start + time_steps_per_bar * length_in_bars

                    # append current note
                    excerpt.tracks[0].append(__extract_note(note, time_marker_start, song.tempos[0].qpm, song.resolution))

            if is_call:
                return count-1
            else:
                # after all notes were processed, save the last excerpt if it is a response
                # if the last excerpt is a call, it does not have to be saved as it is of no use without a corresponding response sequence
                __save_excerpt(excerpt, base_path, is_call, count)
                return count
        return -1
    return 0


def split_all_midis_from_folder(source_folder, name_for_destination_folder, excerpt_length_in_bars, create_log_file = True):
    song_count = 0
    pair_count = 0
    no_mel = 0
    too_short = 0
    err = 0

    t1 = time.time()
    Path('../data/reference_data/' + name_for_destination_folder).mkdir(parents=True, exist_ok=True)   
    if create_log_file: logging.basicConfig(filename='../data/reference_data/' + name_for_destination_folder + '/call-response-split.log', level=logging.DEBUG)

    for root, dirs, files in tqdm(os.walk(source_folder)):
        for file in files:
            if file.endswith(".mid"):
                try:
                    song = muspy.read(os.path.join(root, file))
                    file_name = remove_prefix(root, source_folder + "\\").replace("\\", "_") + "_" + remove_suffix(remove_suffix(file, ".mid"), "_symbol_key")
                    result = extract_melodies_to_folder(song, file_name, name_for_destination_folder, excerpt_length_in_bars)
                    if (result == 0):  
                        if create_log_file: logging.info("No melody track found for %s", file_name)
                        no_mel += 1
                    elif (result == -1):
                        if create_log_file: logging.info("Track is too short: %s", file_name)
                        too_short += 1
                    else:
                        pair_count += result
                    song_count += 1
                    
                except ValueError as error:
                    if create_log_file: logging.error("The following error occurred while processing %s: %s", file_name, error)

    t2 = time.time()
    if create_log_file:
        logging.info("%s songs processed.", song_count)
        logging.info("%s call-and-response pairs created.", pair_count)
        logging.info("%s songs had no melody track.", no_mel)
        logging.info("%s songs were too short.", too_short)
        logging.info("%s songs could not be processed due to an error.",  err)
        logging.info("Total duration in seconds: %d", (t2-t1))

    print(str(song_count) + " songs processed in " + str(t2-t1) + " seconds.")
    print(str(pair_count) + " call-and-response pairs created.")
    print(str(no_mel) + " songs had no melody track.")
    print(str(too_short) + " songs were too short.")
    print(str(err) + " songs could not be processed due to an error.")


def __extract_note(note, time_marker_start, bpm, resolution):
    note.time = note.time - time_marker_start
    note.time = convert_time_steps_to_seconds(note.time, bpm, resolution)
    note.duration = convert_time_steps_to_seconds(note.duration, bpm, resolution)
    return note


def __create_new_empty_track(song):
    excerpt = muspy.Music()
    excerpt.resolution = song.resolution
    excerpt.tempos.append(song.tempos[0])
    excerpt.time_signatures.append(song.time_signatures[0])
    excerpt_track = muspy.Track()
    excerpt_track.name = 'melody'
    excerpt.append(excerpt_track)
    return excerpt


def __save_excerpt(excerpt, base_path, is_call, count):
    if is_call: 
        try:
            muspy.write_midi(base_path + '{:02d}'.format(count) + '_call.mid', excerpt, backend='pretty_midi')
        except BaseException as error:
            print('Error: Could not write MIDI file - ' + str(error))
            return -1
    else:
        try:
            muspy.write_midi(base_path + '{:02d}'.format(count) + '_response.mid', excerpt, backend='pretty_midi')
        except BaseException as error:
            print('Error: Could not write MIDI file - ' + str(error))
            return -1

def get_melody_track(tracks):
    for track in tracks:
        if track.name.lower() == "melody" or track.name.lower() == "vocals" or track.name.lower() == "mel":
            return track
    return None


def convert_time_steps_to_seconds(time_steps, bpm, resolution):
    return time_steps / ( bpm / 60 * resolution )
