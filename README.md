# Spotify Cleanup

## What is it?
Spotify Cleanup allows you to easily fix your Spotify playlists, including de-duping songs, replacing dead tracks, and more!

## To run:

* Setup a new python virtual env for the project:
    ```
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

* Export the settings:
    ```
    cd src/
    export FLASK_APP=app.py
    ```

* Run the app:
    ```
    python -m flask run
    ```

## Collaborating:

Feel free to raise a new issue for any new feature or bug you've spotted.  Pull requests are also welcomed if you're interested in directly improving the project.
