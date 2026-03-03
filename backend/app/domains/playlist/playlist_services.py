from ...extensions import db
from ..playlist.playlist_schema import PlaylistSchema, TrackInfoSchema
from ...common.exception.customException import UnknownException, CustomException, ErrorCode

# --- 전역 변수
playlist_schema = PlaylistSchema()
trackInfo_schema = TrackInfoSchema()

# Playlist 컬렉션에 새 정보 기록
def DB_record_playlist(new_playlist_info: dict, tracks: dict):
    # 저장할 정보 준비
    emotionName = new_playlist_info.get("emotionName")
    playlist_id = new_playlist_info.get("playlistDocId")
    new_data = {
        "emotionName" : emotionName, 
        "playlistId": playlist_id,
        "tracks" : tracks
    }
    
    # schema로 유효성 검사
    playli_db_errors = playlist_schema.validate(new_data) 
    if playli_db_errors:
        raise CustomException(ErrorCode.WRONG_PLAYLIST_INFO)
    
    # Firestore - Playlist 컬렉션
    new_playlist = db.collection("Playlist").document(playlist_id)
    new_playlist.set(new_data)
    
    
# users의 playlistIds 정보 수정
def DB_update_user_playlist(new_playlist_info: dict, userDocId: str):
    # 저장할 정보 검사
    emotionName = new_playlist_info.get("emotionName")
    playlist_id = new_playlist_info.get("playlistDocId")
    new_data = {
        "emotionName" : emotionName, 
        "playlistId": playlist_id,
        "tracks" : {}
    }
    # schema로 유효성 검사
    playli_db_errors = playlist_schema.validate(new_data) 
    if playli_db_errors:
        raise CustomException(ErrorCode.WRONG_PLAYLIST_INFO)
    
    # Firestore - users 컬렉션 수정
    user_ref = db.collection("users").document(userDocId)
    user_ref.update({
        f"playlistIds.{emotionName}": playlist_id
    })
    
# Playlist, users 컬렉션에 재생목록 업뎃
def DB_update_about_playlist(new_playlists_info: dict, userDocId: str, new_playlists_tracks: dict = {}):
    try:
        for emotion, id in new_playlists_info.items():
            info = {
                "emotionName" : emotion,
                "playlistDocId" : id
            }
            
            tracks = new_playlists_tracks.get(f"{emotion}") or {}
            DB_record_playlist(info, tracks)
            DB_update_user_playlist(info, userDocId)
    
    except Exception as e: 
        raise UnknownException(f"재생목록 새로운 정보 기록 중 에러 : {str(e)}")
    
# 재생목록 삭제 (Playlist 컬렉션 내 문서 삭제)
def DB_delete_playlist(playlist_id: str):
    db.collection("Playlist").document(playlist_id).delete()
    
# 재생목록 내 음악 추가
def DB_add_track(playlistDocId: str, position: int, trackInfo: dict):
    try:
        playlist_ref = db.collection("Playlist").document(playlistDocId)        
        playlist_ref.update({
            f"tracks.{str(position)}": trackInfo
        })
    except Exception as e: 
        raise UnknownException(f"재생목록에 음악 추가하다가 뮤지기에서 에러 : {str(e)}")