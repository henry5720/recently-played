import hashlib
import time
from typing import Optional

import requests

from .config import settings

LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"


def generate_api_sig(params: dict) -> str:
    """Generate Last.fm API signature."""
    sorted_params = sorted(params.items())
    sig_string = "".join([f"{k}{v}" for k, v in sorted_params])
    sig_string += settings.LASTFM_API_SECRET
    return hashlib.md5(sig_string.encode("utf-8")).hexdigest()


def get_recent_tracks(limit: int = 10, page: int = 1) -> dict:
    """Get recent tracks from Last.fm."""
    params = {
        "method": "user.getrecenttracks",
        "user": settings.LASTFM_USERNAME,
        "api_key": settings.LASTFM_API_KEY,
        "format": "json",
        "limit": limit,
        "page": page,
    }
    response = requests.get(LASTFM_API_URL, params=params)
    if response.status_code != 200:
        return {}
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {}


def get_now_playing() -> dict:
    """Get currently playing track."""
    data = get_recent_tracks(limit=1)
    if not data or "recenttracks" not in data:
        return {}
    tracks = data["recenttracks"].get("track", [])
    if not tracks:
        return {}
    track = tracks[0] if isinstance(tracks, list) else tracks
    if "@attr" in track and track["@attr"].get("nowplaying") == "true":
        return {"item": track, "is_playing": True}
    return {}


def get_recently_played() -> dict:
    """Get recently played tracks."""
    data = get_recent_tracks(limit=10)
    if not data or "recenttracks" not in data:
        return {"items": []}
    tracks = data["recenttracks"].get("track", [])
    if not tracks:
        return {"items": []}
    if not isinstance(tracks, list):
        tracks = [tracks]
    return {"items": [{"track": t} for t in tracks]}


def get_session_key(token: str) -> dict:
    """Exchange token for session key."""
    params = {
        "method": "auth.getSession",
        "api_key": settings.LASTFM_API_KEY,
        "token": token,
    }
    params["api_sig"] = generate_api_sig(params)
    params["format"] = "json"

    response = requests.post(LASTFM_API_URL, data=params)
    return response.json()


def scrobble_track(artist: str, track: str, timestamp: Optional[int] = None) -> dict:
    """Scrobble a track to Last.fm."""
    if timestamp is None:
        timestamp = int(time.time())

    params = {
        "method": "track.scrobble",
        "api_key": settings.LASTFM_API_KEY,
        "sk": settings.LASTFM_SESSION_KEY,
        "artist": artist,
        "track": track,
        "timestamp": str(timestamp),
    }
    params["api_sig"] = generate_api_sig(params)
    params["format"] = "json"

    response = requests.post(LASTFM_API_URL, data=params)
    return response.json()


def update_now_playing(artist: str, track: str) -> dict:
    """Update now playing status on Last.fm."""
    params = {
        "method": "track.updateNowPlaying",
        "api_key": settings.LASTFM_API_KEY,
        "sk": settings.LASTFM_SESSION_KEY,
        "artist": artist,
        "track": track,
    }
    params["api_sig"] = generate_api_sig(params)
    params["format"] = "json"

    response = requests.post(LASTFM_API_URL, data=params)
    return response.json()
