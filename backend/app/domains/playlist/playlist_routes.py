from flask import Blueprint, request
from ..auth.decorater import login_required

from ...common.apiResponse import ApiResponse

# 서비스 레이어의 함수들 import
from .playlist_usecases import create_new_playlist, record_liked_track, get_hisotry_playlist

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
    userDocId = curr_user.get("userDocId")
    
    request_data = request.get_json()
    spotifyToken = request_data.get("spotifyToken")
    trackInfo = request_data.get("trackInfo") # 넣을 음악 정보 Object
    
    record_liked_track(spotifyToken, userDocId, emotionName, trackInfo, 0)
    
    return ApiResponse.success(201, "음악 추가 성공")


# 재생목록 조회 API - 재생목록 내역을 반환해줌
# TODO - spotifyToken request body data 추가된 거 전달
@playlist_blp.route("/<emotionName>/show", methods=["POST"])
@login_required
def showPlaylistHistory(curr_user, emotionName):
    userDocId = curr_user.get("userDocId")
    
    request_data = request.get_json()
    spotifyToken = request_data.get("spotifyToken")
    
    response_data = get_hisotry_playlist(userDocId, emotionName, spotifyToken)
    
    return ApiResponse.success(
        200, "재생목록 내역 조회 성공", response_data)