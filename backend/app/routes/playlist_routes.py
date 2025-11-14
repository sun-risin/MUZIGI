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
    1-2. 재생목록 존재 여부를 확인한다.
    1-3.1. 이미 감정 별 재생목록이 있다면 종료된다.
    1-3.2. 재생목록이 없는 게 있다면 새로 생성된다.
    """
    if not curr_user:
        return jsonify({"error" : "뮤지기 사용자 토큰 없음"}), 401
    
    # 생성 예정 재생목록 카테고리
    new_playlist = ["happiness", "excited", "aggro", "sorrow", "nervous"]
    
    # 재생목록 존재 여부 확인
    try:
        playlist_ref = db.collection("Playlist").where("userDocId", "==", curr_user["userDocId"])
        playlists = playlist_ref.stream()
        
        for play in playlists:
            data = play.to_dict()
            emotionName = data["emotionName"]
            
            if emotionName in new_playlist:
                new_playlist.remove(emotionName)
        
        if (len(new_playlist) == 0):
            return jsonify({"error" : "이미 재생목록 다 있다"}), 401
        
    except Exception as e:
        return jsonify({"error" : f"오류 발생 : {e}"}), 500
        
        
    # 여기서부터 spotify API 사용
    
    """
    1. 사용자 프로필 get API - **Get Current User's Profile**
        - 호출 예시
            
            curl --request GET \
            --url https://api.spotify.com/v1/me \
            --header 'Authorization: Bearer {access_token}'
            
        
        ⇒ 반환값 중 id 사용 (spotify 고유 사용자 id string임, 위 재생목록 API에 사용됨)
        
    2. 재생목록 생성 API - **Create Playlist**
        - 호출 예시
            
            curl --request POST \
            --url [https://api.spotify.com/v1/users/{user_id}/playlists](https://api.spotify.com/v1/users/smedjan/playlists) \
            --header 'Authorization: Bearer {access_token}' \
            --header 'Content-Type: application/json' \
            --data '{
            "name": "New Playlist",
            "description": "New playlist description",
            "public": false
            }'
    """
    
    request_data = request.get_json() # body - spotify의 액세스 토큰, spotifyToken
    spotifyToken = request_data["spotifyToken"]
    
    
    
    return 