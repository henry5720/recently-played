from typing import Optional

from fastapi import APIRouter, Header, Query, HTTPException

from ..core.config import settings
from ..core.lastfm import (
    get_now_playing,
    get_recent_tracks,
    get_top_tracks,
    get_loved_tracks,
    search_track,
    scrobble_track,
    update_now_playing,
)
from ..schemas.scrobble import ScrobbleRequest, ScrobbleResponse, ErrorResponse

router = APIRouter(prefix="/tracks", tags=["Tracks"])


def verify_token(token: Optional[str]) -> None:
    """Verify API token if configured."""
    if settings.SCROBBLE_API_TOKEN and token != settings.SCROBBLE_API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Invalid or missing API token"}
        )


def check_config() -> None:
    """Check required configuration."""
    if not settings.LASTFM_API_SECRET or not settings.LASTFM_SESSION_KEY:
        raise HTTPException(
            status_code=500,
            detail={"error": "Configuration error", "message": "LASTFM_API_SECRET or LASTFM_SESSION_KEY not set"}
        )


@router.get("")
async def get_recent(
    limit: int = 20,
    page: int = 1,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
):
    """Get recently played tracks.
    
    - **limit**: Tracks per page (default: 20, max: 200)
    - **page**: Page number (default: 1)
    - **from_ts**: Start timestamp (Unix timestamp, optional)
    - **to_ts**: End timestamp (Unix timestamp, optional)
    """
    if limit > 200:
        limit = 200
    if page < 1:
        page = 1
    
    data = get_recent_tracks(limit=limit, page=page, from_ts=from_ts, to_ts=to_ts)
    
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
                "name": t.get("name", ""),
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


@router.get("/now")
async def get_nowplaying():
    """Get currently playing track."""
    data = get_now_playing()
    
    if not data or "item" not in data:
        return {"is_playing": False, "track": None}
    
    track = data["item"]
    return {
        "is_playing": True,
        "track": {
            "artist": track.get("artist", {}).get("#text", ""),
            "name": track.get("name", ""),
            "album": track.get("album", {}).get("#text", ""),
            "image": next(
                (img.get("#text") for img in reversed(track.get("image", [])) if img.get("#text")),
                "",
            ),
        },
    }


@router.get("/top")
async def get_top(
    period: str = "overall",
    limit: int = 50,
    page: int = 1,
):
    """Get user's top tracks.
    
    - **period**: Time period - overall | 7day | 1month | 3month | 6month | 12month
    - **limit**: Results per page (default: 50, max: 1000)
    - **page**: Page number (default: 1)
    """
    valid_periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
    if period not in valid_periods:
        period = "overall"
    if limit > 1000:
        limit = 1000
    if page < 1:
        page = 1
    
    data = get_top_tracks(period=period, limit=limit, page=page)
    
    if not data or "toptracks" not in data:
        return {"tracks": [], "page": page, "per_page": limit, "total_pages": 0, "total": 0}
    
    attr = data["toptracks"].get("@attr", {})
    tracks = data["toptracks"].get("track", [])
    if not isinstance(tracks, list):
        tracks = [tracks]
    
    return {
        "tracks": [
            {
                "name": t.get("name", ""),
                "artist": t.get("artist", {}).get("name", ""),
                "playcount": int(t.get("playcount", 0)),
                "url": t.get("url", ""),
                "image": next(
                    (img.get("#text") for img in reversed(t.get("image", [])) if img.get("#text")),
                    "",
                ),
            }
            for t in tracks
        ],
        "period": period,
        "page": int(attr.get("page", page)),
        "per_page": int(attr.get("perPage", limit)),
        "total_pages": int(attr.get("totalPages", 0)),
        "total": int(attr.get("total", 0)),
    }


@router.get("/loved")
async def get_loved(limit: int = 50, page: int = 1):
    """Get user's loved tracks.
    
    - **limit**: Results per page (default: 50, max: 1000)
    - **page**: Page number (default: 1)
    """
    if limit > 1000:
        limit = 1000
    if page < 1:
        page = 1
    
    data = get_loved_tracks(limit=limit, page=page)
    
    if not data or "lovedtracks" not in data:
        return {"tracks": [], "page": page, "per_page": limit, "total_pages": 0, "total": 0}
    
    attr = data["lovedtracks"].get("@attr", {})
    tracks = data["lovedtracks"].get("track", [])
    if not isinstance(tracks, list):
        tracks = [tracks]
    
    return {
        "tracks": [
            {
                "name": t.get("name", ""),
                "artist": t.get("artist", {}).get("name", ""),
                "url": t.get("url", ""),
                "date": t.get("date", {}).get("#text", ""),
                "image": next(
                    (img.get("#text") for img in reversed(t.get("image", [])) if img.get("#text")),
                    "",
                ),
            }
            for t in tracks
        ],
        "page": int(attr.get("page", page)),
        "per_page": int(attr.get("perPage", limit)),
        "total_pages": int(attr.get("totalPages", 0)),
        "total": int(attr.get("total", 0)),
    }


@router.get("/search")
async def search(
    q: str,
    artist: Optional[str] = None,
    limit: int = 30,
    page: int = 1,
):
    """Search for tracks.
    
    - **q**: Track name to search
    - **artist**: Filter by artist name (optional)
    - **limit**: Results per page (default: 30)
    - **page**: Page number (default: 1)
    """
    data = search_track(track=q, artist=artist, limit=limit, page=page)
    
    if not data or "results" not in data:
        return {"tracks": [], "total": 0}
    
    results = data["results"]
    tracks = results.get("trackmatches", {}).get("track", [])
    if not isinstance(tracks, list):
        tracks = [tracks]
    
    return {
        "tracks": [
            {
                "name": t.get("name", ""),
                "artist": t.get("artist", ""),
                "url": t.get("url", ""),
                "listeners": int(t.get("listeners", 0)),
                "image": next(
                    (img.get("#text") for img in reversed(t.get("image", [])) if img.get("#text")),
                    "",
                ),
            }
            for t in tracks
        ],
        "total": int(results.get("opensearch:totalResults", 0)),
        "page": int(results.get("opensearch:Query", {}).get("startPage", 1)),
        "per_page": int(results.get("opensearch:itemsPerPage", limit)),
    }


@router.post(
    "/scrobble",
    response_model=ScrobbleResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def scrobble(
    body: ScrobbleRequest,
    x_api_token: Optional[str] = Header(default=None, alias="X-API-Token"),
    token: Optional[str] = Query(default=None),
):
    """Scrobble a track to Last.fm.
    
    - **artist**: Artist name (required)
    - **track**: Track name (required)  
    - **action**: Either "scrobble" or "nowplaying" (default: scrobble)
    
    Authentication (optional):
    - Header: `X-API-Token: YOUR_TOKEN`
    - Query param: `?token=YOUR_TOKEN`
    """
    verify_token(x_api_token or token)
    check_config()

    try:
        if body.action == "nowplaying":
            result = update_now_playing(body.artist, body.track)
        else:
            result = scrobble_track(body.artist, body.track)

        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Last.fm error",
                    "message": result.get("message", "Unknown error"),
                    "lastfm_error": result.get("error"),
                }
            )

        return {
            "status": "ok",
            "action": body.action,
            "artist": body.artist,
            "track": body.track,
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Internal error", "message": str(e)})
