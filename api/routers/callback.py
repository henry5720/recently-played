from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from api.core.config import settings
from api.core.lastfm import get_session_key

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def callback(token: str = Query(default=None)):
    """
    Handle Last.fm OAuth callback.
    
    - Without token: Show authorization button
    - With token: Exchange for session key
    """
    if not token:
        auth_url = f"https://www.last.fm/api/auth/?api_key={settings.LASTFM_API_KEY}"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Last.fm Authorization</title>
            <style>
                body {{ font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .btn {{ background: #d51007; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .btn:hover {{ background: #b50e06; }}
            </style>
        </head>
        <body>
            <h1>Last.fm Authorization</h1>
            <p>Click the button below to authorize this application:</p>
            <a class="btn" href="{auth_url}">Authorize with Last.fm</a>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    if not settings.LASTFM_API_SECRET:
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error</h1>
            <p>LASTFM_API_SECRET is not set. Please add it to your environment variables.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=500)

    result = get_session_key(token)

    if "session" in result:
        session_key = result["session"]["key"]
        username = result["session"]["name"]
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{ font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .success {{ color: #1db954; }}
                .key {{ background: #f0f0f0; padding: 15px; border-radius: 5px; word-break: break-all; font-family: monospace; }}
                .copy-btn {{ background: #1db954; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <h1 class="success">Authorization Successful!</h1>
            <p>Username: <strong>{username}</strong></p>
            <p>Your Session Key:</p>
            <div class="key" id="session-key">{session_key}</div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{session_key}'); this.textContent='Copied!';">
                Copy Session Key
            </button>
            <h2>Next Steps</h2>
            <ol>
                <li>Copy the session key above</li>
                <li>Add it to your Vercel environment variables as <code>LASTFM_SESSION_KEY</code></li>
                <li>Redeploy your application</li>
            </ol>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    else:
        error = result.get("error", "Unknown error")
        message = result.get("message", "No message")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Authorization Failed</h1>
            <p>Error {error}: {message}</p>
            <p><a href="/callback">Try again</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=400)
