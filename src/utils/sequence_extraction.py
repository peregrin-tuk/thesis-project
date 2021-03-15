import muspy
from pathlib import Path

#TODO create optional argument regex to choose the melody track based on that regex

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
        int: 1 if operation was successful, 0 if no track was found, -1 in case of an error.
    """
    track = get_melody_track(song.tracks)

    if track is not None:
        is_call = True
        count = 1

        # bar_dur_in_sec = 60 / song.tempos[0].qpm * song.time_signature[0].nominator * 4 / song.time_signature[0].denominator
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
                # save excerpt
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

                # init new one
                excerpt = __create_new_empty_track(song)

                # change time markers (move window x bars)
                time_marker_start = time_marker_end
                time_marker_end = time_marker_start + time_steps_per_bar * length_in_bars

                # append current note
                excerpt.tracks[0].append(__extract_note(note, time_marker_start, song.tempos[0].qpm, song.resolution))
                
                # increase count and toggle call/response
                if not is_call:
                    count += 1
                is_call = not is_call
        return 1
    return 0


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



def get_melody_track(tracks):
    for track in tracks:
        if track.name.lower() == "melody" or track.name.lower() == "vocals" or track.name.lower() == "mel":
            return track
    else:
        return None


def convert_time_steps_to_seconds(time_steps, bpm, resolution):
    return time_steps / ( bpm / 60 * resolution )
