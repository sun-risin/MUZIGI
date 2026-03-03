from ...extensions import db
from ...common.exception.customException import UnknownException, CustomException, ErrorCode
    
# 사용자 소유 재생목록 정보 가져오기
def DB_get_users_playlist(userDocId):
    user_doc = db.collection("users").document(userDocId).get()
    return user_doc.get("playlistIds")

# playlist 컬렉션에 없는 사용자 재생목록 정보를 찾아냄
# : 반환값 - playlist 컬렉션에 없는 재생목록 정보 (감정: id)
def DB_check_playlist_by_user(userDocId):
    have_to_record = {}
    try:
        user_playlists = DB_get_users_playlist(userDocId)
        
        for emotionName, playlistDocId in user_playlists.items():
            playlist_doc = db.collection("Playlist").document(playlistDocId).get()
            
            if not playlist_doc.exists: 
                have_to_record[emotionName] = playlist_doc
                # tracks = spotify_getItems(spotifyToken, playlistDocId)[1]         
                # new_playlist_info = {
                #     "emotionName" : emotionName,
                #     "playlistDocId" : playlistDocId
                # }
                # DB_record_playlist(new_playlist_info, tracks)
        
        return have_to_record
        
    except Exception as e: 
        raise UnknownException(f"DB의 user의 재생목록 정보와 playlist 컬렉션 정보 비교 중 에러 : {str(e)}")


# 사용자의 특정 감정의 DB 재생목록 내역 가져오기
def DB_get_playlist_history(userDocId, emotionName):
    try:         
        user_playlistIds = DB_get_users_playlist(userDocId)
        
        playlistDocId = user_playlistIds.get(f"{emotionName}")
        playlist_doc = db.collection("Playlist").document(playlistDocId).get()
        if not playlist_doc.exists: 
            raise CustomException(ErrorCode.NOT_FOUND_PLAYLIST)
        
        history = playlist_doc.get("tracks") or {} # 아직 내용이 없을 수 있음

    except Exception as e: 
        raise UnknownException(f"재생목록 내역 가져오는 도중 에러 : {str(e)}")

    return history
    
# # spotify 기준 DB 재생목록내역 비교
# # : 반환값 - 업데이트 여부
# def DB_check_playlist_history(playlist_id, tracks):
#     try:
#         playlist_doc = db.collection("Playlist").document(playlist_id).get()
#         db_existing_tracks = playlist_doc.get("tracks") or {}

#         # 다른 내용이면 업데이트
#         return db_existing_tracks != tracks
#             #playlist_ref.update({"tracks": tracks})

#     except Exception as e: 
#         raise UnknownException(f"재생목록 내역 비교 중 에러 : {str(e)}")