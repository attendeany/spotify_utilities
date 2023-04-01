from datetime import datetime

import ciso8601 as ciso8601
from mashumaro.types import SerializationStrategy


class SpotifyDTSerializationStrategy(SerializationStrategy):
    def serialize(self, value: datetime) -> int:
        return int(value.timestamp())

    def deserialize(self, value: str | int) -> datetime:
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        return ciso8601.parse_datetime_as_naive(value)
