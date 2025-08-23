import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pylast
import config

def authenticate_spotify():
    # Use the variables from the config module
    sp_oauth = SpotifyOAuth(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri=config.SPOTIFY_REDIRECT_URI,
        scope="playlist-read-private playlist-modify-public playlist-modify-private"
    )
    return spotipy.Spotify(auth_manager=sp_oauth)

def authenticate_lastfm():
    lastfm_network = pylast.LastFMNetwork(
    api_key=config.LASTFM_API_KEY,
    api_secret=config.LASTFM_API_SECRET
    )
    return lastfm_network