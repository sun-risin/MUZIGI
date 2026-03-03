from ...common.exception.customException import UnknownException, CustomException, ErrorCode
from ..emotion.emotionMapping import EmotionMapping

from .playlist_services import DB_update_about_playlist
from ..spotify.spotify_services import spotify_createPlaylist
from .playlist_repository import DB_get_users_playlist

# 재생목록 생성
def create_new_playlist(userDocId: str, spotifyToken: str):
    """
    1-2. 재생목록 존재 여부를 확인한다.
    1-2.1. spotify와 db 내용 차이가 있다면 업뎃한다.
    1-3.1. 이미 감정 별 재생목록이 있다면 종료된다.
    1-3.2. 재생목록이 없는 게 있다면 새로 생성된다.
    """
        
    # --- 1-2. 재생목록 존재 여부를 확인한다. 
    # db_user 컬렉션에 있는 재생목록 정보 {emotionName : id}
    db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
    # 1-3.1.
    if len(db_user_muzigi_playlists_info) == 5: 
        raise CustomException(ErrorCode.ALREADY_EXIST_ALL_PLAYLIST)
    
    # --- 1-3.2. 없는 감정 재생목록 생성 및 저장
    # 이미 id 부여받은 감정 eng는 제외함
    try:
        existing = set(db_user_muzigi_playlists_info.keys())
        new_playlists_name = [
            eng
            for eng in EmotionMapping.get_eng_key().keys()
            if eng not in existing
        ]
    except Exception as e: 
        raise UnknownException(f"생성할 재생목록 감정 추려내다 에러 발생: {str(e)}")
    
    # spotify 내 생성
    created_playlists_info = spotify_createPlaylist(spotifyToken, new_playlists_name)
    
    # 생성된 정보 db에 기록 (사용자 문서 내 필드 업뎃 + playlist 컬렉션에 문서 업로드)
    DB_update_about_playlist(created_playlists_info, userDocId)
    
    response_data = {"playlistIds" : created_playlists_info}
    
    return response_data