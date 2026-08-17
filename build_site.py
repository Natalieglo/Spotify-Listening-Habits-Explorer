import json
import base64
from io import BytesIO
from pydoc import html

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
    long_names = {a["name"] for a in data["top_artists"]["long_term"][:10]}
    comparison = short_names & long_names  #intersection = names in both
    return len(comparison), comparison



def build():
    import os
    os.makedirs("docs", exist_ok=True)
    
    data = load_data()
    artists_list = make_top_artists_list_html(data)
    short_term_list = make_top_artists_list_html(data, time_range="short_term")
    long_term_list = make_top_artists_list_html(data, time_range="long_term")
        
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

            <h2>Short term vs Long term Artists</h2>

                <div>
                    <button onclick="showList('short-term')" style="margin-right: 10px; padding: 8px 16px; background: #1DB954; color: white; border: none; border-radius: 20px; cursor: pointer;">Last 4 Weeks</button>
                    <button onclick="showList('long-term')" style="padding: 8px 16px; background: #333; color: white; border: none; border-radius: 20px; cursor: pointer;">All-Time</button>
                </div>

                <div id="short-term" style="display: block;">
                    {short_term_list}
                </div>
                <div id="long-term" style="display: none;">
                    {long_term_list}
                </div>
            
                <p>{comparison_count} artist(s) appear in both</p>


                <script>
                    function showList(which) {{
                        document.getElementById('short-term').style.display = (which === 'short-term') ? 'block' : 'none';
                        document.getElementById('long-term').style.display = (which === 'long-term') ? 'block' : 'none';
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