import tempfile
from pathlib import Path

import src.db as db


TEST_DB_PATH = Path(tempfile.gettempdir()) / "sistema_turnos_atc_test.db"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

db.DB_PATH = str(TEST_DB_PATH)

import src.request_store as request_store
import src.roster_store as roster_store

request_store.init_db()
roster_store.init_db()
