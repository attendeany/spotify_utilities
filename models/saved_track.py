from dataclasses import dataclass
from datetime import datetime

from mashumaro import DataClassDictMixin

from .serialization.time_serializers import SpotifyDTSerializationStrategy
from .track import Track


@dataclass
class SavedTrack(DataClassDictMixin):
    """https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks"""
    added_at: datetime
    track: Track

    class Config:
        serialization_strategy = {
            datetime: SpotifyDTSerializationStrategy(),
        }
