# Spotify Listening Explorer

A small Python tool that pulls my own Spotify listening data and builds a static, interactive-feeling dashboard showing listening patterns — top artists, how recent taste compares to all-time favourites, and what time
of day I listen most.


## What it does

- Logs into Spotify (my own account) and pulls top tracks, top artists, and recently played tracks via the Spotify Web API
- Compares "last 4 weeks" vs. "all-time" top artists and shows the overlap between them
- Builds a chart of listening activity by hour of day, using real timestamps from recently played tracks
- Generates a static site from that data — no live server needed to view it

## How it works

Two scripts, run in order:

1. **`fetch_data.py`** — the only part that talks to Spotify. Logs in via OAuth (one-time browser login, then cached locally), pulls the data, and saves it to `spotify_data.json`.
2. **`build_site.py`** — reads that JSON file, generates the charts with matplotlib, and writes a static `index.html` + time chart image png into `/docs`, which GitHub Pages serves directly.

Splitting it this way means the deployed site never needs API credentials and loads instantly, since it's just static files reading from pre-fetched data rather than calling Spotify live on every visit.

## Running it locally

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```
(Get these by registering a free app at
[developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))

Then:
```bash
python fetch_data.py    # pulls your data, opens a browser to log in
python build_site.py    # builds the static site into /docs
```
Open `docs/index.html` in a browser to preview it locally.

## Known limitations

- **Genre and popularity data aren't used.** Spotify deprecated the
  `audio-features` endpoint entirely in late 2024 and stripped the
  `popularity` field (and unreliably returns `genres`) in a Feb 2026
  update. Rather than fake numbers where real ones no longer exist, the
  charts were redesigned around data Spotify still reliably provides —
  which is why "top artists" is shown as a ranked list, not a bar chart
  with no real value to measure.
- **Listening-time chart uses UTC**, not local time — a fix for a future
  version.
- **Data is a snapshot**, not live — re-run both scripts to refresh it.

## What's next

- Convert the hour-of-day chart to local time
- Add an optional "log in with your own Spotify" view so visitors can see
  their own stats (dropped from this version to hit a tighter timeline —
  the OAuth login flow itself already works, just isn't wired into the
  static site yet)
- Automate data refresh on a schedule via GitHub Actions

## Stack

Python, Spotipy, Matplotlib, static HTML/CSS, deployed via GitHub Pages.
