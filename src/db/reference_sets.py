import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime
from IPython.core.display import JSON

db_path = '../data/reference_sets.db'


def create_connection():
    """ 
    Connect to the SQLite database 
    """
    conn = None
    try:
        conn = sqlite3.connect(
            db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        return conn
    except Error as e:
        print(e)


def create_tables():
    """ 
    Creates reference_data and reference_sets tables in the database, if they do not exist yet.
    """
    sql_set_table = """CREATE TABLE IF NOT EXISTS reference_sets (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    number_of_samples integer NOT NULL,
                                    sample_length_in_bars integer NOT NULL,
                                    source text NOT NULL,
                                    date_analyzed timestamp NOT NULL,
                                    average_similarity_distances text,
                                    notes text
                                );"""

    sql_data_table = """CREATE TABLE IF NOT EXISTS reference_data (
                                    id integer PRIMARY KEY,
                                    set_id integer NOT NULL,
                                    song_name text NOT NULL,
                                    pair_number integer NOT NULL,
 
                                    pitch_count_distance real NOT NULL,
                                    pitch_count_per_bar_distance real NOT NULL,
                                    pitch_class_histogram_distance real NOT NULL,
                                    pitch_class_histogram_per_bar_distance real NOT NULL,
                                    pitch_class_transition_matrix_distance real NOT NULL,
                                    avg_pitch_interval_distance real NOT NULL,
                                    pitch_range_distance real NOT NULL,

                                    note_count_distance real NOT NULL,
                                    note_count_per_bar_distance real NOT NULL,
                                    note_length_histogram_distance real NOT NULL,
                                    note_length_transition_matrix_distance real NOT NULL,
                                    avg_ioi_distance real NOT NULL,

                                    FOREIGN KEY (set_id) REFERENCES reference_sets (id)
                                );"""

    conn = create_connection()

    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql_set_table)
            c.execute(sql_data_table)
        except Error as e:
            print(e)
    else:
        print('[DB] Error: Database connection could not be created.')


def store_ref_data(
    set_id: int,
    song_name: str,
    pair_number: int,

    pitch_count: float,
    pitch_count_per_bar: float,
    pitch_class_histogram: float,
    pitch_class_histogram_per_bar: float,
    pitch_class_transition_matrix: float,
    avg_pitch_interval: float,
    pitch_range: float,

    note_count: float,
    note_count_per_bar: float,
    note_length_histogram: float,
    note_length_transition_matrix: float,
    avg_ioi: float
):
    """ 
    Stores a set of similarity distances for a single call-and-response pair.

    Args:
        set_id (int):
        song_name (str): 
        pair_number (int): 

        pitch_count_distance (float): 
        pitch_count_per_bar_distance (float): 
        pitch_class_histogram_distance (float): 
        pitch_class_histogram_per_bar_distance (float): 
        pitch_class_transition_matrix_distance (float): 
        avg_pitch_interval_distance (float): 
        pitch_range_distance (float): 

        note_count_distance (float): 
        note_count_per_bar_distance (float): 
        note_length_histogram_distance (float): 
        note_length_transition_matrix_distance (float): 
        avg_ioi_distance (float): 

    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()

    sql_insert_ref_data = """INSERT INTO reference_data(
                                set_id,
                                song_name,
                                pair_number,
                                pitch_count_distance, 
                                pitch_count_per_bar_distance, 
                                pitch_class_histogram_distance, 
                                pitch_class_histogram_per_bar_distance, 
                                pitch_class_transition_matrix_distance, 
                                avg_pitch_interval_distance, 
                                pitch_range_distance, 
                                note_count_distance, 
                                note_count_per_bar_distance, 
                                note_length_histogram_distance, 
                                note_length_transition_matrix_distance, 
                                avg_ioi_distance)
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    cursor.execute(sql_insert_ref_data, (
        set_id,
        song_name,
        pair_number,
        pitch_count,
        pitch_count_per_bar,
        pitch_class_histogram,
        pitch_class_histogram_per_bar,
        pitch_class_transition_matrix,
        avg_pitch_interval,
        pitch_range,
        note_count,
        note_count_per_bar,
        note_length_histogram,
        note_length_transition_matrix,
        avg_ioi)
    )

    conn.commit()
    return cursor.lastrowid


def store_ref_set(
        name: str,
        number_of_samples: int,
        sample_length_in_bars: int,
        source: str,
        average_similarity_distances: dict = None,
        notes: str = None
    ):
    """ 
    Adds a database entry for a reference data set, stores it's meta data and average similarity distances.

    Args:


    Returns:
        int: id of the inserted row
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()

    sql_insert_ref_set = """INSERT INTO reference_sets(
                                name,
                                number_of_samples,
                                sample_length_in_bars,
                                source,
                                date_analyzed,
                                average_similarity_distances,
                                notes)
                                VALUES(?, ?, ?, ?, ?, ?, ?)"""

    cursor.execute(sql_insert_ref_set, (
        name,
        number_of_samples,
        sample_length_in_bars,
        source,
        date,
        average_similarity_distances,
        notes)
    )

    conn.commit()
    return cursor.lastrowid


def update_avg_distances_for_set(
        index: int,
        average_similarity_distances: JSON,
    ):
    """ 
    Updates the average similarity distances for a reference data set.

    Args:
        index (int):  id of the reference set
        analysis (JSON): average similarity distances as JSON object
    """
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now()

    sql_update_ref_set = """UPDATE reference_set
                            SET date_analyzed = ?,
                                average_similarity_distances = ?
                            WHERE id = ?"""

    cursor.execute(sql_update_ref_set, (
        date,
        average_similarity_distances,
        index)
    )

    conn.commit()


def fetch_ref_data_by_id(index: int):
    """ 
    Fetches a reference data entry from the database.

    Args:
        id (int): row id of the entry

    Returns:
        sqlite3.Row: row object with the generation result entry
    """
    sql_fetch_data = """SELECT * from reference_data where id = ?"""

    conn = create_connection()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql_fetch_data, (index,))
    return c.fetchone()


def fetch_ref_set_by_id(index: int):
    """ 
    Fetches a reference set entry from the database.

    Args:
        id (int): row id of the entry

    Returns:
        sqlite3.Row: row object with the midi entry
    """
    sql_fetch_set = """SELECT * from reference_set where id = ?"""

    conn = create_connection()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql_fetch_set, (index,))
    return c.fetchone()


def fetch_ref_set_by_name(name: str):
    """ 
    Fetches a reference set entry from the database.

    Args:
        name (str): name of the data set

    Returns:
        sqlite3.Row: row object with the midi entry
    """
    sql_fetch_set = """SELECT * from reference_set where name = ?"""

    conn = create_connection()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql_fetch_set, (name,))
    return c.fetchone()


def ref_data_table_to_dataframe(index: int):
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM reference_data WHERE set_id = ?", conn, params=(index,))
    conn.commit()
    conn.close()
    return df
