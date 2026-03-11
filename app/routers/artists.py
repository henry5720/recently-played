from fastapi import APIRouter

from ..core.lastfm import get_top_artists, search_artist

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("/top")
async def get_top(
    period: str = "overall",
    limit: int = 50,
    page: int = 1,
):
    """Get user's top artists.
    
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
    
    data = get_top_artists(period=period, limit=limit, page=page)
    
    if not data or "topartists" not in data:
        return {"artists": [], "page": page, "per_page": limit, "total_pages": 0, "total": 0}
    
    attr = data["topartists"].get("@attr", {})
    artists = data["topartists"].get("artist", [])
    if not isinstance(artists, list):
        artists = [artists]
    
    return {
        "artists": [
            {
                "name": a.get("name", ""),
                "playcount": int(a.get("playcount", 0)),
                "url": a.get("url", ""),
                "image": next(
                    (img.get("#text") for img in reversed(a.get("image", [])) if img.get("#text")),
                    "",
                ),
            }
            for a in artists
        ],
        "period": period,
        "page": int(attr.get("page", page)),
        "per_page": int(attr.get("perPage", limit)),
        "total_pages": int(attr.get("totalPages", 0)),
        "total": int(attr.get("total", 0)),
    }


@router.get("/search")
async def search(q: str, limit: int = 30, page: int = 1):
    """Search for artists.
    
    - **q**: Artist name to search
    - **limit**: Results per page (default: 30)
    - **page**: Page number (default: 1)
    """
    data = search_artist(artist=q, limit=limit, page=page)
    
    if not data or "results" not in data:
        return {"artists": [], "total": 0}
    
    results = data["results"]
    artists = results.get("artistmatches", {}).get("artist", [])
    if not isinstance(artists, list):
        artists = [artists]
    
    return {
        "artists": [
            {
                "name": a.get("name", ""),
                "url": a.get("url", ""),
                "listeners": int(a.get("listeners", 0)),
                "image": next(
                    (img.get("#text") for img in reversed(a.get("image", [])) if img.get("#text")),
                    "",
                ),
            }
            for a in artists
        ],
        "total": int(results.get("opensearch:totalResults", 0)),
        "page": int(results.get("opensearch:Query", {}).get("startPage", 1)),
        "per_page": int(results.get("opensearch:itemsPerPage", limit)),
    }
