from typing import List
import services
from models import Track

def filter_tracks_by_genre(tracks: List[Track], genre: str) -> List[Track]:
    """
    Filters a list of Track objects by a specified genre.
    This is the core "business logic" of the application.
    """
    filtered_tracks = []
    for track in tracks:
        if track:
            # Get genre list from the appropriate service
            genre_list = services.get_track_genre(
                track.artist, 
                track.name
            )
            
            # Check if the target genre is in the list
            if genre.lower() in [g.lower() for g in genre_list]:
                filtered_tracks.append(track)
                
    return filtered_tracks