import os
from dotenv import load_dotenv

# This line loads the variables from your .env file into the environment
load_dotenv()

def get_required_env(var_name: str) -> str:
    """Gets a required environment variable or raises an error."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"'{var_name}' is not set in the environment or .env file.")
    return value

# --- Spotify ---
SPOTIFY_CLIENT_ID = get_required_env("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_required_env("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = get_required_env("SPOTIPY_REDIRECT_URI")

# --- Last.fm ---
LASTFM_API_KEY = get_required_env("LASTFM_API_KEY")
LASTFM_API_SECRET = get_required_env("LASTFM_API_SECRET")