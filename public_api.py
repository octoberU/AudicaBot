from flask import Flask, request, abort, jsonify, send_from_directory
from tools import customs_database
from threading import Thread

import json
import time
import requests
import os

#ip_refresh_url = "http://sync.afraid.org/u/AKVCttkQ48nt8dxjmXSDfNsC/"

custom_songs_directory = "AUDICA" + os.sep + "CUSTOMS"
custom_songs_archive = "AUDICA" + os.sep + "CUSTOMS_ARCHIVE"

app = Flask(__name__)

# def ip_update_loop():
    # while True:
        # try:
            # r = requests.get(ip_refresh_url)
            # print(r.text)
            # time.sleep(300)
        # except Exception as e:
            # print("Error updating IP")
            # print(e)
            
# Tool to return custom songs data list
            
def get_customs_database(database, args):
    query = {"page": 1,
             "pagesize": 50,
             "search": "",
             "difficulty": "all",
             "artist": "",
             "mapper": "",
             "title": ""}
    pages = []
    for k, v in args:
        if k == "page":
            query["page"] = v
        elif k == "pagesize":
            query["pagesize"] = v
        elif k == "search":
            query["search"] = v
        elif k == "difficulty":
            query["difficulty"] = v
        elif k == "artist":
            query["artist"] = v
        elif k == "mapper":
            query["mapper"] = v
        elif k == "title":
            query["title"] = v
    temp_list = []
    for song in database.song_list:
        if query["difficulty"] == "all":
            temp_list.append(song)
        elif query["difficulty"] == "expert":
            if song["expert"] == True:
                temp_list.append(song)
        elif query["difficulty"] == "advanced":
            if song["advanced"] == True:
                temp_list.append(song)
        elif query["difficulty"] == "standard":
            if song["standard"] == True:
                temp_list.append(song)
        elif query["difficulty"] == "beginner":
            if song["beginner"] == True:
                temp_list.append(song)
    temp_list2 = []
    for song in temp_list:
        if query["search"] != "":
            if query["search"].lower() in song["author"].lower():
                temp_list2.append(song)
            elif query["search"].lower() in song["title"].lower():
                temp_list2.append(song)
            elif query["search"].lower() in song["artist"].lower():
                temp_list2.append(song)
        else:
            temp_list2.append(song)
    temp_list = []
    for song in temp_list2:
        if query["artist"] != "":
            if query["artist"].lower() in song["artist"].lower():
                temp_list.append(song)
        else:
            temp_list.append(song)
    temp_list2 = []
    for song in temp_list:
        if query["title"] != "":
            if query["title"].lower() in song["title"].lower():
                temp_list2.append(song)
        else:
            temp_list2.append(song)
    temp_list = []
    for song in temp_list2:
        if query["mapper"] != "":
            if query["author"].lower() in song["author"].lower():
                temp_list.append(song)
        else:
            temp_list.append(song)
    pages = []
    page = []
    page_ammount = 0
    total_ammount = 0
    for item in temp_list:
        page.append(item)
        page_ammount = page_ammount + 1
        total_ammount = total_ammount + 1
        if page_ammount == int(query["pagesize"]):
            pages.append(page)
            page = []
            page_ammount = 0
        elif len(temp_list) == total_ammount:
            pages.append(page)
            page = []
            page_ammount = 0
    songs = []
    pagesize = 0
    page_number = int(query["page"])
    try:
        songs = pages[int(query["page"]) - 1]
        pagesize = len(pages[int(query["page"]) - 1])
        
    except:
        page_number = 0
    songs = sorted(songs, key=lambda k: k["title"].lower())
    results = {"page": page_number,
               "total_pages": len(pages),
               "pagesize": pagesize,
               "song_count": len(temp_list),
               "songs": songs}
    print(query)
    return json.dumps(results)
    
# Welcome message for the main url

@app.route("/api")
def hello():
    return("Hello, this link is for an API to get Audica Bot's data.")
    
# Customs database download handling
    
@app.route("/api/customsongsfiles")
def list_custom_songs_files():
    files = []
    for filename in os.listdir(custom_songs_directory):
        path = os.path.join(custom_songs_directory, filename)
        if os.path.isfile(path):
            if ".audica" in filename:
                files.append(filename)
    return jsonify(files)

@app.route("/api/customsongsfiles/<path:path>")
def get_custom_song(path):
    return send_from_directory(custom_songs_directory, path, as_attachment=True)
    
# Archive database download handling
    
@app.route("/api/archivedsongsfiles")
def list_archived_songs_files():
    files = []
    for filename in os.listdir(custom_songs_archive):
        path = os.path.join(custom_songs_archive, filename)
        if os.path.isfile(path):
            if ".audica" in filename:
                files.append(filename)
    return jsonify(files)
    
@app.route("/api/archivedsongsfiles/<path:path>")
def get_archived_song(path):
    return send_from_directory(custom_songs_archive, path, as_attachment=True)
    
# Link to get custom songs data
    
@app.route("/api/customsongs")
def custom_songs():
    args = request.args
    database = customs_database()
    database.load()
    return get_customs_database(database, args.items())
    
@app.route("/api/customsongstotal")
def custom_songs_total():
    database = customs_database()
    database.load()
    authors = []
    for song in database.song_list:
        if song["author"] != "" and song["author"] not in authors:
            authors.append(song["author"])
    return json.dumps({"song_count":len(database.song_list),
                       "author_count":len(authors)})
    
# Link to get archived songs data
            
@app.route("/api/archivedsongs")
def archived_songs():
    args = request.args
    database = customs_database()
    database.folder = database.folder[:-1] + "_ARCHIVE" + os.sep
    database.filename = database.filename.replace("customs", "archive")
    database.load()
    return get_customs_database(database, args.items())
    
#Link to get pulled songs, this link should not be in the readme.
    
@app.route("/api/pulledsongs")
def pulled_songs():
    args = request.args
    database = customs_database()
    database.folder = database.folder[:-1] + "_PULLED" + os.sep
    database.filename = database.filename.replace("customs", "pulled")
    database.load()
    return get_customs_database(database, args.items())

    
if __name__ == '__main__':
    #ip_update_thread = Thread(target=ip_update_loop)
    #ip_update_thread.start()
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
    #app.run(host="127.0.0.1", port=5000, threaded=True, debug=True)