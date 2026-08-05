import sqlite3
from pathlib import Path


# create connection with dictionary databse
def dictionary_connection():
    DB_PATH = Path(__file__).resolve().parent / "dictionary.db"
    conn = sqlite3.connect(DB_PATH)
    return conn

def kanji_dict_connection():
    DB_PATH = Path(__file__).resolve().parent / "kanji.db"
    conn = sqlite3.connect(DB_PATH)
    return conn

def database_connection():
    DB_PATH = Path(__file__).resolve().parent / "main.db"
    conn = sqlite3.connect(DB_PATH)
    return conn
