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
    """
    1-2. 재생목록 생성 여부를 확인한다.
    1-3.1. 이미 감정 별 재생목록이 있다면 종료된다.
    1-3.2. 재생목록이 없는 게 있다면 새로 생성된다.
    """

    data = request.get_json() # body - spotify의 액세스 토큰, spotifyToken
    
    
    return 