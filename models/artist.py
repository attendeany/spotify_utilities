from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin


@dataclass
class Artist(DataClassDictMixin):
    """https://developer.spotify.com/documentation/web-api/reference/get-an-artist"""
    id: str
    name: str
    uri: str

    popularity: int | None = None
    genres: list[str] | None = field(default_factory=list)
