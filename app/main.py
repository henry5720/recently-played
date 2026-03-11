from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .routers import widget, callback, tracks, artists, albums, user

app = FastAPI(
    title="Last.fm API",
    description="Last.fm integration API - scrobble, stats, and widget",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/widget")


app.include_router(widget.router)
app.include_router(callback.router, prefix="/callback", tags=["Auth"])
app.include_router(tracks.router)
app.include_router(artists.router)
app.include_router(albums.router)
app.include_router(user.router)
