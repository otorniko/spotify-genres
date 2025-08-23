import services
import auth

# --- Main Logic ---
def main(user_id: str, playlist_name: str, genre: str):
    sp = auth.authenticate_spotify()
    playlist = services.find_playlist_by_name(sp, playlist_name)
    
    if not playlist:
        print(f"Playlist '{playlist_name}' not found for user {user_id}.")
        return
    
    filtered_tracks = services.filter_by_genre(sp, playlist['id'], genre)
    
    if filtered_tracks:
        print(f"Tracks in playlist '{playlist_name}' matching genre '{genre}':")
        for track in filtered_tracks:
            print(f"- {track['name']} by {track['artists'][0]['name']}")
    else:
        print(f"No tracks found in playlist '{playlist_name}' matching genre '{genre}'.")
    track_uris = [track['uri'] for track in filtered_tracks]
    genre_playlist_name = f"{genre.title()}"
    genre_playlist = services.create_or_update_playlist(sp, user_id, genre_playlist_name, track_uris)
    
    if genre_playlist:
        print(f"Playlist '{genre_playlist['name']}' is ready with {len(track_uris)} tracks.")
    else:
        print("Failed to create or update the genre playlist.")
    return genre_playlist