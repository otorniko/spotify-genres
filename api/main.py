import argparse
import logic
import parsers
import services
import auth
from models import Track
from utils import load_valid_genres, find_closest_genre

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
    
    # 1. FETCH & PARSE
    raw_items = services.get_playlist_tracks(sp, playlist['id'])
    parsed_items: list[Track | None] = [parsers.parse_spotify_playlist_item(item) for item in raw_items]

    # 2. CLEAN THE LIST
    # Create a new list containing only the actual Track objects, filtering out any None values.
    parsed_tracks: list[Track] = [track for track in parsed_items if track is not None]

    
    print("Filtering tracks by genre...")
    filtered_tracks = logic.filter_tracks_by_genre(parsed_tracks, genre)

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
    valid_genres = load_valid_genres()

    if args.genre in valid_genres:
        main(args.playlist_name, args.genre)
    else:
        suggestion = find_closest_genre(args.genre, valid_genres)
        if suggestion:
            print(f"Invalid genre: {args.genre}. Did you mean: {suggestion}?")
        else:
            print(f"Invalid genre: {args.genre}.")