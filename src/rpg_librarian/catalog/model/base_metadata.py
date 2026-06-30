from __future__ import annotations

from pydantic import BaseModel


class BaseMetadata(BaseModel):
    artist: str | None = None
    title: str | None = None
    publisher: str | None = None
    copyright: str | None = None
    genre: str | None = None

    def is_empty(self) -> bool:
        """True when no field carries a value, so the block adds nothing to an entry."""
        return not any((self.artist, self.title, self.publisher, self.copyright, self.genre))
