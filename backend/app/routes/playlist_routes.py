from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from app.routes.auth_routes import login_required
import requests

# 서비스 레이어의 함수들 import
from app.services.playlist_services import (spotify_getCurrentUser,
                                            spotify_createPlaylist,
                                            spotify_getUserPlaylist,
                                            spotify_addItem,
                                            spotify_getItems,
                                            DB_checkPlaylist,
                                            DB_update,
                                            DB_checkHistory,
                                            DB_getHistory)

playlist_blp = Blueprint("playlist", __name__, url_prefix="/api/playlist")
db = firestore.client()
    
# --- 뮤지기 서비스 API들
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
    
    new_playlists_name = [
        "happiness", "excited", "aggro", "sorrow", "nervous"] 

    # --- 여기서부터 spotify API 사용    
    request_data = request.get_json() # body - spotify의 액세스 토큰, spotifyToken
    spotifyToken = request_data["spotifyToken"]    
    
    # 1-2. 재생목록 존재 여부 확인 (Spotify)
    try:
        exist_play, plus_db_play = spotify_getUserPlaylist(spotifyToken, userDocId) # spotify
    except requests.exceptions.HTTPError as http_e:
        http_error_msg = str(http_e)
        return jsonify({"error" : f"spotify 재생목록 가져오기 오류: {http_error_msg}"}), 500
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"뮤지기쪽 오류: {error_msg}"}), 500
    
    if len(exist_play) >= 5: # 1-3.1. 이미 감정 별 재생목록이 다 있다.
        return jsonify({"error" : "이미 감정 재생목록이 다 있습니다."}), 400
    else:
        for name in exist_play.keys():
            new_playlists_name.remove(name)
        for n in plus_db_play.keys():
            new_playlists_name.remove(n)
            
    if len(new_playlists_name) > 0:
        try: # 사용자 프로필 가져오기 -> 재생목록 생성에 필요한 spotify 사용자 id 가져옴
            spotifyId = spotify_getCurrentUser(spotifyToken)
        except requests.exceptions.HTTPError as http_e:
            http_error_msg = str(http_e)
            return jsonify({"error" : f"spotify 사용자 프로필 가져오기 오류: {http_error_msg}"}), 500

        try: # 1-3.2. 재생목록이 없는 게 있다면 새로 생성된다. (spotify)
            created_playlists_info = spotify_createPlaylist(spotifyToken, spotifyId, new_playlists_name)
        except requests.exceptions.HTTPError as http_e:
            http_error_msg = str(http_e)
            return jsonify({"error" : f"spotify 재생목록 생성 오류: {http_error_msg}"}), 500
        except Exception as e:
            error_msg = str(e)
            return jsonify({"error" : f"뮤지기쪽 문제로 재생목록 생성 실패: {error_msg}"}), 500
        
    elif len(plus_db_play) > 0:
        try:
            DB_update(plus_db_play, userDocId)
        except ValueError as ve: 
            return jsonify({"error" : str(ve)}), 400  # 유효하지 않은 입력값 - validate 오류
        except PermissionError as pe: 
            return jsonify({"error" : str(pe)}), 401  # 뮤지기 사용자 토큰 문제
        except Exception as e:
            error_msg = str(e)
            return jsonify({"error" : f"재생목록 생성 내용 DB에 저장 실패 : {error_msg}"}), 500

        return jsonify({"message" : f"재생목록 다 있는데 DB에 안 적혀 있어서 업뎃하고 끝남: {plus_db_play}"}), 200
    
    
    # DB에 업뎃해야 하는 정보 정리 - 업뎃되지 않은 정보 + 새로 생성한 것의 정보
    # 딕셔너리 언패킹 -> 동일 키값 있으면 새로 생성된 정보 기준으로 동작하게 했음
    new_playlists_info = {**plus_db_play, **created_playlists_info}
    
    # --- 여기서부터 DB 조작    
    try: # 지워야 하는 정보 확인 (이전에 갖고 있던 의미없는 재생목록 정보값)
        delete_db_play = DB_checkPlaylist(userDocId)
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"DB에 존재하는 재생목록 보다가 오류: {error_msg}"}), 500
    
    if len(delete_db_play) > 0:
        try: # 지워야 하는 정보 지우기
            for playlistDocId in delete_db_play.values():
                # Playlist 컬렉션의 문서 삭제
                db.collection("Playlist").document(playlistDocId).delete()

        except Exception as e:
            error_msg = str(e)
            return jsonify({"error" : f"DB에 있던 의미없는 재생목록 정보 지우다가 오류: {error_msg}"}), 500

    # 업뎃할 내용, 생성한 재생목록 db에 저장하기
    try:
        DB_update(new_playlists_info, userDocId)
    except ValueError as ve: 
        return jsonify({"error" : str(ve)}), 400  # 유효하지 않은 입력값 - validate 오류
    except PermissionError as pe: 
        return jsonify({"error" : str(pe)}), 401  # 뮤지기 사용자 토큰 문제
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"재생목록 생성 내용 DB에 저장 실패 : {error_msg}"}), 500
    
    
    return jsonify({"playlistIds" : new_playlists_info}), 201 # 성공!


# 선호 여부 기록 -> 재생목록 내 음악 추가 API
@playlist_blp.route("/<emotionName>/add", methods=["POST"])
@login_required
def addTrackToPlaylist(curr_user, emotionName):
    """
    1-2. 재생목록 존재 여부를 확인한다.
    1-3.1. 재생목록이 존재하지 않으면 생성 API를 부르고 마저 진행된다.
    1-3.2. 재생목록이 있다면 해당하는 감정 재생목록에 저장된다.
           (spotify, firestore 모두 반영)
    """
    if not curr_user:
        return jsonify({"error" : "뮤지기 사용자 토큰 없음"}), 401
    userDocId = curr_user.get("userDocId")
    
    request_data = request.get_json()
    spotifyToken = request_data.get("spotifyToken")
    trackInfo = request_data.get("trackInfo") # 넣을 음악 정보 Object
    
    # 1-2. 재생목록 존재 여부를 확인한다.
    try:
        exist_play, plus_db_play = spotify_getUserPlaylist(spotifyToken, userDocId) # spotify
    except requests.exceptions.HTTPError as http_e:
        http_error_msg = str(http_e)
        return jsonify({"error" : f"spotify 재생목록 가져오기 오류: {http_error_msg}"}), 500
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"뮤지기쪽 오류: {error_msg}"}), 500
    
    # 1-3.1. 재생목록이 존재하지 않으면 생성
    if emotionName not in exist_play.keys(): 
        try: # 사용자 프로필 가져오기 -> 재생목록 생성에 필요한 spotify 사용자 id 가져옴
            spotifyId = spotify_getCurrentUser(spotifyToken)
        except requests.exceptions.HTTPError as http_e:
            http_error_msg = str(http_e)
            return jsonify({"error" : f"spotify 사용자 프로필 가져오기 오류: {http_error_msg}"}), 500
        
        try:
            created_play = spotify_createPlaylist(spotifyToken, spotifyId, [emotionName])
        except requests.exceptions.HTTPError as http_e:
            http_error_msg = str(http_e)
            return jsonify({"error" : f"spotify 재생목록 생성 오류: {http_error_msg}"}), 500
        except Exception as e:
            error_msg = str(e)
            return jsonify({"error" : f"뮤지기쪽 문제로 재생목록 생성 실패: {error_msg}"}), 500
    
        new_playlists_info = {**plus_db_play, **created_play}
        try:
            DB_update(new_playlists_info, userDocId)
        except ValueError as ve: 
            return jsonify({"error" : str(ve)}), 400  # 유효하지 않은 입력값 - validate 오류
        except PermissionError as pe: 
            return jsonify({"error" : str(pe)}), 401  # 뮤지기 사용자 토큰 문제
        except Exception as e:
            error_msg = str(e)
            return jsonify({"error" : f"재생목록 생성 내용 DB에 저장 실패 : {error_msg}"}), 500
    
    # 데이터베이스 확인 (생성한 내용 잘 저장됐는지)
    try: 
        exist_db_play = DB_checkPlaylist(userDocId)
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error" : f"DB에 존재하는 재생목록 보다가 오류: {error_msg}"}), 500
    
    if emotionName not in exist_db_play.keys():
        return jsonify({"error" : "분명 생성하고 저장도 했을 텐데 DB에 없음..."}), 500
     
    
    # --- 해당하는 재생목록 있음, 음악 추가   
    playlist_id = exist_db_play.get(emotionName) 
    
    try:
        position, items = spotify_getItems(spotifyToken, playlist_id)
    except requests.exceptions.HTTPError as http_e:
        return jsonify({"error" : f"spotify에서 재생목록 내역 가져오기 오류 : {str(http_e)}"}), 500
    
    if position >= 50:
        return jsonify({"error" : "재생목록 내 음악 개수가 너무 많습니다. (최대 50개)"}), 400
    
    try:
        spotify_tracks = DB_checkHistory(playlist_id, items)
    except ValueError as ve: return jsonify({"error" : f"{ve}"}), 400
    except Exception as e : return jsonify({"error" : f"재생목록내역 spotify랑 db 비교하다가 오류: {e}"}), 500
    
    # trackId는 다른데 곡이 같은 경우가 있어서 제목, 가수로 비교함
    existing_pairs = {(v["title"], v["artist"]) for v in spotify_tracks.values()}
    if (trackInfo.get("title"), trackInfo.get("artist")) in existing_pairs:
        return jsonify({"message": "이미 있는 음악이라 추가 안함!"}), 204
    
    try:
        spotify_addItem(playlist_id, spotifyToken, trackInfo, position)
    except ValueError as ve:
        return jsonify({"error" : f"{ve}"}), 400
    except requests.exceptions.HTTPError as http_e:
        return jsonify({"error" : f"spotify에서 재생목록에 음악 추가 실패: {str(http_e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"뮤지기쪽 문제로 음악 추가 실패 : {str(e)}"}), 500
    
    
    return jsonify({"message" : "음악 추가 성공!"}), 200


# 재생목록 조회 API - 재생목록 내역을 반환해줌
@playlist_blp.route("/<emotionName>/show", methods=["GET"])
@login_required
def showPlaylistHistory(curr_user, emotionName):
    if not curr_user:
        return jsonify({"error" : "뮤지기 사용자 토큰 없음"}), 401
    userDocId = curr_user.get("userDocId")
    
    try:
        history = DB_getHistory(userDocId, emotionName)
    except FileNotFoundError as fe:
        return jsonify({"error" : f"{str(fe)}"}), 400
    except PermissionError as pe:
        return jsonify({"error" : f"{str(pe)}"}), 401
    except Exception as e:
        return jsonify({"error" : f"재생목록 내역 DB 조회하다 에러남 : {str(e)}"}), 500
    
    return jsonify({"tracks" : history}), 200