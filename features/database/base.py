import sqlite3

from cosntants.paths import Paths


class SpotifyDatabase:
    database_file = Paths.LOCAL_DATABASE
    db: sqlite3.Connection

    def connect(self):
        self.db = sqlite3.connect(self.database_file)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._init_tables()

    def _init_tables(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
