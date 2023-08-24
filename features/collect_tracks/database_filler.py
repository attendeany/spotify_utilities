from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

from features.database.features_db import TracksFeaturesDatabase
from features.database.tracks_db import TracksDatabase
from models.artist import Artist
from models.saved_track import SavedTrack
from models.track_features import TrackFeatures
from utils.helpers import iter_chunks

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='user-library-read'))


def fill_track_features():
    with TracksFeaturesDatabase() as database:
        track_ids = database.track_ids_without_features()
        with tqdm(total=len(track_ids), desc="Fetching tracks features", ncols=100) as pbar:
            for chunk in iter_chunks(track_ids, 100):
                audio_features = spotify.audio_features(chunk)
                for f in audio_features:
                    track_features = TrackFeatures.from_dict(f)
                    database.add_features(track_features)
                    pbar.update(1)
    return len(track_ids)


def fill_artists_info():
    with TracksDatabase() as database:
        artist_ids = database.artist_ids_without_info()
        with tqdm(total=len(artist_ids), desc="Fetching artists info", ncols=100) as pbar:
            for chunk in iter_chunks(artist_ids, 50):
                artists = spotify.artists(chunk)['artists']
                for art in artists:
                    artist = Artist.from_dict(art)
                    database.add_artist(artist)
                    pbar.update(1)
    return len(artist_ids)


def fill_saved_tracks():
    with TracksDatabase() as database:
        try:
            latest_date = datetime.fromtimestamp(
                database.db.execute("SELECT MAX(added_at_timestamp) FROM saved_tracks").fetchone()[0])
        except TypeError:
            latest_date = None

        saved_tracks = {'next': True, '_is_first': True}
        added_count = 0
        with tqdm(desc="Fetching saved tracks", ncols=100) as pbar:
            while saved_tracks['next']:
                if saved_tracks.get('_is_first'):
                    saved_tracks = spotify.current_user_saved_tracks(limit=50)
                    pbar.total = saved_tracks.get('total')
                    print(f"Total tracks: {pbar.total}")
                else:
                    saved_tracks = spotify.next(saved_tracks)

                for item in saved_tracks['items']:
                    track = SavedTrack.from_dict(item)
                    database.add_saved_track(track)
                    added_count += 1
                    pbar.update(1)
                    if latest_date and (track.added_at < latest_date):
                        return added_count
    return added_count
