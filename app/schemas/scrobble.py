from typing import Literal

from pydantic import BaseModel


class ScrobbleRequest(BaseModel):
    artist: str
    track: str = ""
    action: Literal["scrobble", "nowplaying"] = "scrobble"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "artist": "ROSÉ - R",
                    "track": "Gone",
                    "action": "nowplaying"
                },
                {
                    "artist": "杜宣达 - 习惯性依赖",
                    "track": "",
                    "action": "scrobble"
                }
            ]
        }
    }


class ScrobbleResponse(BaseModel):
    status: str
    action: str
    artist: str
    track: str
    album: str = ""
    enriched: bool = False
    result: dict


class ErrorResponse(BaseModel):
    error: str
    message: str


class UsageResponse(BaseModel):
    status: str
    message: str
    usage: dict
