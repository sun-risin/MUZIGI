from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from app.routes.auth_routes import login_required
from app.schemas.playlist_schema import PlaylistSchema, PlaylistHistorySchema
import requests
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
    userDocId = curr_user.get("userDocId")
    # 생성 예정 재생목록 카테고리
    new_playlists = ["happiness", "excited", "aggro", "sorrow", "nervous"]
    emotions_mapping = {
        "happiness" : "행복",
        "excited" : "신남",
        "aggro" : "화남",
        "sorrow" : "슬픔",
        "nervous" : "긴장" }
    
    # 재생목록 존재 여부 확인
    try:
        playlist_ref = db.collection("Playlist").where("userDocId", "==", userDocId)
        playlists = playlist_ref.stream()
        
        for play in playlists:
            data = play.to_dict()
            emotionName = data["emotionName"]
            
            if emotionName in new_playlists:
                new_playlists.remove(emotionName)
        
        if (len(new_playlists) == 0):
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
            
        ⇒ 반환값 중 id 사용 (spotify 고유 사용자 id string임, 재생목록 생성 API에 사용됨)
        
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
        ⇒ 반환값 중 id 저장 (spotify에 생성한 재생목록 고유 id string)
    """
    
    request_data = request.get_json() # body - spotify의 액세스 토큰, spotifyToken
    spotifyToken = request_data["spotifyToken"]
    
    # 사용자 프로필 가져오기 API
    SPOTIFY_GET_PROFILE_URL = "https://api.spotify.com/v1/me"
    profile_header = { "Authorization": f"Bearer {spotifyToken}" }
    try:
        get_profile_response = requests.get(SPOTIFY_GET_PROFILE_URL, headers=profile_header)
        get_profile_response.raise_for_status()
        
        spotifyId = get_profile_response.json().get("id") # spotify 고유 id 저장
        
    except requests.exceptions.HTTPError as e:
        return jsonify({"error" : "사용자 프로필 못 가져왔음"}), 500
    
    
    # 재생목록 생성 API
    SPOTIFY_CREATE_PLAYLIST_URL = f"https://api.spotify.com/v1/users/{spotifyId}/playlists"
    create_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    new_playlists_ids = {}
    try:
        for new in new_playlists:
            emotion = emotions_mapping.get(new)
            create_data = {
                "name": f"{emotion}",
                "description": f"뮤지기 - 감정 {emotion}에 맞는 플리",
                "public": False
            }
            
            create_response = requests.post(SPOTIFY_CREATE_PLAYLIST_URL,
                                            json=create_data, headers=create_headers)
            create_response.raise_for_status()
            
            new_id = create_response.json().get("id")
            new_playlists_ids[emotion] = new_id
                    
    except requests.exceptions.HTTPError as http_e:
        http_e_msg = str(http_e)
        return jsonify({"error" : f"Spotify쪽에서 재생목록 생성 실패 : {http_e_msg}"}), 500
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"뮤지기쪽의 문제로 재생목록 생성 실패 : {error_msg}"}), 500
    
    
    # 생성된 재생목록 db에 저장하기
    try:
        for emo in new_playlists_ids.keys():        
            
            # Firestore - Playlist 컬렉션            
            new_playli = db.collection("Playlist").document(new_playlists_ids.get(emo))
            new_data = {
                "emotionName" : f"{emo}",
                "playlistId":  new_playli.id,
                "userDocId" : curr_user.get("userDocId")
            }
            playli_db_errors = playlist_schema.validate(new_data) # schema로 유효성 검사
            if playli_db_errors:                      
                return jsonify({ "error": f"유효하지 않은 입력값 : {playli_db_errors}" }), 400
            
            new_playli.set(new_data)
            
            # Firestore - users 컬렉션
            user_ref = db.collection("users").document(userDocId)
            user_doc = user_ref.get()
            if not user_doc.exists: 
                return jsonify({"error": "유효하지 않은 사용자입니다."}), 401
            
            user_ref.update({ # 추가! (수정이긴 한데 어쨌든...)
                f"playlistIds.{emo}": new_playli.id
            })
            
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"재생목록 생성 내용 DB에 저장 실패 : {error_msg}"}), 500