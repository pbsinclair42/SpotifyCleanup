import re
from utils import httpRequest, buildUrl
from itertools import groupby
from datetime import timedelta
from base64 import urlsafe_b64encode
from math import isclose
from statistics import mean


class SpotifyAPI:
    MARKET = "GB"
    BASEURL = "https://api.spotify.com/v1/"
    DURATION_LEEWAY = 10000

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
        self.userDetails = UserDetails(response)

    def getPlaylists(self, username=None):
        if username is None:
            username = self.userDetails.username
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
                raise KeyError("Error getting user's playlists\n{}: {}", str(response['error']['status']),
                               response['error']['message'])
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
                    trackInfo = SpotifyAPI.extractTrackInfo(track)
                    unplayableTracks.append(trackInfo)
                    if not silent:
                        print(trackInfo)
            except KeyError as e:
                # local tracks can be safely ignored
                if "local" not in track['uri']:
                    raise e

        return unplayableTracks

    @staticmethod
    def extractTrackInfo(track):
        return {
            'title': track['name'],
            'spotifyID': track['id'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'albumArt': SpotifyAPI.extractAlbumArt(track),
            'duration': _millisecondsToString(track['duration_ms']),
            'added_at': track['added_at'].split('T')[0] if track['added_at'] != None else "Unknown",
            'index': track['index'],
            'preview_url': track['preview_url']
        }

    @staticmethod
    def extractArtists(track):
        return {normalize(artist['name']) for artist in track['artists']}

    @staticmethod
    def extractTitle(track):
        return normalize(track['name'])

    @staticmethod
    def extractAlbumArt(track):
        try:
            return track['album']['images'][0]['url']
        except IndexError:
            return "http://i1156.photobucket.com/albums/p580/keca-pooh22/albumart_mp_unknown.png"

    @staticmethod
    def getDuplicateTracks(tracks, silent=True):
        duplicates = []
        tracks = sorted(tracks, key=SpotifyAPI.extractTitle)
        for key, group in groupby(tracks, SpotifyAPI.extractTitle):
            # all tracks with the same name
            group = list(group)
            if len(group) > 1:
                # we believe two tracks to be equal if they share an artist and are roughly similar length
                # we also believe equality is transitive, ie if A shares an artist with B and B shares an artist with C,
                # and they're all similar lengths, we believe A, B, and C are all equal
                # each subgroup is a set of tracks we believe to be duplicates
                subgroups = []
                for track in group:
                    artists = set(SpotifyAPI.extractArtists(track))
                    duration = track['duration_ms']
                    newGroup = True
                    matches = [subgroup for subgroup in subgroups if len(artists.intersection(subgroup['artists'])) > 0
                               and isclose(duration, mean(subgroup['durations']), abs_tol=SpotifyAPI.DURATION_LEEWAY)]
                    if len(matches) > 0:
                        subgroups[:] = [subgroup for subgroup in subgroups if
                                        len(artists.intersection(subgroup['artists'])) == 0
                                        and not isclose(duration, mean(subgroup['durations']),
                                                        abs_tol=SpotifyAPI.DURATION_LEEWAY)]
                    newTracks = [track]
                    newArtists = artists
                    newDurations = {duration}
                    for subgroup in matches:
                        newTracks += subgroup['tracks']
                        newArtists.update(subgroup['artists'])
                        newDurations.update(subgroup['durations'])
                    subgroups.append({'artists': newArtists, 'tracks': newTracks, 'durations': newDurations})

                subgroups = map(lambda x: x['tracks'], subgroups)
                subgroups = list(filter(lambda group: len(group) > 1, subgroups))

                for group in subgroups:
                    group = list(map(SpotifyAPI.extractTrackInfo, group))
                    duplicates.append(group)
                    if not silent:
                        print(group)

        return duplicates

    def getPlaylistInfo(self, playlist, silent=True):
        tracks = self.getTracksInPlaylist(playlist)
        playlist['unplayableTracks'] = self.getUnplayableTracks(tracks, silent=silent)
        playlist['duplicateTracks'] = self.getDuplicateTracks(tracks, silent=silent)
        return playlist

    def removeTrackFromPlaylist(self, trackId, playlistId, index):
        url = self.BASEURL + "users/" + self.userDetails["id"] + "/playlists/" + playlistId + "/tracks"
        data = {"tracks": [{
            'positions': [int(index)],
            'uri': "spotify:track:" + trackId
        }]}
        headers = self.STANDARD_HEADERS
        headers['Content-Type'] = "application/json"
        headers['Accept'] = "application/json"
        return httpRequest(url, {}, headers, method="delete", data=data)


def _millisecondsToString(ms):
    string = str(timedelta(milliseconds=round(ms / 1000) * 1000))[0:7]
    while string[0] in '0:':
        string = string[1:]
    return string


def normalize(string):
    if ' - ' in string:
        string = string[:string.index(' - ')]
    while '(' in string and ')' in string:
        string = string[:string.index('(')] + string[string.index(')') + 1:]
        string = string.strip()
    string = re.sub('\W|_', '', string)
    return string.lower()


class UserDetails:
    def __init__(self, d):
        self.username = d['id']
        self.displayName = d['display_name']
        self.url = d['external_urls']['spotify']
        self.img = d['images'][0]['url']
