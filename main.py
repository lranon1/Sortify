from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json
import time

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

def get_artist(token, url):
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["artists"]
    return json_result[0]

def get_related_artists(token, id):
    url = f"https://api.spotify.com/v1/artists/{id}/related-artists"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["artists"]
    return json_result

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
    #print(json_result)
    return json_result

def simplify_result(token, r):
    simple = []
    for song in r:
        art = get_artist(token, song['href'])
        title = song['name']
        simple.append(f"{title} by {art["name"]}")
    return simple

def merge_sort(r): #by lexicographical
    if len(r) > 1:
        front = r[:len(r)//2]
        back = r[len(r)//2:]

        merge_sort(front)
        merge_sort(back)

        f = 0
        b = 0
        idx = 0

        while f < len(front) and b < len(back):
            if front[f] < back[b]:
                r[idx] = front[f]
                f += 1
            else:
                r[idx] = back[b]
                b += 1
            idx += 1
        
        while f < len(front):
            r[idx] = front[f]
            f += 1
            idx += 1

        while b < len(back):
            r[idx] = back[b]
            b += 1
            idx += 1



print("Welcome to Sortify\n")

opt = "-1"

while opt != "0":
    token = get_token()

    print("Options\n")
    print("1. Get an artist's top songs")
    print("2. Get related artists")
    print("3. Get recommendations based on artist, genre, and track")
    print("Press 0 to exit")
    opt = input("Enter option: ")

    if opt == "1":
        artist = input("Enter an artist: ")
        artist_name = search_for_artist(token, artist)
        if artist_name == None:
            continue
        else:
            print(f"Best artist match: {artist_name["name"]}\n")
            artist_id = artist_name["id"]

            print("Getting tracks...\n")
            songs = get_songs_by_artist(token, artist_id)

            simple = simplify_result(token, songs)
            quickSimple = simplify_result(token, songs)

            print("Merge sorting...\n")
            start = time.time()
            merge_sort(simple)
            end = time.time()-start
            print(f"{end} seconds\n")

            print("Quick sorting...\n")
            qstart = time.time()
            quicksort(quickSimple, 0, len(quickSimple) - 1)
            qend = time.time() - qstart
            print(f"{qend} seconds\n")


            print("Top Tracks:\n")
            for idx, s in enumerate(simple):
                print(f"{idx+1}. {simple[idx]}") 

            print("Top Quick Sorted Tracks:\n")
            for idx, s in enumerate(quickSimple):
                print(f"{idx+1}. {quickSimple[idx]}")
                
    elif opt == "2":
        artist = input("Enter an artist: ")
        artist_name = search_for_artist(token, artist)
        if artist_name == None:
            continue
        else:
            print(f"Best artist match: {artist_name["name"]}\n")
            artist_id = artist_name["id"]
            related = get_related_artists(token, artist_id)

            simple = []
            for s in related:
                simple.append(s['name'])
            
            print("Merge sorting...\n")
            start = time.time()
            merge_sort(simple)
            end = time.time()-start
            print(f"{end} seconds\n")

            print("Related Artists:\n")
            for idx, s in enumerate(simple):
                print(f"{idx+1}. {simple[idx]}") 
    elif opt == "3":
        artist = input("Enter an artist: ")
        artist_name = search_for_artist(token, artist)
        if artist_name == None:
            continue
        else:
            print(f"Best artist match: {artist_name["name"]}\n")
            artist_id = artist_name["id"]

        genre = input("Enter a genre: ")
        genres = available_genres(token)
        if genre not in genres:
            print("No such genre exists...\n")
            continue

        track = input("Enter a track: ")
        track_title = search_for_track(token, track)
        #if track_title == None:
        print(f"Best track match: {track_title["name"]}\n")
        track_id = track_title["id"]

        print("Getting recommendations...\n")
        recommendations = get_recommendations(token, artist_id, genre, track_id)
        recommended = simplify_result(token, recommendations)

        print("Merge sorting...\n")
        start = time.time()
        merge_sort(recommended)
        end = time.time()-start
        print(f"{end} seconds\n")

        print("Recommended Tracks: \n")  
        for idx, song in enumerate(recommended):
            print(f"{idx+1}. {song}")
    elif opt == "0":
        print("Thank you for using Sortify!")
        break
    else:
        print("Invalid input.")   

    print("\n")

#swap values in an array
def swap(arr, i, j):
    #hold value of index to be changed in a temp
    temp = arr[i]
    #assign value at index j to index i
    arr[i] = arr[j]
    #assign original value in i to index j
    arr[j] = temp

#generate random index value for pivot
def randomPivot(low, high):
    return random.randint(low, high)

#quicksort algorithm
def quicksort(arr, low, high):
    if low < high:
        pivotIndex = randomPivot(low, high)
        pivotValue = arr[pivotIindex]

        #swap pivot with high, putting it last in arr
        swap(arr, pivotIndex, high)
        
        i = low - 1
        
        for j in range(low, high):
            if arr[j] < pivotValue:
                i+=1
                swap(arr, i, j)

        #swap pivot back into correct place in array 
        swap(arr, i+1, high)
        
        #recursive call to sort subarrays 
        quicksort(arr, low, i)
        quicksort(arr, i+2, high)


        
        

    
