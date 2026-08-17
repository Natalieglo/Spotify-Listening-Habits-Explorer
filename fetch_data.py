
#importing top tracks/artists

import json
import os
from datetime import datetime, timezone

from spotipy import Spotify
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

#loads SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI from .env file
load_dotenv()
#reading top tracks/artists and recently played tracks 
SCOPE = "user-top-read user-read-recently-played"

#connection to spotify's API using spotipy library and OAuth authentication
#SpotifyOAuth handles login and permission
#cache_path - after first login, the access token is saved in .spotify_cache file, so you don't have to log in again
sp = Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scope=SCOPE,
        cache_path=".spotify_cache",
    )
)

#gets top 50 tracks for specific time range: 
#'short_term' (last 4 weeks),
#'medium_term' (last 6 months),
#'long_term' (~years / all-time)
def get_top_tracks(time_range):
    results = sp.current_user_top_tracks(limit=50, time_range=time_range)
    tracks = results.get("items", [])

    #no listening history? return empty list
    if not tracks:
        return []

#combining top track info
    out = []
    for t in tracks:
        artists = t.get("artists") or []
        album = t.get("album") or {}
        out.append({
            "name": t.get("name"),
            "artist": artists[0].get("name") if artists else None,
            "id": t.get("id"),
            "album": album.get("name"),
        })
    return out

#same as above but for top artists instead of tracks
#genre included
def get_top_artists(time_range):
    results = sp.current_user_top_artists(limit=50, time_range=time_range)
    return [
        {
            "name": a.get("name"),
            "genres": a.get("genres"),
        }
        for a in results.get("items", [])
    ]

#gets last 50 played tracks, with artist name and time played
def get_recently_played():
    results = sp.current_user_recently_played(limit=50)
    out = []
    for item in results.get("items", []):
        t = item.get("track") or {}
        artists = t.get("artists") or []
        out.append({
            "name": t.get("name"),
            "artist": artists[0].get("name") if artists else None,
            "played_at": item.get("played_at"),
        })
    return out



#runs all 3 functions and saves the results to a JSON file (spotify_data.json)
def main():
    print("Fetching your Spotify data...")

    #updating tracks once in a while
    existing_history = []
    if os.path.exists("spotify_data.json"):
         with open("spotify_data.json", "r",encoding="utf-8") as f:
            try:
                old_data = json.load(f)
                existing_history = old_data.get("recently_played",[])
            except json.JSONDecodeError:
                pass # if file is empty/corrupt exception

    #getting new data, comparing it to old tracks using timestamp and adding new tracks
    new_data = get_recently_played()
    old_timestamps = {track["played_at"] for track in existing_history}
    new_tracks = [track for track in new_data if track["played_at"] not in old_timestamps]

    #new tracks placed at the top
    combined_history = (new_tracks + existing_history)[:1000] #add limit so JSON is manageable
             

    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "top_tracks": {
            "short_term": get_top_tracks("short_term"),
            "medium_term": get_top_tracks("medium_term"),
            "long_term": get_top_tracks("long_term"),
        },
        "top_artists": {
            "short_term": get_top_artists("short_term"),
            "medium_term": get_top_artists("medium_term"),
            "long_term": get_top_artists("long_term"),
        },
        "recently_played": combined_history,
    }

    with open("spotify_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Done. Saved {len(data['top_tracks']['long_term'])} long-term top tracks "
          f"and {len(data['recently_played'])} recently played tracks to spotify_data.json")



if __name__ == "__main__":
    main()