import os
import random
import requests

from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from flask import Flask, Response, render_template

load_dotenv(find_dotenv())

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")

LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"

app = Flask(__name__)


def getRecentTracks(limit=10):
    params = {
        "method": "user.getrecenttracks",
        "user": LASTFM_USERNAME,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit,
    }
    response = requests.get(LASTFM_API_URL, params=params)
    if response.status_code != 200:
        return {}
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {}


def nowPlaying():
    data = getRecentTracks(limit=1)
    if not data or "recenttracks" not in data:
        return {}
    tracks = data["recenttracks"].get("track", [])
    if not tracks:
        return {}
    track = tracks[0] if isinstance(tracks, list) else tracks
    if "@attr" in track and track["@attr"].get("nowplaying") == "true":
        return {"item": track, "is_playing": True}
    return {}


def recentlyPlayed():
    data = getRecentTracks(limit=10)
    if not data or "recenttracks" not in data:
        return {"items": []}
    tracks = data["recenttracks"].get("track", [])
    if not tracks:
        return {"items": []}
    if not isinstance(tracks, list):
        tracks = [tracks]
    return {"items": [{"track": t} for t in tracks]}


def barGen(barCount):
    barCSS = ""
    left = 1
    for i in range(1, barCount + 1):
        anim = random.randint(1000, 1350)
        barCSS += (
            ".bar:nth-child({})  {{ left: {}px; animation-duration: {}ms; }}".format(
                i, left, anim
            )
        )
        left += 4
    return barCSS


def loadImageB64(url):
    if not url:
        return ""
    response = requests.get(url)
    return b64encode(response.content).decode("ascii")


def getTrackImage(track):
    images = track.get("image", [])
    for img in reversed(images):
        url = img.get("#text", "")
        if url:
            return url
    return ""


def makeSVG(data):
    barCount = 84
    contentBar = "".join(["<div class='bar'></div>" for i in range(barCount)])
    barCSS = barGen(barCount)

    if data == {} or data.get("item") is None:
        currentStatus = "Was playing:"
        recentPlays = recentlyPlayed()
        items = recentPlays.get("items", [])
        if not items:
            return render_template(
                "spotify.html.j2",
                contentBar=contentBar,
                barCSS=barCSS,
                artistName="No recent tracks",
                songName="",
                image="",
                status="",
            )
        recentPlaysLength = len(items)
        itemIndex = random.randint(0, recentPlaysLength - 1)
        item = items[itemIndex]["track"]
    else:
        item = data["item"]
        currentStatus = "Vibing to:"

    imageUrl = getTrackImage(item)
    image = loadImageB64(imageUrl)
    artistName = item.get("artist", {}).get("#text", "Unknown Artist").replace("&", "&amp;")
    songName = item.get("name", "Unknown Track").replace("&", "&amp;")

    dataDict = {
        "contentBar": contentBar,
        "barCSS": barCSS,
        "artistName": artistName,
        "songName": songName,
        "image": image,
        "status": currentStatus,
    }

    return render_template("spotify.html.j2", **dataDict)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    data = nowPlaying()
    svg = makeSVG(data)

    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


if __name__ == "__main__":
    app.run(debug=True)
