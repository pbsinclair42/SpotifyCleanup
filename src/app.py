from flask import Flask, render_template, request, redirect
from spotifyAPI import SpotifyAPI
from secrets import CLIENT_ID, CLIENT_SECRET
import json

app = Flask(__name__, static_url_path='')
api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)


@app.route('/manualClean/')
def manualClean():
    try:
        playlists = api.getPlaylists()
        return render_template("manualClean.html", username=api.userDetails.username, playlists=playlists)
    except AttributeError:
        return redirect('/authenticate')


@app.route('/getCleanupData/')
def getCleanupData():
    id = request.args['playlistId']
    owner = request.args['owner']
    name = request.args['playlistName']
    snapshot_id = request.args['snapshot_id']
    playlist = {'id': id, 'owner': owner, 'name': name, 'snapshot_id': snapshot_id}
    api.getPlaylistInfo(playlist)
    return json.dumps(playlist)


@app.route('/authenticate')
def startAuthentication():
    redirect_uri = "http://localhost:5000/authenticationCallback"  # request.base_url[:-13] + "/authenticationCallback/"
    print(redirect_uri)
    url = api.getAuthenticationUrl(redirect_uri)
    return redirect(url)


@app.route('/authenticationCallback/')
def continueAuthentication():
    redirect_uri = "http://localhost:5000/authenticationCallback"
    state = request.args['state']
    if 'code' in request.args.keys():
        # Access Granted
        code = request.args['code']
        try:
            api.continueAuthentication(code, redirect_uri, state)
        except Exception as e:
            print(e)
            return "Authentication failed"
        return redirect("/manualClean/")
    else:
        # Access Denied
        error = request.args['error']
        return error


@app.route('/delete/')
def delete():
    trackId = request.args['trackId']
    playlistId = request.args['playlistId']
    index = request.args['index']
    snapshot_id = request.args['snapshot_id']
    return json.dumps(api.removeTrackFromPlaylist(trackId, playlistId, index, snapshot_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/favicon.ico')
def fav():
    return "TODO"


if __name__ == "__main__":
    app.run()
