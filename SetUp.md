# Set Up Guide

## Last.fm

### 1. Create a Last.fm Account

* If you don't have one, register at [Last.fm](https://www.last.fm/join)

### 2. Connect Spotify to Last.fm

* Go to [Last.fm Settings > Applications](https://www.last.fm/settings/applications)
* Connect your Spotify account to enable scrobbling

### 3. Get API Key

* Go to [Last.fm API Account](https://www.last.fm/api/account/create)
* Create an API application (name can be anything like "My GitHub Widget")
* Take note of:
    * `API Key`

### 4. Get Your Username

* Your Last.fm username is visible in your profile URL: `https://www.last.fm/user/{USERNAME}`

## Vercel

* Register on [Vercel](https://vercel.com/)

* Fork this repo, then create a vercel project linked to it

* Add Environment Variables:
    * `https://vercel.com/<YourName>/<ProjectName>/settings/environment-variables`
        * `LASTFM_API_KEY` - Your Last.fm API key
        * `LASTFM_USERNAME` - Your Last.fm username

* Deploy!

## ReadMe

You can now use the following in your readme:

```[![Spotify](https://USER_NAME.vercel.app/api/spotify)](https://www.last.fm/user/USER_NAME)```

## Customization

If you want a distinction between the widget showing your currently playing, and your recently playing:

### Hide the EQ bar

Remove the `#` in front of `contentBar` in [line 81](https://github.com/novatorem/novatorem/blob/98ba4a8489ad86f5f73e95088e620e8859d28e71/api/spotify.py#L81) of current master, then the EQ bar will be hidden when you're in not currently playing anything.

### Status String

Have a string saying either "Vibing to:" or "Was playing:".

* Change [`height` to `height + 40`](https://github.com/novatorem/novatorem/blob/5194a689253ee4c89a9d365260d6050923d93dd5/api/templates/spotify.html.j2#L1-L2) (or whatever `margin-top` is set to)
* Uncomment [**.main**'s `margin-top`](https://github.com/novatorem/novatorem/blob/5194a689253ee4c89a9d365260d6050923d93dd5/api/templates/spotify.html.j2#L10)
* Uncomment [currentStatus](https://github.com/novatorem/novatorem/blob/5194a689253ee4c89a9d365260d6050923d93dd5/api/templates/spotify.html.j2#L93)

## Requests

Customization requests can be submitted as an issue.

If you want to share your own customization options, open a PR if it's done or open an issue if you want it implemented by someone else.

## Debugging

If you have issues setting up, try checking out the functions tab in vercel, linked as:
```https://vercel.com/{name}/spotify/{build}/functions``` 

<details><summary>Which looks like-</summary>

![image](https://user-images.githubusercontent.com/16753077/91338931-b0326680-e7a3-11ea-8178-5499e0e73250.png)

</details><br>

You will see a log there, and most issues can be resolved by ensuring you have the correct variables from setup.

## Migration from Spotify API

If you were previously using the Spotify API directly, you'll need to:

1. Remove old environment variables:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_SECRET_ID`
   - `SPOTIFY_REFRESH_TOKEN`

2. Add new Last.fm environment variables:
   - `LASTFM_API_KEY`
   - `LASTFM_USERNAME`

3. Make sure your Spotify account is connected to Last.fm for scrobbling to work.
