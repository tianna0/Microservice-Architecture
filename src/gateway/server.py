import os, gridfs, pika, json 
#pika: use to interfrace with queue
#gridfs: allow to store larger file in mongodb
from flask import Flask, request, send_file
from flask_pymongo import PyMongo #use mongodb store files
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

#create server
server = Flask(__name__)

#pymongo: manages mangodb connections for flask app
mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")

mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

#login route: communicate with auth service to log the user in and assign a token to the user
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request) #request from flask

    if not err:
        return token
    else:
        return err

#upload route: used to upload vide that want to convert to mp3 
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access) #convert json string to python object

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1: #only allow one file at a time
            return "exactly 1 file required", 400

        for _, f in request.files.items(): #iterate through file
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)