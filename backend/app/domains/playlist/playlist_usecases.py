from ...common.exception.customException import UnknownException, CustomException, ErrorCode, SpotifyNotFoundException
from ..emotion.emotionMapping import EmotionMapping

from .playlist_services import DB_update_about_playlist, DB_add_track
from ..spotify.spotify_services import spotify_createPlaylist, spotify_addItem, sync_spotify_playlists
from .playlist_repository import DB_get_users_playlist, DB_get_playlist_history

# 재생목록 생성
def create_new_playlist(userDocId: str, spotifyToken: str):
    """
    1-2. 재생목록 존재 여부를 확인한다.
    1-2.1. 이미 감정 별 재생목록이 있다면 종료된다.
    1-3. 재생목록이 없는 게 있다면 새로 생성된다.
    """
        
    # --- 1-2. 재생목록 존재 여부를 확인한다. 
    # db_user 컬렉션에 있는 재생목록 정보 {emotionName : id}
    db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
    # 1-2.1.
    if len(db_user_muzigi_playlists_info) == 5: 
        raise CustomException(ErrorCode.ALREADY_EXIST_ALL_PLAYLIST)
    
    # --- 1-3. 없는 감정 재생목록 생성 및 저장
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

# 선호 여부 기록
def record_liked_track(spotifyToken: str, userDocId: str, emotionName:str, trackInfo: dict, retry_cnt: int = 0):
    """
    0. retry_cnt (재시도 횟수)는 1 이하여야 한다. (아닐 시 에러)
    1-2. 재생목록 존재 여부를 확인한다.
    1-2.1. 재생목록이 존재하지 않으면 생성 메서드를 부르고 마저 진행된다.
    1-3. 해당하는 감정 재생목록에 음악의 존재 여부를 확인한다.
    1-3.1. 이미 있으면 저장하지 않는다.
    1-4. 없는 음악이라면 해당하는 감정 재생목록에 음악이 저장된다.
        1-4-1. spotify add
        1-4-1.2. 404 에러 시 동기화 후 재시도
        1-4-2. db에 기록
    """
    # --- 0. retry_cnt (재시도 횟수)는 1 이하여야 한다.
    if retry_cnt > 1:
        raise CustomException(ErrorCode.UNKNOWN_ERR)
    
    # --- 1-2. 재생목록 존재 여부를 확인한다. 
    # db_user 컬렉션에 있는 재생목록 정보 {emotionName : id}
    db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
    # 1-2.1.
    if emotionName not in db_user_muzigi_playlists_info.keys():
        create_new_playlist(userDocId, spotifyToken)
        db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
    
    # --- 1-3. 해당하는 감정 재생목록에 음악의 존재 여부를 확인한다.
    existing_tracks = DB_get_playlist_history(userDocId, emotionName)
    # 1-3.1.
    if ((trackInfo.get("title"), trackInfo.get("artist")) 
            in ((v["title"], v["artist"]) for v in existing_tracks.values())): 
        raise CustomException(ErrorCode.DUPLICATE_TRACK)
    
    # --- 1-4. 해당하는 감정 재생목록에 음악이 저장된다.
    playlistDocId = db_user_muzigi_playlists_info.get(emotionName)
    position = len(existing_tracks) + 1
    
    # 1-4-1. & 1-4-1.2.
    try:
        spotify_addItem(spotifyToken, playlistDocId, position, trackInfo)
    except SpotifyNotFoundException:
        if retry_cnt == 0:
            sync_spotify_playlists(playlistDocId, spotifyToken, emotionName, userDocId)
            return record_liked_track(spotifyToken, userDocId, emotionName, trackInfo, 1)
            
        raise
    
    except:
        raise
    
    # 1-4-2.
    DB_add_track(playlistDocId, position, trackInfo)
    
# 재생목록 내역 조회
def get_hisotry_playlist(userDocId: str, emotionName: str, spotifyToken: str):
    """
    1-2. 재생목록 존재 여부를 확인한다.
    1-2.1. 재생목록이 존재하지 않으면 생성 메서드를 부르고 마저 진행된다.
    1-3. db playlist 컬렉션 내 문서 필드 내부 음악 내역 가져오기
    """
    
    # --- 1-2. 재생목록 존재 여부를 확인한다. 
    # db_user 컬렉션에 있는 재생목록 정보 {emotionName : id}
    db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
    # 1-2.1.
    if emotionName not in db_user_muzigi_playlists_info.keys():
        create_new_playlist(userDocId, spotifyToken)
        db_user_muzigi_playlists_info = DB_get_users_playlist(userDocId)
        
    # --- 1-3. db playlist 컬렉션 내 문서 필드 내부 음악 내역 가져오기
    history = DB_get_playlist_history(userDocId, emotionName)
    response_data = {"tracks" : history}
    
    return response_data