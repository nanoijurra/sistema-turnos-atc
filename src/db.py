import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "swaps_atc.db")


def get_connection():
    return sqlite3.connect(DB_PATH)