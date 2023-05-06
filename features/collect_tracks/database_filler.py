from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from features.database.features_db import TracksFeaturesDatabase
from models.artist import Artist
from models.saved_track import SavedTrack
from models.track_features import TrackFeatures
from utils.helpers import iter_chunks

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='user-library-read'))
database = TracksFeaturesDatabase()


def fill_track_features():
    track_ids = database.track_ids_without_features()
    for chunk in iter_chunks(track_ids, 100):
        audio_features = spotify.audio_features(chunk)
        for f in audio_features:
            track_features = TrackFeatures.from_dict(f)
            database.add_features(track_features)
    return len(track_ids)


def fill_artists_info():
    artist_ids = database.artist_ids_without_info()
    for chunk in iter_chunks(artist_ids, 50):
        artists = spotify.artists(chunk)['artists']
        for art in artists:
            artist = Artist.from_dict(art)
            database.add_artist(artist, update_on_conflict=True)
    return len(artist_ids)


def fill_saved_tracks():
    try:
        latest_date = datetime.fromtimestamp(
            database.db.execute("SELECT MAX(added_at_timestamp) FROM saved_tracks").fetchone()[0])
    except TypeError:
        latest_date = None

    saved_tracks = {'next': True, '_is_first': True}
    added_count = 0
    while saved_tracks['next']:
        if saved_tracks.get('_is_first'):
            saved_tracks = spotify.current_user_saved_tracks(limit=50)
            print(f"Total tracks: {saved_tracks.get('total')}")
        else:
            saved_tracks = spotify.next(saved_tracks)

        for item in saved_tracks['items']:
            track = SavedTrack.from_dict(item)
            if latest_date and (track.added_at <= latest_date):
                return added_count
            database.add_saved_track(track)
            added_count += 1
    return added_count
