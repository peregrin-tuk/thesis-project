import sqlite3
import json
import copy
from sqlite3 import Error
from datetime import datetime
from pathlib import Path

from definitions import ROOT_DIR
from src.datatypes.melody_data import MelodyData
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
                                    set_id integer,
                                    FOREIGN KEY (input_id) REFERENCES midi_analysis (id),
                                    FOREIGN KEY (gen_base_id) REFERENCES midi_analysis (id),
                                    FOREIGN KEY (output_id) REFERENCES midi_analysis (id),
                                    FOREIGN KEY (set_id) REFERENCES test_sets (id)
                                );"""

    sql_testsets_table = """CREATE TABLE IF NOT EXISTS test_sets (
                                    id integer PRIMARY KEY,
                                    date_created timestamp NOT NULL,
                                    avg_gen_evaluation text NOT NULL,
                                    avg_output_evaluation text NOT NULL,
                                    notes text
                                );"""

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


def store_generation_result(input_data: MelodyData, gen_base_data: MelodyData, result_data: MelodyData, set_id: int = None):
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

    sql_insert_generation = """INSERT INTO generation_results(input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_steps, set_id)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    input_id = store_midi(input_data)
    gen_base_id = store_midi(gen_base_data)
    output_id = store_midi(result_data)

    # CHECK this is not very safe to do -> noone guarantees that those values are included in the dict
    # => maybe extend MelodyData with another datatype that holds fields for the absolutely necessary values ? (that might be None at certain time)
    gen_dur = gen_base_data.meta['generation']['gen_dur']
    gen_model = gen_base_data.meta['generation']['model'] + ' ' + gen_base_data.meta['generation']['checkpoint']
    gen_temperature = gen_base_data.meta['generation']['temperature']
    adapt_steps = copy.deepcopy(result_data.meta['adaptation']['steps'])
    adapt_dur = result_data.meta['adaptation']['total_duration']

    adapt_steps_json = []

    for step in adapt_steps:
        adapt_steps_json.append(dict_values_to_string(step))
    adapt_steps_json = json.dumps(adapt_steps_json)


    cursor.execute(sql_insert_generation, (input_id, gen_base_id, output_id, date, gen_dur, gen_model, gen_temperature, adapt_dur, adapt_steps_json, set_id))
    
    conn.commit()
    return cursor.lastrowid, gen_base_id



def store_midi(data: MelodyData):
    """ 
    Adds a database entry for a midi file and stores the corresponding file in the file system.

    Args:
        data (MelodyData): MelodyData object containing the midi sequence, its type, analysis and evaluation results

    Returns:
        int: id of the inserted row
    """
    data = copy.deepcopy(data)

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


def store_set(cr_sets: list, avg_gen_evaluation: dict, avg_output_evaluation: dict, notes: str = None):
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()

    sql_insert_set = """INSERT INTO test_sets(date_created, avg_gen_evaluation, avg_output_evaluation, notes)
              VALUES(?, ?, ?, ?)"""

    avg_gen_evaluation = copy.deepcopy(avg_gen_evaluation)
    avg_output_evaluation = copy.deepcopy(avg_output_evaluation)
    

    avg_gen_evaluation_json = json.dumps(dict_values_to_string(avg_gen_evaluation))
    avg_output_evaluation_json = json.dumps(dict_values_to_string(avg_output_evaluation))

    cursor.execute(sql_insert_set, (date, avg_gen_evaluation_json, avg_output_evaluation_json, notes))
    set_id = cursor.lastrowid
    conn.commit()

    generation_ids = []
    for cr_set in cr_sets:
        _, gen_id = store_generation_result(cr_set.input_sequence, cr_set.generated_base_sequence, cr_set.output_sequence, set_id)
        generation_ids.append(gen_id)
    
    return set_id, generation_ids


def update_notes_in_set(set_id: int, notes: str):
    """ 
    Updates the notes for a test set.

    Args:
        index (int):  id of the test set
        notes (str): updated notes string
    """
    conn = create_connection()
    cursor = conn.cursor()

    sql_update_test_set = """UPDATE test_sets
                            SET notes = ?,
                            WHERE id = ?"""

    cursor.execute(sql_update_test_set, (
        notes,
        set_id)
    )

    conn.commit()

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


def dict_values_to_string(dictionary: dict):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            value = dict_values_to_string(value)
        else:
            if value is not str:
                dictionary[key] = str(value)
    return dictionary