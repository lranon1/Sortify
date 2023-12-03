from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization":"Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url,headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization" : "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url,headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    #print(json_result)
    if len(json_result) == 0:
        print("Artist not found...")
        return None
    return json_result[0]

def search_for_track(token, track_title):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_title}&type=track&limit=10"
    query_url = url + query
    result = get(query_url,headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    #print(json_result)
    if len(json_result) == 0:
        print("Track not found...")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def available_genres(token):
    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["genres"]
    #print(json_result)
    return json_result

def get_recommendations(token, artist, genre, track):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    query = f"?seed_artists={artist}&seed_genres={genre}&seed_tracks={track}"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


token = get_token()

print("Welcome to Spotify Recommender\n")

#menu turn into while
artist, genre, track = input("To get recommendations give one artist, one genre, and one track: ").split()

#for artist
artist_name = search_for_artist(token, artist)
#if artist_name == None: 
print(artist_name["name"])
artist_id = artist_name["id"]
songs = get_songs_by_artist(token, artist_id)
#print(songs)

for idx, song in enumerate(songs):
    print(f"{idx+1}. {song['name']}") 


#for genre
genres = available_genres(token)
if genre not in genres:
    print("No such genre exists...\n")

#for track
track_title = search_for_track(token, track)
#if track_title == None:
print(track_title["name"])
track_id = track_title["id"]

recommendations = get_recommendations(token, artist_id, genre, track_id)
for idx, song in enumerate(recommendations):
    print(f"{idx+1}. {song['name']}") 

