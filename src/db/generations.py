import sqlite3
from sqlite3 import Error
from enum import Enum
from datetime import datetime
from pathlib import Path
from IPython.core.display import JSON
from pretty_midi import PrettyMIDI

from definitions import ROOT_DIR, SequenceType
from src.io.output import saveMidiFile

db_path = ROOT_DIR / Path('/data/generations.db')
midi_dir_path = ROOT_DIR / Path('/data/generation_files')


def create_connection():
    """ 
    Connect to the SQLite database 
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        return conn
    except Error as e:
        print(e)



def create_tables():
    """ 
    Creates generation_results, midi_analysis and test_sets tables in the database, if they do not exist yet.
    """
    sql_midi_table = """CREATE TABLE IF NOT EXISTS midi_analysis (
                                    id integer PRIMARY KEY,
                                    midi_file text NOT NULL,
                                    type integer NOT NULL,
                                    date_created timestamp NOT NULL,
                                    analysis text
                                );"""

    sql_generations_table = """CREATE TABLE IF NOT EXISTS generation_results (
                                    id integer PRIMARY KEY,
                                    input_id integer NOT NULL,
                                    gen_base_id integer NOT NULL,
                                    output_id integer NOT NULL,
                                    date timestamp NOT NULL,
                                    gen_dur real NOT NULL,
                                    gen_model text NOT NULL,
                                    gen_temperature real NOT NULL,
                                    adapt_dur real NOT NULL,
                                    adapt_settings text,
                                    FOREIGN KEY (input_id) REFERENCES midi_analysis (id),
                                    FOREIGN KEY (gen_base_id) REFERENCES midi_analysis (id),
                                    FOREIGN KEY (output_id) REFERENCES midi_analysis (id)
                                );"""

    sql_testsets_table = """CREATE TABLE IF NOT EXISTS test_sets (
                                    id integer PRIMARY KEY,
                                    date_created timestamp NOT NULL,
                                    result_set text NOT NULL,
                                    notes text
                                );"""

    # TODO add analysis and evaluation parameters as columns
    # NOTE analysis and adapt_settings are here expected to be json objects
    # NOTE instead of adding new nullable columns for new features, consider creating a whole new DB with the new version

    conn = create_connection()

    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql_midi_table)
            c.execute(sql_generations_table)
            c.execute(sql_testsets_table)
        except Error as e:
            print(e)
    else:
        print('[DB] Error: Database connection could not be created.')



def store_generation_result(
    input_midi: PrettyMIDI,
    gen_base_midi: PrettyMIDI,
    output_midi: PrettyMIDI,
    gen_dur: float,
    gen_model: str,
    gen_temperature: float,
    adapt_dur: float,
    adapt_settings: dict = None,
    in_recorded: bool = True
):
    """ 
    Stores a single generation result in the database and the 3 corresponding midi files in the file system.

    Args:
        input_midi (PrettyMIDI): 'call' sequence as midi object
        gen_base_midi (PrettyMIDI): result of the generation model as midi object (intermediate step)
        output_midi (PrettyMIDI): 'response' sequence as midi object
        gen_dur (float): duration of the generation
        gen_model (str): checkpoint of the used generation model
        gen_temperature (float): temperature used for the generation model
        adapt_dur (float): duration of the adaption
        adapt_settings (dict, optional): default = None
        in_recorded (bool, optional): default = True

    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()

    sql_insert_generation = """INSERT INTO generation_results(input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_settings)
              VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    input_type = SequenceType.REC_INPUT if in_recorded else SequenceType.EXAMPLE
    input_id = store_midi(input_midi, input_type)
    gen_base_id = store_midi(gen_base_midi, SequenceType.GEN_BASE)
    output_id = store_midi(output_midi, SequenceType.OUTPUT)

    cursor.execute(sql_insert_generation, (input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_settings))
    
    conn.commit()
    return cursor.lastrowid



def store_midi(midi: PrettyMIDI, sequence_type: SequenceType, analysis: JSON = None):
    """ 
    Adds a database entry for a midi file and stores the corresponding file in the file system.

    Args:
        midi (PrettyMIDI):  sequence as midi object
        type (connection.SequenceType): role of the midi sequence, enum of REC_INPUT, EXAMPLE, GEN_BASE or OUTPUT
        analysis (dict, optional): music analysis data, default = None

    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()
    index = cursor.lastrowid + 1 if cursor.lastrowid is not None else 0 
    file_path = '{:03d}_'.format(index) + date.strftime("%Y-%m-%d-%H-%M") + '_{}.mid'.format(sequence_type.name) # save midis as ###(id)_####-##-##-##-##(date)_(type).mid

    sql_insert_midi = """INSERT INTO midi_analysis(midi_file, date_created, type, analysis)
              VALUES(?, ?, ?, ?)"""

    sql_update_filepath = """UPDATE midi_analysis SET midi_file = ? WHERE id = ?"""

    cursor.execute(sql_insert_midi, (file_path, date, sequence_type.name, analysis))

    # check id
    last_id = cursor.lastrowid 
    if (last_id is not index):
        file_path = f'{last_id:03}{file_path[3:]}'
        cursor.execute(sql_update_filepath, (file_path, last_id))

    saveMidiFile(midi, f'../data/midi_files/{file_path}', False)

    conn.commit()
    return last_id



def read_generation_result(index: int):
    """ 
    Fetches a generation result entry from the database.

    Args:
        id (int): row id of the entry

    Returns:
        sqlite3.Row: row object with the generation result entry
    """
    sql_fetch_gen = """SELECT * from generation_results where id = ?"""

    conn = create_connection()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql_fetch_gen, (index,))
    return c.fetchone()




def read_midi(index: int):
    """ 
    Fetches a midi entry from the database.

    Args:
        id (int): row id of the entry

    Returns:
        sqlite3.Row: row object with the midi entry
    """
    sql_fetch_mid = """SELECT * from midi_analysis where id = ?"""

    conn = create_connection()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql_fetch_mid, (index,))
    return c.fetchone()
