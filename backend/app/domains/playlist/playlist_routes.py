from flask import Blueprint, request, jsonify
from ..auth.decorater import login_required

from ...common.apiResponse import ApiResponse

# 서비스 레이어의 함수들 import
from .playlist_usecases import create_new_playlist, record_liked_track

playlist_blp = Blueprint("playlist", __name__, url_prefix="/api/playlist")
    
# --- 뮤지기 서비스 API들
# 재생목록 생성 API
@playlist_blp.route("/new", methods=["POST"])
@login_required
def createPlaylist(curr_user):
    userDocId = curr_user.get("userDocId")   

    request_data = request.get_json()
    spotifyToken = request_data["spotifyToken"]    # spotify의 액세스 토큰
    
    # 새 재생목록 생성 -> 생성된 플레이리스트 정보 반환
    response_data = create_new_playlist(userDocId, spotifyToken)
    
    return ApiResponse.success(
        status=201, message="재생목록 생성 성공", data=response_data)


# 선호 여부 기록 -> 재생목록 내 음악 추가 API
@playlist_blp.route("/<emotionName>/add", methods=["POST"])
@login_required
def addTrackToPlaylist(curr_user, emotionName):
    if not curr_user:
        return jsonify({"error" : "뮤지기 사용자 토큰 없음"}), 401
    userDocId = curr_user.get("userDocId")
    
    request_data = request.get_json()
    spotifyToken = request_data.get("spotifyToken")
    trackInfo = request_data.get("trackInfo") # 넣을 음악 정보 Object
    
    record_liked_track(spotifyToken, userDocId, emotionName, trackInfo, 0)
    
    return ApiResponse.success(201, "음악 추가 성공")


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