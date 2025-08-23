import parsers
import pylast
from auth import authenticate_lastfm


def get_playlist_tracks(sp, playlist_id: str):
    """
    Fetches all tracks from a Spotify playlist, handling pagination and errors.
    """
    try:
        results = sp.playlist_items(playlist_id)
        
        # Check if the initial API call failed
        if not results:
            return [] # Return an empty list if playlist not found

        tracks = results['items']
        
        # Handle pagination if there are more than 100 tracks
        while results and results['next']:
            results = sp.next(results)
            # Also check if the paginated call was successful
            if results:
                tracks.extend(results['items'])
        
        return tracks
    except Exception as e:
        # Catch other potential exceptions (like network errors)
        print(f"An error occurred: {e}")
        return []

def get_track_genre(artist_name: str, track_name: str) -> list:
    """
    Gets the top tags for a given track from Last.fm.
    ALWAYS returns a list (it will be empty if the track is not found).
    """
    lastfm_network = authenticate_lastfm()
    try:
        search_results = lastfm_network.search_for_track(artist_name, track_name)
        search_page = search_results.get_next_page()

        if not search_page:
            return []

        # Find the first track in the results that matches the artist's name
        best_match = None
        for track in search_page:
            # Compare the artist names (case-insensitive)
            if track.artist and track.artist.name and track.artist.name.lower() == artist_name.lower() and track.get_top_tags(limit=1) != []:
                best_match = track
                break # Stop as soon as we find the first correct match

        # If we found a match, get its tags
        if best_match:
            top_tags = best_match.get_top_tags(limit=5)
            if best_match.artist and best_match.artist.name:
                print(f"Matched '{track_name}' to '{best_match.title}' by '{best_match.artist.name}' -> Tags: {[tag.item.name for tag in top_tags]}")
            return top_tags
        else:
            # No track in the search results matched the artist
            print(f"-> No direct match found for '{track_name}' by '{artist_name}'.")
            return []


    #    track = lastfm_network.get_track(
    #        artist_name,
    #        track_name
    #    )
    #    top_tags = track.get_top_tags(limit=5) # pylast returns a list of TopItem objects
    #    print(f"Top tags for {track_name} by {artist_name}: {[tag.item.name for tag in top_tags]}")
    #    # If top_tags is empty, this will just return [] which is what we want
    #    if not top_tags:
    #        search_track = lastfm_network.search_for_track(artist_name, track_name)
    #        if search_track:
    #            print(f"Did you mean: {search_track}?")
    #    return top_tags

    except pylast.WSError:
        # Track not found on Last.fm, return an empty list
        print(f"Track not found on Last.fm: {track_name} by {artist_name}")
        return []
    except Exception as e:
        # Handle other potential errors (network, etc.)
        print(f"An error occurred fetching genre for {track_name}: {e}")
        return []
    
def find_playlist_by_name(sp, name: str) -> dict | None:
    """Finds a user's playlist by its exact name."""
    playlists = sp.current_user_playlists()
    
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == name:
                return playlist # Return the full playlist object if found
        
        # Check for more pages of playlists
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
            
    return None # Return None if no match is found

def filter_by_genre(sp, playlist_id: str, genre: str):
    """
    Filters tracks in a Spotify playlist by a specified genre.
    """

    raw_tracks = get_playlist_tracks(sp, playlist_id)
    if not raw_tracks:
        print("No tracks found in the playlist or an error occurred.")
        return []

    filtered_tracks = []
    tracks = [parsers.parse_spotify_playlist_item(track) for track in raw_tracks if track]
    for track in tracks:
        if not track:
            continue
        # Fetch the genre tags for the track
        top_tags = get_track_genre(track.artist, track.name)
        tag_names = [tag.item.name.lower() for tag in top_tags]

        if genre.lower() in tag_names:
            filtered_tracks.append(track)

    return filtered_tracks

def create_or_update_playlist(sp, user_id: str, playlist_name: str, track_uris: list[str]):
    """
    Finds a playlist by name. If it exists, replaces its tracks.
    If it doesn't exist, creates it and adds the tracks.
    """
    
    print(f"Checking for existing playlist named '{playlist_name}'...")
    existing_playlist = find_playlist_by_name(sp, playlist_name)

    if existing_playlist:
        # --- PLAYLIST EXISTS: REPLACE ITEMS ---
        playlist_id = existing_playlist['id']
        print(f"Found existing playlist. Updating tracks...")
        
        # Note: playlist_replace_items can only handle 100 tracks at a time
        # For simplicity, this assumes len(track_uris) <= 100
        # For real app, need to batch this call.
        sp.playlist_replace_items(playlist_id, track_uris)
        print("Playlist updated successfully.")
        
    else:
        # --- PLAYLIST DOES NOT EXIST: CREATE NEW ---
        print("No existing playlist found. Creating a new one...")
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Filtered tracks from another playlist."
        )
        playlist_id = new_playlist['id']
        
        # Add tracks to the newly created playlist
        # Note: playlist_add_items also has a 100-track limit per call
        sp.playlist_add_items(playlist_id, track_uris)
        print("New playlist created and tracks added.")
        
    return playlist_id