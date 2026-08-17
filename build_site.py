import json
#not needed but keeping for history as i changed to have static page
#import base64
#from io import BytesIO
#from pydoc import html

import matplotlib
matplotlib.use("agg") 
import matplotlib.pyplot as plt



#reading spotify_data.json file
def load_data():
    with open("spotify_data.json", "r") as f:
        return json.load(f)


def make_top_artists_list_html(data, time_range="long_term"):
   artists = data["top_artists"][time_range][:10]
   items = "".join(
       f"<li>{i + 1}. {a['name']}</li>" 
       for i, a in enumerate(artists))
   return f"""
    <ul style="
    list-style: none; 
    text-align: center; 
    padding: 0;
    line-height: 1.8;
    ">
        {items}

   """

def make_listening_time_chart(data):
    from datetime import datetime

    hours_played = [0] * 24
    for item in data["recently_played"]:
        played_at = item.get("played_at")
        if not played_at:
            continue
        dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
        hours_played[dt.hour] += 1

    hours = list(range(24))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(hours, hours_played)
    ax.set_xlabel("Hour of Day (UTC)")
    ax.set_ylabel("Number of plays")
    ax.set_title("Listening Activity (last 50 plays)")
    ax.set_xticks(hours)
    fig.tight_layout()


    plt.savefig("docs/time_chart.png")
    plt.close(fig)

#comparing short term vs long term top artists
def get_comparison_stat(data):
    short_names = {a["name"] for a in data["top_artists"]["short_term"][:10]}
    medium_names = {a["name"] for a in data["top_artists"]["medium_term"][:10]}
    long_names = {a["name"] for a in data["top_artists"]["long_term"][:10]}
    comparison = short_names & medium_names & long_names  #intersection = names in both
    return len(comparison), comparison

#choosing 2 time periods and comparing artists from these
def get_artist_comparison(data, range1, range2):
    artists1 = {
        a["name"]
        for a in data["top_artists"][range1][:10]
    }

    artists2 = {
        a["name"]
        for a in data["top_artists"][range2][:10]
    }

    return sorted(artists1 & artists2)


def build():
    import os
    os.makedirs("docs", exist_ok=True)
    
    data = load_data()
    artists_list = make_top_artists_list_html(data)
    short_term_list = make_top_artists_list_html(data, time_range="short_term")
    medium_term_list = make_top_artists_list_html(data, time_range="medium_term")
    long_term_list = make_top_artists_list_html(data, time_range="long_term")
    print(long_term_list)

    short_artists = [a["name"] for a in data["top_artists"]["short_term"][:10]]
    medium_artists = [a["name"] for a in data["top_artists"]["medium_term"][:10]]
    long_artists = [a["name"] for a in data["top_artists"]["long_term"][:10]]   

    comparison_count, comparison_names = get_comparison_stat(data)

    make_listening_time_chart(data)

    html = f"""
        <head><title>My Spotify Listening Explorer</title></head>

        <style>
                body {{
                    background-color: #121212;
                    color: white;
                    font-family: Arial, sans-serif;
                }}
                h1, h2 {{
                    color: #1DB954;
                }}
                img {{
                    border-radius: 8px;
                }}
            </style>
        
        <body style="font-family: sans-serif; text-align: center; padding: 40px;">
            <h1>My Spotify Listening Explorer</h1>
            <br>

            <h2>Top Artists</h2>
            <p style="color: #888;">Data last updated: {data['fetched_at'][:10]}</p>
            {artists_list}
            <br>

            <h2>Listening Activity</h2>
            <img src="time_chart.png" alt="Listening Chart"/>
            <br>

            <h2>Short term vs Medium term vs Long term Artists</h2>

                <button id="short-button"
                    onclick="showList('short-term')"
                    style="margin-right: 10px; padding: 8px 16px; background: #1DB954; color: white; border: none; border-radius: 20px; cursor: pointer;">
                    Last 4 Weeks
                </button>

                <button id="medium-button"
                    onclick="showList('medium-term')"
                    style="margin-right: 10px; padding: 8px 16px; background: #333; color: white; border: none; border-radius: 20px; cursor: pointer;">
                    Last 6 months
                </button>

                <button id="long-button"
                    onclick="showList('long-term')"
                    style="padding: 8px 16px; background: #333; color: white; border: none; border-radius: 20px; cursor: pointer;">
                    All-Time
                </button>

                <div id="short-term" style="display: block;">
                    {short_term_list}
                </div>
                <div id="medium-term" style="display: none;">
                    {medium_term_list}
                </div>
                <div id="long-term" style="display: none;">
                    {long_term_list}
                </div>

                <p>Total comparison: {comparison_count} artist(s) appear in both</p>
                
                <h2>Compare Time Ranges</h2>

                <div style="margin-bottom: 20px;">
                    <select id="compare-one"
                        style="padding: 8px 12px; border-radius: 20px; margin-right: 10px;">
                        <option value="short-term">Last 4 Weeks</option>
                        <option value="medium-term">Last 6 Months</option>
                        <option value="long-term">All-Time</option>
                    </select>

                    <select id="compare-two"
                        style="padding: 8px 12px; border-radius: 20px; margin-right: 10px;">
                        <option value="medium-term">Last 6 Months</option>
                        <option value="short-term">Last 4 Weeks</option>
                        <option value="long-term">All-Time</option>
                    </select>

                    <button onclick="compareArtists()"
                        style="padding: 8px 16px; background: #1DB954; color: white; border: none; border-radius: 20px; cursor: pointer;">
                        Compare
                    </button>
                </div>

                <div id="comparison-result"></div>
            
            
                <script>
                    const artistLists = {{
                        "short-term": {json.dumps(short_artists)},
                        "medium-term": {json.dumps(medium_artists)},
                        "long-term": {json.dumps(long_artists)}
                    }};

                    function showList(which) {{
                        document.getElementById('short-term').style.display = (which === 'short-term') ? 'block' : 'none';
                        document.getElementById('medium-term').style.display = (which === 'medium-term') ? 'block' : 'none';
                        document.getElementById('long-term').style.display = (which === 'long-term') ? 'block' : 'none';
                        document.getElementById('short-button').style.background = (which === 'short-term') ? '#1DB954' : '#333';
                        document.getElementById('medium-button').style.background = (which === 'medium-term') ? '#1DB954' : '#333'; 
                        document.getElementById('long-button').style.background = (which === 'long-term') ? '#1DB954' : '#333';
                    }}

                    function compareArtists() {{
                        const rangeOne = document.getElementById('compare-one').value;
                        const rangeTwo = document.getElementById('compare-two').value;

                        const artistsOne = artistLists[rangeOne];
                        const artistsTwo = artistLists[rangeTwo];

                        const sharedArtists = artistsOne.filter(artist => artistsTwo.includes(artist)
                        );

                        const result = document.getElementById('comparison-result');

                        if (sharedArtists.length === 0) {{
                            result.innerHTML = "<p>No artists appear in both top 10 lists.</p>";
                            return;
                        }}

                        result.innerHTML = `
                            <p><strong>${{sharedArtists.length}} artist(s) appear in both:</strong></p>
                            <ul style="
                                list-style: none;
                                padding: 0;
                                line-height: 1.8;
                            ">
                                ${{sharedArtists.map((artist, index) =>
                                    `<li>${{index + 1}}. ${{artist}}</li>`
                                ).join('')}}
                            </ul>
                        `;
                    }}
                </script>
            </body>
    </html>
    """

    with open("docs/index.html", "w") as f:
            f.write(html)

            print("Site built into /docs")

if __name__ == "__main__":
    build()