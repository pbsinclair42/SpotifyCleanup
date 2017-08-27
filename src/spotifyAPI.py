from utils import httpRequest, buildUrl
from itertools import groupby
from datetime import timedelta
from base64 import urlsafe_b64encode

class SpotifyAPI():
    MARKET = "GB"
    BASEURL = "https://api.spotify.com/v1/"

    def __init__(self, client_id, client_secret):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

    def authenticate(self, redirect_uri):
        try:
            self.reauthenticate()
        except:
            self.getAuthenticationUrl(redirect_uri)

    def getAuthenticationUrl(self, redirect_uri):
        url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": "TODO",
            "scope": " ".join([
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-public",
                "playlist-modify-private"
            ])

        }
        return buildUrl(url, params, {}, method="get")

    def continueAuthentication(self, code, redirect_uri, state):
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
        self.finishAuthentication(params)
        self.getUserDetails()

    def finishAuthentication(self, params):
        url = "https://accounts.spotify.com/api/token"
        secret = self.CLIENT_ID + ":" + self.CLIENT_SECRET
        secret = secret.encode()
        headers = {
            "Authorization": "Basic " + urlsafe_b64encode(secret).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = httpRequest(url, params, headers, method="post")
        self.STANDARD_HEADERS = {
            "Authorization": response["token_type"] + " " + response['access_token']
        }
        self.refresh_token = response["refresh_token"]

    def reauthenticate(self):
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        self.finishAuthentication(params)

    def getUserDetails(self):
        url = self.BASEURL + "me"
        headers = self.STANDARD_HEADERS
        response = httpRequest(url, {}, headers)
        self.userDetails = response

    def getPlaylists(self, username="blackcat0030"):
        url = self.BASEURL + "users/" + username + "/playlists"
        params = {"limit": 50, "offset": 0}
        headers = self.STANDARD_HEADERS
        response = httpRequest(url, params, headers)

        playlists = []
        try:
            for playlist in response['items']:
                playlistInfo = {'id': playlist['id'], 'name': playlist['name'], 'owner': playlist['owner']['id']}
                playlists.append(playlistInfo)
            self.playlists = playlists
            return playlists
        except KeyError as e:
            if 'error' in response:
                exit(str.format("Error getting user's playlists\n{}: {}", str(response['error']['status']),
                                response['error']['message']))
            raise e

    def getNumberOfTracks(self, playlist):
        url = self.BASEURL + "users/" + playlist['owner'] + "/playlists/" + playlist['id']
        params = {"fields": "tracks(total)"}
        headers = self.STANDARD_HEADERS
        response = httpRequest(url, params, headers)
        try:
            return response['tracks']['total']
        except KeyError as e:
            if 'error' in response:
                exit(str.format("Error getting playlist info for '{}':\n{}: {}", playlist['name'],
                                str(response['error']['status']), response['error']['message']))
            raise e

    def getTracksInPlaylist(self, playlist, silent=True):
        url = self.BASEURL + "users/" + playlist['owner'] + "/playlists/" + playlist['id'] + "/tracks"
        params = {
            "fields": "items(added_at,track(name,id,uri,is_playable,artists(name),album(images),duration_ms,preview_url))",
            "market": self.MARKET
        }
        headers = self.STANDARD_HEADERS

        numTracks = self.getNumberOfTracks(playlist)

        tracks = []
        for offset in range(0, numTracks, 100):
            params["offset"] = offset
            response = httpRequest(url, params, headers)

            for i, item in enumerate(response['items']):
                track = item['track']
                track['added_at'] = item['added_at']
                track['index'] = i
                tracks.append(track)
        return tracks

    @staticmethod
    def getUnplayableTracks(tracks, silent=True):
        unplayableTracks = []
        for track in tracks:
            try:
                if not track['is_playable']:
                    trackInfo = {
                        'title': track['name'],
                        'spotifyID': track['id'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'albumArt': track['album']['images'][0]['url']
                    }
                    unplayableTracks.append(trackInfo)
                    if not silent:
                        print(trackInfo)
            except KeyError as e:
                # local tracks can be safely ignored
                if "local" not in track['uri']:
                    raise e

        return unplayableTracks

    @staticmethod
    def extractArtist(track):
        return [artist['name'] for artist in track['artists']]

    @staticmethod
    def extractTitle(track):
        return track['name']

    @staticmethod
    def extractDuration(track):
        return track['duration_ms']

    @staticmethod
    def getDuplicateTracks(tracks, silent=True):
        duplicates = []
        keyFunction = lambda track: {'artist': SpotifyAPI.extractArtist(track), 'title': SpotifyAPI.extractTitle(track)}
        tracks = sorted(tracks, key=lambda x: str(keyFunction(x)))
        for key, group in groupby(tracks, keyFunction):
            group = list(group)
            if len(group) > 1:
                group = list(map(lambda track: {
                    'title': track['name'],
                    'spotifyID': track['id'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'albumArt': track['album']['images'][0]['url'],
                    'added_at': track['added_at'],
                    'preview_url': track['preview_url'],
                    'index': track['index'],
                    'duration': _millisecondsToString(track['duration_ms'])
                }, group))
                duplicates.append(group)
                if not silent:
                    print(group)

        return duplicates

    def getPlaylistInfo(self, playlist, silent=True):
        tracks = self.getTracksInPlaylist(playlist)
        playlist['unplayableTracks'] = self.getUnplayableTracks(tracks, silent=silent)
        playlist['duplicateTracks'] = self.getDuplicateTracks(tracks, silent=silent)
        return playlist


def _millisecondsToString(ms):
    string = str(timedelta(milliseconds=round(ms / 1000) * 1000))[0:7]
    while string[0] in '0:':
        string = string[1:]
    return string
