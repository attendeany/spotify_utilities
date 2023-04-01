from dataclasses import dataclass

from mashumaro import DataClassDictMixin

from models.artist import Artist


@dataclass
class Track(DataClassDictMixin):
    """https://developer.spotify.com/documentation/web-api/reference/get-track"""
    artists: list[Artist]
    duration_ms: int
    explicit: bool

    id: str
    name: str
    popularity: str
    uri: str
