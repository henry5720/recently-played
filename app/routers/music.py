import random
from pathlib import Path
from base64 import b64encode

import requests
from fastapi import APIRouter
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader

from ..core.lastfm import get_now_playing, get_recently_played, get_recent_tracks

router = APIRouter()

template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))


def bar_gen(bar_count: int) -> str:
    """Generate CSS for animated bars."""
    bar_css = ""
    left = 1
    for i in range(1, bar_count + 1):
        anim = random.randint(1000, 1350)
        bar_css += f".bar:nth-child({i})  {{ left: {left}px; animation-duration: {anim}ms; }}"
        left += 4
    return bar_css


def load_image_b64(url: str) -> str:
    """Load image and convert to base64."""
    if not url:
        return ""
    response = requests.get(url)
    return b64encode(response.content).decode("ascii")


def get_track_image(track: dict) -> str:
    """Extract image URL from track data."""
    images = track.get("image", [])
    for img in reversed(images):
        url = img.get("#text", "")
        if url:
            return url
    return ""


def make_svg(data: dict) -> str:
    """Generate SVG widget."""
    bar_count = 84
    content_bar = "".join(["<div class='bar'></div>" for _ in range(bar_count)])
    bar_css = bar_gen(bar_count)

    template = jinja_env.get_template("spotify.html.j2")

    if data == {} or data.get("item") is None:
        current_status = "Was playing:"
        recent_plays = get_recently_played()
        items = recent_plays.get("items", [])
        if not items:
            return template.render(
                contentBar=content_bar,
                barCSS=bar_css,
                artistName="No recent tracks",
                songName="",
                image="",
                status="",
            )
        recent_plays_length = len(items)
        item_index = random.randint(0, recent_plays_length - 1)
        item = items[item_index]["track"]
    else:
        item = data["item"]
        current_status = "Vibing to:"

    image_url = get_track_image(item)
    image = load_image_b64(image_url)
    artist_name = item.get("artist", {}).get("#text", "Unknown Artist").replace("&", "&amp;")
    song_name = item.get("name", "Unknown Track").replace("&", "&amp;")

    return template.render(
        contentBar=content_bar,
        barCSS=bar_css,
        artistName=artist_name,
        songName=song_name,
        image=image,
        status=current_status,
    )


@router.get("/")
async def get_widget():
    """Get the music widget SVG showing currently/recently played track."""
    data = get_now_playing()
    svg = make_svg(data)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "s-maxage=1"},
    )


@router.get("/recent")
async def get_recent(limit: int = 20, page: int = 1):
    """Get recently played tracks as JSON with pagination.
    
    - **limit**: Tracks per page (default: 20, max: 200)
    - **page**: Page number (default: 1)
    """
    if limit > 200:
        limit = 200
    if page < 1:
        page = 1
    
    data = get_recent_tracks(limit=limit, page=page)
    
    if not data or "recenttracks" not in data:
        return {
            "tracks": [],
            "page": page,
            "per_page": limit,
            "total_pages": 0,
            "total": 0,
        }
    
    attr = data["recenttracks"].get("@attr", {})
    tracks = data["recenttracks"].get("track", [])
    if not isinstance(tracks, list):
        tracks = [tracks]
    
    return {
        "tracks": [
            {
                "artist": t.get("artist", {}).get("#text", ""),
                "track": t.get("name", ""),
                "album": t.get("album", {}).get("#text", ""),
                "image": next(
                    (img.get("#text") for img in reversed(t.get("image", [])) if img.get("#text")),
                    "",
                ),
                "now_playing": t.get("@attr", {}).get("nowplaying") == "true",
                "date": t.get("date", {}).get("#text", ""),
            }
            for t in tracks
        ],
        "page": int(attr.get("page", page)),
        "per_page": int(attr.get("perPage", limit)),
        "total_pages": int(attr.get("totalPages", 0)),
        "total": int(attr.get("total", 0)),
    }
