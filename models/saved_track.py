from dataclasses import dataclass, field
from datetime import datetime

import ciso8601
from mashumaro import DataClassDictMixin

from .track import Track


@dataclass
class SavedTrack(DataClassDictMixin):
    """https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks"""
    added_at: datetime = field(
        metadata={"deserialize": ciso8601.parse_datetime_as_naive}
    )
    track: Track
