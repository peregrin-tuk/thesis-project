# class MidiInput

# Global variables:
# ✔ default port 
# ✔ signature (enum - 4/4, 3/4, ..)
# ✔ tempo (int bpm)
#    => those two can be used to record a specific number of bars + play a click metronom for the user

# FUNCTIONS
# ✔ abstract? record (record function only differentiate in their break condition)
# recordSeconds(int: length in ms)
        # output: "ready to record"
        # recording starts when first note is pressed
# ✔ recordBars(int: length in bars)
# ✔ recordUntilRest(optional: int: rest length in ms)
        # if no open note_on event exists + no new event incoming for X ms -> stop recording
# recordUntilStopped()
        # records until stopRecording() is called -> could be the general record() function, so all other recordings could also bes stopped
        # should other recordings be able to be stopped? canceled yes, but stopping and saving the recording midway might lead to unexpected behaviour
# ✔ recordSingleNote()
# cancelRecording()
# playNote() ? (als callback um input zu hören, sollte dann synthesize_input = true/false an init übergeben können)

from datetime import datetime
import mido
import pretty_midi


class MidiInput():
    """
    docstring
    """

    used_ports = []
    default_port = 0                # default midi device port
    default_tempo = 120             # beats per minute (BPM) // MIDI uses QPM (quarters per minute)
    default_beat_resolution = 480   # ticks per beat (= PPQ if time signature = x/4)
    default_time_signature = (4, 4)
    midi_file_cache = '../midi/tmp/recording_cache.mid'
    start_on_note = True


    def __init__(self, port_id = default_port, tempo = default_tempo, beat_resolution = default_beat_resolution, time_signature = default_time_signature):
        self.tempo = tempo
        self.beat_resolution = beat_resolution
        self.time_signature = time_signature
        self.open_port(port_id)



    def __del__(self):
        self.close_port()



    ### OPEN & CLOSE INPUT PORT ###

    def open_port(self, port_id = 0):
        if port_id in self.used_ports:
            print('Error: Port {0} "{1}" is already in use. Close the port in the MidiInput object that is using it and then try again.'.format(str(port_id), str(mido.get_input_names()[port_id])))
        else:
            try:
                self.port_id = port_id
                self.port = mido.open_input(mido.get_input_names()[port_id])
            except OSError as error:
                print('Error: Could not open MIDI port - ' + str(error))
            except IndexError as error:
                print('Error: Could not open MIDI port - no port exists at index ' + str(port_id))
                print('Available input ports: ' + str(mido.get_input_names()))
            else:
                self.used_ports.append(port_id)
                print('[IO] "{0}" connected as input port'.format(str(self.port.name)))



    def close_port(self):
        try:
            self.port.close()
            self.used_ports.remove(self.port_id)
            print('[IO] Input port "{0}" closed.'.format(str(mido.get_input_names()[self.port_id])))
        except:
            pass



    ### RECORD ###

    def recordUntilRest(self, max_rest_in_seconds = 2):
        """
        Records MIDI input until no message arrives for a specified amounts of seconds (default = 2)

        Returns:
            PrettyMIDI object if recording was successful.
            None if recording failed or no input was recorded.
        """

        midi, track, init_datetime = self.__init_recording()
        last_event_datetime = init_datetime

        while (datetime.now() - last_event_datetime).total_seconds() < max_rest_in_seconds:
            try:
                track, _, last_event_datetime = self.__record_message(track, last_event_datetime)
            except ConnectionError:
                return None

        return self.__save_and_return_recording(midi)



    def recordBars(self, number_of_bars):
        """
        Records for a specified number of bars. The length of one bar is calculted by the internal tempo and time signature attributes.

        Returns:
            PrettyMIDI object if recording was successful.
            None if recording failed or no input was recorded.
        """

        length = number_of_bars * self.length_of_bar_in_seconds()

        midi, track, init_datetime = self.__init_recording()
        last_event_datetime = init_datetime

        while (datetime.now() - init_datetime).total_seconds() < length:
            try:
                track, _, last_event_datetime = self.__record_message(track, last_event_datetime)
            except ConnectionError:
                return None

        return self.__save_and_return_recording(midi)

    

    def recordNotes(self, number_of_notes):
        """
        Records a specified number of notes. One note = note_on + note_off event

        Returns:
            PrettyMIDI object if recording was successful.
            None if recording failed or no input was recorded.
        """

        midi, track, init_datetime = self.__init_recording()
        last_event_datetime = init_datetime

        note_off_count = 0
        note_on_count = 0

        while note_off_count < number_of_notes:
            try:
                track, msg, last_event_datetime = self.__record_message(track, last_event_datetime)
            except ConnectionError:
                return None
            else:
                if msg is not None:
                    if msg.type == 'note_off':
                        note_off_count += 1
                    else:
                        note_on_count += 1

        # clean up midi: remove note_on events without corresponding note_off
        if note_on_count != note_off_count:
            on_events = [msg for msg in track if msg.type == 'note_on']
            for msg in on_events:
                if not any(c.type == 'note_off' and c.note == msg.note for c in track[track.index(msg):]):
                    track.remove(msg)

        return self.__save_and_return_recording(midi)



    ### INTERNAL RECORDING METHODS ###

    def __init_recording(self):
        """
        Creates midi object, creates and appends track.
        Sets tempo and beat resolution.
        Registers the time when recording started.

        Returns:
            ( midi object,
              track object,
              init_datetime )

        """
        # create file and track, set tempo and beat resolution
        midi = mido.MidiFile(type=0, ticks_per_beat=self.beat_resolution)
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo)))
        track.append(mido.MetaMessage('time_signature', numerator=self.time_signature[0], denominator=self.time_signature[1]))

        # init timing
        init_datetime = datetime.now()

        # tell user that recording started
        print('[IO] NOW RECORDING ...')
        print('[REC]', end=' ')

        return midi, track, init_datetime



    def __record_message(self, track, last_event_datetime):
        """
        Listens to port and records a single MIDI message.
        Adds delta time in ticks to recorded MIDI message

        Returns:
            MIDI message

        Raises:
            ConncetionError: If port is undefined no longer available
        """

        # listen for incoming message
        try:
            msg = self.port.receive(block=False)
        except AttributeError:
            print('Error: No Input Port defined')
            raise ConnectionError
        except IOError as error:
            print('Error: MIDI device disconnected - ' + str(error))
            self.close_port()
            raise ConnectionError

        # check if port still exists
        if self.port.name not in mido.get_input_names():
            print('Error: MIDI device {0} disconnected.'.format(self.port.name))
            self.close_port()
            raise ConnectionError

        # add time ticks to msg and append to track
        if msg is not None:
            event_datetime = datetime.now()
            delta_time_in_seconds = (event_datetime - last_event_datetime).total_seconds()
            msg.time = int(mido.second2tick(delta_time_in_seconds, self.beat_resolution, mido.bpm2tempo(self.tempo)))
            last_event_datetime = event_datetime

            track.append(msg)

            # live output pitches of note_on events while recording
            if msg.type == 'note_on':
                print(msg.note, end=' ')
        
        return  track, msg, last_event_datetime



    def __save_and_return_recording(self, midi):
        """
        Checks if messages where recorded and converts midi to pretty_midi
        
        Returns:
            PrettyMIDI object if midi data was recorded.
            None if midi is empty.
        """
        if midi.length <= 0:
            print('[IO] nothing was recorded.')
            return None

        midi.save(self.midi_file_cache)
        pm = pretty_midi.PrettyMIDI(self.midi_file_cache)
        print('\n[IO] recording successful.')
        return pm



    ### UTILITY ###
    def length_of_bar_in_seconds(self):
        """
        Calculates the duration of one bar based on set tempo and time signature

        Returns:
            float: length of one bar in seconds
        """
        return 60.0/self.tempo * self.time_signature[0]
