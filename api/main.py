from fastapi import FastAPI

from api.routers import music, callback, scrobble

app = FastAPI(
    title="Last.fm Widget API",
    description="Display recently played tracks and scrobble to Last.fm",
    version="1.0.0",
)

app.include_router(music.router, tags=["Widget"])
app.include_router(callback.router, prefix="/callback", tags=["Auth"])
app.include_router(scrobble.router, prefix="/scrobble", tags=["Scrobble"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
