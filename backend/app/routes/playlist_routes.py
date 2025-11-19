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
    new_playlists_name = ["happiness", "excited", "aggro", "sorrow", "nervous"]
    emotions_mapping = {
        "happiness" : "행복",
        "excited" : "신남",
        "aggro" : "화남",
        "sorrow" : "슬픔",
        "nervous" : "긴장" }

    # --- 여기서부터 spotify API 사용
    """
    1. 가진 재생목록 가져오기 API - **Get Current User's Playlists**
        - 호출 예시
            
            curl --request GET \
            --url https://api.spotify.com/v1/me/playlists \
            --header 'Authorization: Bearer {access_token}'        
        
        ⇒ 반환값 중 items 내 description, id 사용, 설명이 일치하는 게 있으면 DB에도 겹치는 문서가 있는지 확인 후 제외.
            겹치는 문서가 없다면 spotify에는 있는데 db에는 없는 것이므로 에러
            TODO - 된다면 이 경우에 에러 나게 하지말고, playlist, users, palylisthistory 컬렉션에 있는 내용을 업뎃하도록 수정
        
    2. 사용자 프로필 get API - **Get Current User's Profile**
        - 호출 예시
            
            curl --request GET \
            --url https://api.spotify.com/v1/me \
            --header 'Authorization: Bearer {access_token}'
            
        ⇒ 반환값 중 id 사용 (spotify 고유 사용자 id string임, 재생목록 생성 API에 사용됨)
        
    3. 재생목록 생성 API - **Create Playlist**
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
    
    # 사용자 소유 재생목록 가져오기 API
    SPOTIFY_GET_PLAYLIST_URL = "https://api.spotify.com/v1/me/playlists"
    get_playlist_header = { "Authorization": f"Bearer {spotifyToken}" }
    get_playlist_params = { "limit" : 50 }
    try:
        get_playlist_response = requests.get(SPOTIFY_GET_PLAYLIST_URL, headers=get_playlist_header, params=get_playlist_params)
        get_playlist_response.raise_for_status()
        
        curr_playlists = get_playlist_response.json().get("items")
        for item in curr_playlists:
            description = item.get("description")  # 뮤지기 관련 플리만 고정 패턴
            item_id = item.get("id")    # 뮤지기 관련 플리 id
            
            # description 패턴 기반 역매핑
            for eng, kor in emotions_mapping.items():
                if description == f"뮤지기 - 감정 {kor}에 맞는 플리":
                    if eng in new_playlists_name:
                        try:
                            playlist_doc = db.collection("Playlist").document(item_id).get()
                            if not playlist_doc.exists:
                                return jsonify({"error" : f"spotify에는 있는데 DB에는 없음. 감정: {kor}"}), 500
                        except Exception as e:
                            error_msg = str(e)
                            return jsonify({"error":f"DB 접근하다 오류난 듯... : {error_msg}"}), 500
                        
                        new_playlists_name.remove(eng)
                        
        if (len(new_playlists_name) == 0):                
            return jsonify({"error" : f"이미 다 있음"}), 400    
                
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        return jsonify({"error" : f"소유 재생목록 못가져옴: {error_msg}"}), 500
    
    
    # 사용자 프로필 가져오기 API
    SPOTIFY_GET_PROFILE_URL = "https://api.spotify.com/v1/me"
    profile_header = { "Authorization": f"Bearer {spotifyToken}" }
    try:
        get_profile_response = requests.get(SPOTIFY_GET_PROFILE_URL, headers=profile_header)
        get_profile_response.raise_for_status()
        
        spotifyId = get_profile_response.json().get("id") # spotify 고유 id 저장
        
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        return jsonify({"error" : f"사용자 프로필 못 가져왔음 {error_msg}"}), 500
    
    
    # 재생목록 생성 API
    SPOTIFY_CREATE_PLAYLIST_URL = f"https://api.spotify.com/v1/users/{spotifyId}/playlists"
    create_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    new_playlists_ids = {}
    try:
        for new in new_playlists_name:
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
            new_playlists_ids[new] = new_id # 영어로 저장
                    
    except requests.exceptions.HTTPError as http_e:
        http_e_msg = str(http_e)
        return jsonify({"error" : f"Spotify쪽에서 재생목록 생성 실패 : {http_e_msg}"}), 500
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"뮤지기쪽의 문제로 재생목록 생성 실패 : {error_msg}"}), 500
    
    
    # --- 여기서부터 DB 조작
    # 재생목록 존재 여부 확인 - 어플에서 지우고 db 업뎃 안됐을 수 있음
    try:
        playlist_ref = db.collection("Playlist").where("userDocId", "==", userDocId)
        playlists = playlist_ref.stream()
        
        for play in playlists:
            data = play.to_dict()
            emotionName = data["emotionName"]
            playlistDocId = data["playlistId"]

            if emotionName in new_playlists_name:
                # PlaylistHistory 컬렉션에서 playlistId가 같은 문서 삭제
                history_ref = db.collection("PlaylistHistory").where("playlistId", "==", playlistDocId)
                history_docs = history_ref.stream()
                for hist in history_docs:
                    hist.reference.delete()

                # Playlist 컬렉션의 문서 삭제
                play.reference.delete()
        
    except Exception as e:
        return jsonify({"error" : f"오류 발생 : {e}"}), 500
    
    
    # 생성된 재생목록 db에 저장하기
    try:
        for emo in new_playlists_ids.keys():        
            
            # Firestore - Playlist 컬렉션            
            new_playli = db.collection("Playlist").document(new_playlists_ids.get(emo))
            new_data = {
                "emotionName" : f"{emo}", # 영어가 들어감
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
    
    return jsonify({"playlistIds" : new_playlists_ids}), 201

# 선호 여부 기록 -> 재생목록 내 음악 추가 API
@playlist_blp.route("/<emotionName>/add", methods=["POST"])
@login_required
def addTrackToPlaylist(curr_user):
    """
    1-2. 재생목록 존재 여부를 확인한다.
    1-3.1. 재생목록이 존재하지 않으면 생성 API를 부르고 마저 진행된다.
    1-3.2. 재생목록이 있다면 해당하는 감정 재생목록에 저장된다.
           (spotify, firestore 모두 반영)
    """
    
    
    """
    사용할 Spotify API - Add Items to Playlist
    - 호출 예시
        curl --request POST \
        --url [https://api.spotify.com/v1/playlists/{playlist_id}/tracks] \
        --header 'Authorization: Bearer {access_token}' \
        --header 'Content-Type: application/json' \
        --data '{
            "uris": ["spotify:track:{trackId}"], - 추가할 음악
            "position": 0 - 추가할 위치
        }'
        => 반환값: snapshot_id 인데 현재 재생목록의 버전값이래 다른 요청 시 쓸 수 있다니 참고
    """
    return 