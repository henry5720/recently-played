from fastapi import APIRouter

from ..core.lastfm import get_user_info

router = APIRouter(prefix="/user", tags=["User"])


@router.get("")
async def get_info():
    """Get Last.fm user info."""
    data = get_user_info()
    
    if not data or "user" not in data:
        return {"error": "Unable to fetch user info"}
    
    user = data["user"]
    return {
        "name": user.get("name", ""),
        "realname": user.get("realname", ""),
        "url": user.get("url", ""),
        "country": user.get("country", ""),
        "playcount": int(user.get("playcount", 0)),
        "artist_count": int(user.get("artist_count", 0)),
        "track_count": int(user.get("track_count", 0)),
        "album_count": int(user.get("album_count", 0)),
        "image": next(
            (img.get("#text") for img in reversed(user.get("image", [])) if img.get("#text")),
            "",
        ),
        "registered": user.get("registered", {}).get("#text", ""),
    }
