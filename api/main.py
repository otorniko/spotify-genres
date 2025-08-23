import argparse
import services
import auth

# --- Main Logic ---
def main(playlist_name: str, genre: str):
    sp = auth.authenticate_spotify()
    user = sp.current_user()
    if not user or not user.get('id'):
        print("Could not retrieve user info. Exiting.")
        return
    user_id = user['id']
    print(f"Logged in as: {user['display_name']}")

    print(f"Searching for playlist '{playlist_name}'...")
    playlist = services.find_playlist_by_name(sp, playlist_name)
    
    if not playlist:
        print(f"Playlist '{playlist_name}' not found for user {user_id}.")
        return
    
    print("Filtering tracks by genre...")
    filtered_tracks = services.filter_by_genre(sp, playlist['id'], genre)
    
    if not filtered_tracks:
        print(f"No tracks found in playlist '{playlist_name}' matching genre '{genre}'.")
        return

    print(f"Found {len(filtered_tracks)} tracks matching '{genre}'.")

    track_uris = [track.uri for track in filtered_tracks]
    genre_playlist_name = f"{genre.title()}"
    genre_playlist = services.create_or_update_playlist(sp, user_id, genre_playlist_name, track_uris)
    
    if genre_playlist:
        print(f"Playlist '{genre_playlist_name}' is ready with {len(track_uris)} tracks.")
    else:
        print("Failed to create or update the genre playlist.")
    return genre_playlist

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter a Spotify playlist by genre.")
    parser.add_argument("playlist_name", type=str, help="The exact name of the playlist to filter.")
    parser.add_argument("genre", type=str, help="The genre to filter by (e.g., 'rock', 'techno').")
    args = parser.parse_args()
    main(args.playlist_name, args.genre)