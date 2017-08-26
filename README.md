# Spotify Cleanup

## What is it?
Spotify Cleanup allows you to easily fix your Spotify playlists, including de-duping songs, replacing dead tracks, and more!

## To run:

* Setup a new python virtual env for the project:
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

* Export the settings:
    cd src/
    export FLASK_APP=app.py

* Get yourself an API key from Spotify.  Visit [their API docs](https://developer.spotify.com/web-api/console/get-playlists/) and click the "GET OAUTH TOKEN" button, then copy the token it generates and replace the old token in spotifyAPI > SpotifyAPI > TOKEN

* Run the app:
    python -m flask run
