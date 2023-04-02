from functools import cache
from inspect import get_annotations

from cosntants.sqlite_types import SQLITE_TYPES
from models.track_features import TrackFeatures
from .tracks_db import TracksDatabase


class TracksFeaturesDatabase(TracksDatabase):
    def add_features(self, track_features: TrackFeatures):
        self.db.execute(self._insert_query(), track_features.to_dict())
        self.db.commit()

    def get_features(self, track_id: str):
        data = self.db.execute("SELECT * FROM track_features WHERE id=?", (track_id,)).fetchone()
        return TrackFeatures.from_dict(data)

    @classmethod
    @cache
    def _insert_query(cls):
        fields = tuple(get_annotations(TrackFeatures).keys())
        keys = ', '.join(fields)
        placeholders = ', '.join((f":{key}" for key in fields))
        return f"INSERT INTO track_features ({keys}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    def _init_tables(self):
        super()._init_tables()
        # This approach may have problems if you change the TrackFeatures class,
        # but this is acceptable for the current project.
        fields = []
        for name, cls in get_annotations(TrackFeatures).items():
            fields.append(f"{name} {SQLITE_TYPES[cls]}")

        # noinspection SqlResolve
        query = (
            "CREATE TABLE IF NOT EXISTS track_features ("
            f"{', '.join(fields)}, "
            "PRIMARY KEY (id), "
            "FOREIGN KEY (id) REFERENCES tracks(id) ON DELETE CASCADE"
            ")"
        )
        self.db.execute(query)
