from flask import Blueprint, request, jsonify
from firebase_admin import firestore

track_blp = Blueprint("track", __name__, url_prefix="/api/spotify")
db = firestore.client()

@track_blp.route("/auth/login", methods=["POST"])
def spotify_login():
    return 

@track_blp.route("/auth/callback", methods=["POST"])
def spotify_callback():
    return 