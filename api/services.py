import musicbrainzngs

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
    
def setup_musicbrainz():
    """
    Sets the user-agent for all future MusicBrainz API calls.
    This is required by their terms of service.
    """
    musicbrainzngs.set_useragent(
        "SpotifyGenreSorter",
        "0.1",
        "https://github.com/otorniko/spotify-genres"
    )
    print("MusicBrainz user-agent set.")

setup_musicbrainz()



def get_track_genre(artist_name: str, track_name: str) -> list[str]:
    """
    Finds the best-tagged track on MusicBrainz by searching and returns its genres.
    """
    try:
        result = musicbrainzngs.search_recordings(
            query=track_name, 
            artist=artist_name, 
            limit=5
        )

        recording_list = result.get('recording-list', [])
        if not recording_list:
            print(f"-> No result for '{track_name}' on MusicBrainz.")
            return []

        # --- Find the best-tagged match ---
        best_match = None
        for recording in recording_list:
            # Check 1: Does the recording have an artist and does the name match?
            artist_match = False
            if 'artist-credit' in recording and recording['artist-credit']:
                if recording['artist-credit'][0]['artist']['name'].lower() == artist_name.lower():
                    artist_match = True
            
            # Check 2: Does the recording have tags?
            has_tags = 'tag-list' in recording and recording['tag-list']
            
            # If both conditions are met, we've found our best match
            if artist_match and has_tags:
                best_match = recording
                break # Stop searching as soon as we find a good one

        # If we didn't find a perfect match, fall back to the first result
        if not best_match:
            best_match = recording_list[0]
            
        # --- End of Logic ---

        # Now, extract the tags from our chosen best_match
        genres = []
        if 'tag-list' in best_match:
            for tag in best_match['tag-list']:
                genres.append(tag['name'])
        
        print(f"Matched '{track_name}' to '{best_match['title']}' -> Tags: {genres}")
        return genres

    except musicbrainzngs.MusicBrainzError as e:
        print(f"A MusicBrainz error occurred for {track_name}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred for {track_name}: {e}")
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

def create_or_update_playlist(sp, user_id: str, playlist_name: str, track_uris: list[str]):
    """
    Finds a playlist by name. If it exists, replaces its tracks.
    If it doesn't exist, creates it and adds the tracks.
    Handles batching for playlists with more than 100 tracks.
    """
    
    # A helper function to break a list into chunks
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    if not track_uris:
        print("No tracks to add. Skipping playlist creation/update.")
        return None

    print(f"Checking for existing playlist named '{playlist_name}'...")
    existing_playlist = find_playlist_by_name(sp, playlist_name)

    if existing_playlist:
        # --- PLAYLIST EXISTS: REPLACE ITEMS IN BATCHES ---
        playlist_id = existing_playlist['id']
        print(f"Found existing playlist. Updating {len(track_uris)} tracks...")

        # The first batch uses playlist_replace_items to clear the playlist
        uri_chunks = list(chunks(track_uris, 100))
        sp.playlist_replace_items(playlist_id, uri_chunks[0])

        # Subsequent batches use playlist_add_items
        for chunk in uri_chunks[1:]:
            sp.playlist_add_items(playlist_id, chunk)
        
        print("Playlist updated successfully.")
        return existing_playlist # Return the existing playlist object
        
    else:
        # --- PLAYLIST DOES NOT EXIST: CREATE NEW AND ADD IN BATCHES ---
        print("No existing playlist found. Creating a new one...")
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Filtered for a specific genre by your app."
        )
        playlist_id = new_playlist['id']
        
        # Add all tracks in batches of 100
        for chunk in chunks(track_uris, 100):
            sp.playlist_add_items(playlist_id, chunk)
            
        print("New playlist created and tracks added.")
        return new_playlist # Return the new playlist object