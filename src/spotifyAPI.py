from utils import getJSONResponse, postResponse


class SpotifyAPI():
    MARKET = "GB"
    BASEURL = "https://api.spotify.com/v1/"

    TOKEN = "BQByZymkWklpHQXwRBdavBLlquNmOvASnblLBJUdwFp18xqBud-thkdvT5PL08IUpU6znAfwM5OOsqZyiXY_m6mM9eaAvm5jpIxNzY7JEv0K8wZNs2ZCEsAghn5ua2klhFXjoimqgIUd_dKr9OgPHq1qRYXTKemhge5meQ"
    STANDARD_HEADERS = {"Authorization": "Bearer " + TOKEN}

    @staticmethod
    def authenticate():
        #TODO
        url = "https://accounts.spotify.com/api/token"
        params = {'grant_type': 'client_credentials'}
        headers = SpotifyAPI.STANDARD_HEADERS
        headers['Authorization'] = '56ec1ebecde8417abe1b020a3dd797de:xxxxxx'
        return postResponse(url, params, headers)

    @staticmethod
    def getPlaylists(username="spotify"):
        url = SpotifyAPI.BASEURL + "users/" + username + "/playlists"
        params = {"limit": 50, "offset": 0}
        headers = SpotifyAPI.STANDARD_HEADERS
        response = getJSONResponse(url, params, headers)

        toReturn = []
        try:
            for playlist in response['items']:
                playlistInfo = {'id': playlist['id'], 'name': playlist['name'], 'owner': playlist['owner']['id']}
                toReturn.append(playlistInfo)
            return toReturn
        except KeyError as e:
            if 'error' in response:
                exit("Error getting user's playlists\n" + str(response['error']['status']) + ": " + response['error']['message'])
            raise e

    @staticmethod
    def getNumberOfTracks(playlist):
        url = SpotifyAPI.BASEURL + "users/" + playlist['owner'] + "/playlists/" + playlist['id']
        params = {"fields": "tracks(total)"}
        headers = SpotifyAPI.STANDARD_HEADERS
        response = getJSONResponse(url, params, headers)
        try:
            return response['tracks']['total']
        except KeyError as e:
            if 'error' in response:
                exit("Error getting playlist info for '" + playlist['name'] + "':\n" + str(response['error']['status']) + ": " + response['error']['message'])
            raise e

    @staticmethod
    def getUnplayableTracksInPlaylist(playlist, silent=True):
        url = SpotifyAPI.BASEURL + "users/" + playlist['owner'] + "/playlists/" + playlist['id'] + "/tracks"
        params = {"fields": "items(track(name,id,uri,is_playable,artists(name),album(images)))", "market": SpotifyAPI.MARKET}
        headers = SpotifyAPI.STANDARD_HEADERS

        numTracks = SpotifyAPI.getNumberOfTracks(playlist)

        unplayableTracks = []
        for offset in range(0, numTracks, 100):
            params["offset"] = offset
            response = getJSONResponse(url, params, headers)
            #print(response)

            for item in response['items']:
                track = item['track']
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

        playlist['unplayableTracks'] = unplayableTracks


if __name__ == '__main__':
    playlists = SpotifyAPI.getPlaylists()
    for playlist in playlists[3]:
        SpotifyAPI.getUnplayableTracksInPlaylist(playlist, silent=True)
        print(len(playlist['unplayableTracks']))
