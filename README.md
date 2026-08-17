# Spotify Listening Explorer

A small Python tool that pulls my own Spotify listening data and builds a static, interactive-feeling dashboard showing listening patterns:
- Top artists across different time ranges
- How recent taste compares with medium-term and all-time favourites
- Which artists are shared between two selected time ranges
- What time of day I listen most

Link: https://natalieglo.github.io/Spotify-Listening-Habits-Explorer/

## What it does

- Logs into Spotify (my own account) using OAuth and pulls top tracks, top artists, and recently played tracks via the Spotify Web API
- Builds a chart showing listening activity by hour of day using timestamps from recently played tracks
- Shows my top artists across three time ranges:
  - **Last 4 Weeks**
  - **Last 6 Months**
  - **All-Time**
- Lets users switch between the three time ranges using interactive buttons
- Highlights the currently selected time range using Spotify's green colour
- Compares the top 10 artists across all three time ranges and shows how many appear in all three
- Allows users to select **any two time ranges** and compare their top 10 artists
- Displays the artists that appear in both selected time ranges
- Generates a static website from the collected data — no live server is needed to view it

## How it works

Two scripts, run in order:

1. **`fetch_data.py`** — the only part that talks to Spotify. Logs in via OAuth (one-time browser login, then cached locally), pulls the data, and saves it to `spotify_data.json`.
2. **`build_site.py`** — reads that JSON file, generates the charts with matplotlib, and writes a static `index.html` + time chart image png into `/docs`, which GitHub Pages serves directly.

Splitting it this way means the deployed site never needs API credentials and loads instantly, since it's just static files reading from pre-fetched data rather than calling Spotify live on every visit.

## Running it locally

pip install -r requirements.txt


Create a `.env` file in the project root:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```
(Get these by registering a free app at
[developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))

Then:

python fetch_data.py    # pulls your data, opens a browser to log in
python build_site.py    # builds the static site into /docs
```
Open `docs/index.html` in a browser to preview it locally.

## Known limitations

- **Genre and popularity data aren't used.** Spotify removed `audio-features` entirely and stripped the `popularity` field (and unreliably returns `genres`). Rather than fake numbers where real ones no longer exist, the charts were redesigned around data Spotify still reliably provides - which is why "top artists" is shown as a ranked list, not a bar chart with no real value to measure.
- **Listening-time chart uses UTC**, not local time - a fix for a future version.
- **Data is a snapshot**, not live - re-run both scripts to refresh it.
- **Static dashboard**: Because the deployed site uses pre-generated data, visitors cannot currently log in with their own Spotify account and view their own statistics

## What's next

- Convert the hour-of-day chart from UTC to local time
- Add more listening-pattern visualisations
- Add an optional "Log in with your own Spotify" experience so visitors can explore their own listening data
- Automate data collection refresh and website updates button using GitHub Actions
- Expand the dashboard with additional statistics as Spotify's API makes more data available


## Stack

- Python
- Spotipy - Spotify Web API wrapper
- Matplotlib - data visualisation
- HTML/CSS/JavaScript - static interactive dashboard
- GitHub Pages - deployment
