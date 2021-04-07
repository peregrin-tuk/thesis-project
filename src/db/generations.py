import sqlite3
import json
from sqlite3 import Error
from datetime import datetime
from pathlib import Path
from src.datatypes.melody_data import MelodyData

from definitions import ROOT_DIR
from src.io.output import saveMidiFile

db_path = ROOT_DIR / Path('data/generations.db')
midi_dir_path = ROOT_DIR / Path('data/generation_files')


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
                                    analysis text,
                                    evaluation text
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
                                    adapt_steps text,
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



def store_generation_result(input_data: MelodyData, gen_base_data: MelodyData, result_data: MelodyData):
    """ 
    Stores a single generation result in the database and the 3 corresponding midi files in the file system.

    Args:
        input_data (MelodyData): 'call' sequence melody data object
        gen_base_data (MelodyData): result of the generation model as melody data object (intermediate step)
        result_data (MelodyData): 'response' sequence as melody data object

    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()

    sql_insert_generation = """INSERT INTO generation_results(input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_steps)
              VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    input_id = store_midi(input_data)
    gen_base_id = store_midi(gen_base_data)
    output_id = store_midi(result_data)

    # CHECK this is not very safe to do -> noone guarantees that those values are included in the dict
    # => maybe extend MelodyData with another datatype that holds fields for the absolutely necessary values ? (that might be None at certain time)
    gen_dur = gen_base_data.meta['generation']['gen_dur']
    gen_model = gen_base_data.meta['generation']['model'] + ' ' + gen_base_data.meta['generation']['checkpoint']
    gen_temperature = gen_base_data.meta['generation']['temperature']
    adapt_steps = result_data.meta['adaptation']['steps']
    adapt_dur = result_data.meta['adaptation']['total_duration']

    adapt_steps_json =  json.dumps(dict_values_to_string(adapt_steps))


    cursor.execute(sql_insert_generation, (input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_steps_json))
    
    conn.commit()
    return cursor.lastrowid



def store_midi(data: MelodyData):
    """ 
    Adds a database entry for a midi file and stores the corresponding file in the file system.

    Args:
        data (MelodyData): MelodyData object containing the midi sequence, its type, analysis and evaluation results

    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()
    index = cursor.lastrowid + 1 if cursor.lastrowid is not None else 0 
    file_path = '{:03d}_'.format(index) + date.strftime("%Y-%m-%d-%H-%M") + '_{}.mid'.format(data.sequence_type.name) # save midis as ###(id)_####-##-##-##-##(date)_(type).mid

    analysis_json =  json.dumps(dict_values_to_string(data.analysis))
    evaluation_json =  json.dumps(dict_values_to_string(data.evaluation))

    sql_insert_midi = """INSERT INTO midi_analysis(midi_file, date_created, type, analysis, evaluation)
              VALUES(?, ?, ?, ?, ?)"""

    sql_update_filepath = """UPDATE midi_analysis SET midi_file = ? WHERE id = ?"""

    cursor.execute(sql_insert_midi, (file_path, date, data.sequence_type.name, analysis_json, evaluation_json))

    # check id
    last_id = cursor.lastrowid 
    if (last_id is not index):
        file_path = f'{last_id:03}{file_path[3:]}'
        cursor.execute(sql_update_filepath, (file_path, last_id))

    saveMidiFile(data.sequence, str(midi_dir_path / file_path), False)

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


def dict_values_to_string(dict: dict):
    for key, value in dict.items():
        if isinstance(value, dict):
            value = dict_values_to_string(value)
        else:
            if value is not str:
                value = str(value)
    return dict