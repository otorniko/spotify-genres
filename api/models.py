from dataclasses import dataclass
from typing import Optional

@dataclass
class Track:
    """A simplified object representing only the track data we need."""
    id: str
    name: str
    artist: str
    genre: Optional[str] = None