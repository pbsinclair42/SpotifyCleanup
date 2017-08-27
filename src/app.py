from flask import Flask, render_template, request, redirect
from spotifyAPI import SpotifyAPI
from secrets import CLIENT_ID, CLIENT_SECRET

app = Flask(__name__, static_url_path='')
api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)


@app.route('/user/')
def forUser():
    try:
        username = request.args['username']
        playlists = api.getPlaylists(username)
        return render_template("playlists.html", username=username, playlists=playlists)
    except KeyError:
        return "Error: Unknown username"


@app.route('/getDeadSongs/')
def getDeadSongs():
    id = request.args['id']
    owner = request.args['owner']
    name = request.args['owner']
    playlist = {'id': id, 'owner': owner, 'name': name}
    api.getPlaylistInfo(playlist)
    return render_template("deadsongs.html", playlist=playlist)


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
        return redirect("/user/?username=" + api.userDetails['id'])
    else:
        # Access Denied
        error = request.args['error']
        return error


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/favicon.ico')
def fav():
    return "TODO"


if __name__ == "__main__":
    app.run()
