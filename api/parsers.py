from typing import Optional
from models import Track

def parse_spotify_playlist_item(item: dict) -> Optional[Track]:
    """
    Parses a single item from Spotify's playlist response
    and converts it into our custom Track object.
    """
    try:
        track_data = item.get('track')
        if not track_data or not track_data.get('id'):
            return None

        return Track(
            id=track_data['id'],
            name=track_data['name'],
            artist=track_data['artists'][0]['name'],
            uri=track_data['uri']
        )
    except (KeyError, IndexError):
        return None