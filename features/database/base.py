import sqlite3

from cosntants.paths import Paths


class SpotifyDatabase:
    def __init__(self):
        self.db = sqlite3.connect(Paths.LOCAL_DATABASE)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._init_tables()

    def _init_tables(self):
        pass

    def __del__(self):
        self.db.close()
