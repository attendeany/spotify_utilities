from models.artist import Artist
from models.saved_track import SavedTrack
from models.track import Track
from .base import SpotifyDatabase


class TracksDatabase(SpotifyDatabase):
    def _init_tables(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS tracks ("
            "id TEXT PRIMARY KEY, "
            "name TEXT, "
            "artists TEXT, "
            "popularity INTEGER, "
            "duration_ms INTEGER, "
            "explicit INTEGER, "
            "uri TEXT"
            ")"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS saved_tracks ("
            "id TEXT PRIMARY KEY REFERENCES tracks(id) ON DELETE CASCADE, "
            "added_at TEXT, "
            "added_at_timestamp INTEGER"
            ")"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS artists ("
            "id TEXT PRIMARY KEY, "
            "name TEXT, "
            "uri TEXT, "
            "popularity INTEGER, "
            "genres TEXT"
            ")"
        )
        self.db.execute(
            """
            CREATE VIEW IF NOT EXISTS track_summary AS 
            SELECT
                artists.name as artist,
                tracks.name,
                tracks.popularity,
                artists.genres,
                duration_ms,
                explicit,
                added_at,
                added_at_timestamp,
                tracks.uri,
                tracks.id
            FROM tracks 
            INNER JOIN saved_tracks st on tracks.id = st.id 
            INNER JOIN artists on ltrim(tracks.artists, ',') = artists.id
            """
        )

    def add_artist(self, artist: Artist):
        artist_dict = artist.to_dict()
        artist_dict['genres'] = ','.join(artist.genres)
        self.db.execute(
            "INSERT INTO artists (id, name, uri, popularity, genres) "
            "VALUES (:id, :name, :uri, :popularity, :genres) "
            "ON CONFLICT DO UPDATE SET popularity=:popularity, genres=:genres", artist_dict)
        self.db.commit()

    def get_artist(self, artist_id: str):
        output = dict(self.db.execute("SELECT * FROM artists WHERE id=?", (artist_id,)).fetchone())
        output['genres'] = output['genres'].split(',')
        return Artist.from_dict(output)

    def add_track(self, track: Track):
        for artist in track.artists:
            self.add_artist(artist)
        track_dict = track.to_dict()
        track_dict['artists'] = ','.join(artist.id for artist in track.artists)
        track_dict['explicit'] = int(track.explicit)
        self.db.execute(
            "INSERT INTO tracks (id, name, artists, popularity, duration_ms, explicit, uri) "
            "VALUES (:id, :name, :artists, :popularity, :duration_ms, :explicit, :uri) ON CONFLICT DO NOTHING",
            track_dict)
        self.db.commit()

    def get_track(self, track_id: str):
        output = dict(self.db.execute("SELECT * FROM tracks WHERE id=?", (track_id,)).fetchone())
        artists = []
        for artist_id in output['artists'].split(','):
            artists.append(self.get_artist(artist_id))

        output['artists'] = []
        output['explicit'] = bool(output['explicit'])
        track = Track.from_dict(output)
        track.artists = artists
        return track

    def add_saved_track(self, saved_track: SavedTrack):
        self.add_track(saved_track.track)
        self.db.execute(
            "REPLACE INTO saved_tracks (id, added_at, added_at_timestamp) VALUES (?, ?, ?)",
            (saved_track.track.id, str(saved_track.added_at), int(saved_track.added_at.timestamp())))
        self.db.commit()

    def artist_ids_without_info(self):
        data = self.db.execute("SELECT id FROM artists WHERE popularity IS NULL").fetchall()
        return [i[0] for i in data]
