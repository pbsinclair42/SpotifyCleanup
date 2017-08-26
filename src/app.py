from flask import Flask, render_template, request, send_from_directory
from spotifyAPI import SpotifyAPI

app = Flask(__name__, static_url_path='')


@app.route('/user/')
def forUser():
    username = request.args['username']
    playlists = SpotifyAPI.getPlaylists(username)
    return render_template("playlists.html", username=username, playlists=playlists)


@app.route('/getDeadSongs/')
def getDeadSongs():
    id = request.args['id']
    owner = request.args['owner']
    name = request.args['owner']
    playlist = {'id': id, 'owner': owner, 'name': name}
    SpotifyAPI.getUnplayableTracksInPlaylist(playlist)
    return render_template("deadsongs.html", playlist=playlist)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/static/images/<path>')
def send_loading(path):
    return send_from_directory('static/images', path)


@app.route('/favicon.ico')
def fav():
    return "TODO"


if __name__ == "__main__":
    print("Hi")
    app.run()
