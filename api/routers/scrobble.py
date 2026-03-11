from typing import Optional

from fastapi import APIRouter, Header, Query, HTTPException

from ..core.config import settings
from ..core.lastfm import scrobble_track, update_now_playing
from ..schemas.scrobble import (
    ScrobbleRequest,
    ScrobbleResponse,
    ErrorResponse,
    UsageResponse,
)

router = APIRouter()


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


@router.get("/", response_model=UsageResponse)
async def get_usage():
    """Get API usage information."""
    return {
        "status": "ok",
        "message": "Scrobble API is running. Use POST to scrobble.",
        "usage": {
            "method": "POST",
            "body": {
                "artist": "Artist name (required)",
                "track": "Track name (required)",
                "action": "scrobble or nowplaying (optional, default: scrobble)"
            }
        }
    }


@router.post(
    "/",
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
    """
    Scrobble a track to Last.fm.
    
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
