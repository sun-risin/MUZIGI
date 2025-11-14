from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from app.routes.auth_routes import login_required
from app.schemas.playlist_schema import PlaylistSchema, PlaylistHistorySchema
from functools import wraps

playlist_blp = Blueprint("playlist", __name__, url_prefix="/api/playlist")
db = firestore.client()
playlist_schema = PlaylistSchema()
playlistHistory_schema = PlaylistHistorySchema()

# 재생목록 생성 API
@playlist_blp.route("/new", methods=["POST"])
@login_required
def createPlaylist(curr_user):
    data = request.get_json() # body - spotify의 액세스 토큰, spotifyToken
    return 