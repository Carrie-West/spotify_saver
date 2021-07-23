import os
import pandas as pd
import spotipy
import openpyxl
from spotipy.oauth2 import SpotifyOAuth


scope = "user-library-read"

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
redirect_url = "https://replit.com/@CarrieViolet"  # Would be replaced with the host website


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_url, open_browser=True, ))

song_data = pd.DataFrame([], columns=["Track Name", "Album", "Artist"])

playlists = sp.current_user_playlists()

while playlists:

    for i, playlist in enumerate(playlists['items']):
        print(".", end='')
        song_max = playlist["tracks"]["total"]
        song_count = 0
        songs = sp.playlist_items(playlist['id'], offset=song_count)

        while songs:  # Limit is set to 100 songs, need to be able to continue from there

            # continues to reset the API call at the last known point until max is reached
            songs = sp.playlist_items(playlist['id'], offset=song_count)
            for song in songs['items']:
                song_count = song_count + 1
                if song_data.empty:
                    song_data.loc[0] = [song['track']['name'], song['track']['album']['name'],
                                        song['track']['artists'][0]['name']]
                else:
                    song_data.loc[song_data.index[-1] + 1] = [song['track']['name'], song['track']['album']['name'],
                                                              song['track']['artists'][0]['name']]
            if song_count == song_max:
                songs = None
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

liked_songs = sp.current_user_saved_tracks(limit=50)
song_count = 0

while liked_songs:

    for song in liked_songs['items']:
        song_count = song_count + 1
        if song_data.empty:
            song_data.loc[0] = [song['track']['name'], song['track']['album']['name'],
                                song['track']['artists'][0]['name']]
        else:
            song_data.loc[song_data.index[-1] + 1] = [song['track']['name'], song['track']['album']['name'],
                                                      song['track']['artists'][0]['name']]
    if song_count == 50:
        liked_songs = sp.current_user_saved_tracks(limit=50, offset=song_count)
    else:
        liked_songs = None

album_count = 0
saved_albums = sp.current_user_saved_albums(limit=50, offset=album_count)
album_data = pd.DataFrame([], columns=["Album Name", "Artist"])
while saved_albums:

    for album in saved_albums['items']:
        album_count = album_count + 1
        if album_data.empty:
            album_data.loc[0] = [album['album']['name'], album['album']['artists'][0]['name']]
        else:
            album_data.loc[album_data.index[-1] + 1] = [album['album']['name'], album['album']['artists'][0]['name']]
    if album_count == 50:
        saved_albums = sp.current_user_saved_albums(limit=50, offset=album_count)
        album_count = 0
    else:
        saved_albums = None
print("Done!")
with pd.ExcelWriter('output.xlsx', engine='openpyxl', mode='w') as writer:
    song_data.to_excel(writer, sheet_name='Liked Songs and Playlists')
    album_data.to_excel(writer, sheet_name='Saved Albums')
os.remove('.cache')
