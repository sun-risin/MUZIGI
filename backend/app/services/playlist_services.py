from firebase_admin import firestore
from app.schemas.playlist_schema import PlaylistSchema, TrackInfoSchema
import requests

db = firestore.client()
playlist_schema = PlaylistSchema()
trackInfo_schema = TrackInfoSchema()

# --- 전역 변수
emotions_mapping = {
        "happiness" : "행복",
        "excited" : "신남",
        "aggro" : "화남",
        "sorrow" : "슬픔",
        "nervous" : "긴장" } # 감정값 영어(key) 한글(value) 딕셔너리

# --- spotify API 사용 함수
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
        
    3. 소유 재생목록 가져오기 API - **Get Current User's Playlists**
        - 호출 예시
            
            curl --request GET \
            --url https://api.spotify.com/v1/me/playlists \
            --header 'Authorization: Bearer {access_token}'        
        
        ⇒ 반환값 중 items 내 description, id 사용, 설명이 일치하는 게 있으면 DB에도 겹치는 문서가 있는지 확인 후 제외.
            겹치는 문서가 없다면 spotify에는 있는데 db에는 없는 것이므로 에러
            TODO - 된다면 이 경우에 에러 나게 하지말고, playlist, users 컬렉션에 있는 내용을 업뎃하도록 수정
            
    4. 재생목록에 음악 추가 API - Add Items to Playlist
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
        
    5. 재생목록 내 아이템 조회 API - Get Playlist Items
    - 호출 예시
        curl --request GET \
        --url https://api.spotify.com/v1/playlists/{playlist_id}/tracks \
        --header 'Authorization: Bearer {access_token}'
        --params 'market' : 'KR', 'fields':'total, items(track(id, name, artists(name)))', 'limit':50
        => 반환값 중 total -> 들어있는 음악 개수 / items - 들어있는 요소, track(~) 음악 아이디, 제목, 가수 이름
"""
    
# 사용자 프로필 가져오기 API -> spotify 사용자 id 반환
def spotify_getCurrentUser(spotifyToken):
    SPOTIFY_GET_PROFILE_URL = "https://api.spotify.com/v1/me"
    profile_header = { "Authorization": f"Bearer {spotifyToken}" }
    try:
        get_profile_response = requests.get(SPOTIFY_GET_PROFILE_URL, headers=profile_header)
        get_profile_response.raise_for_status()
        
        spotifyId = get_profile_response.json().get("id") # spotify 고유 id 저장
        
    except requests.exceptions.HTTPError : raise # spotify 관련 에러

    return spotifyId # spotify 사용자 id 반환
    
# 재생목록 생성 API -> 생성한 재생목록 정보 보냄 (key - 감정(영어), value - 재생목록 ID)
def spotify_createPlaylist(spotifyToken, spotifyId, new_playlists_name):    
    SPOTIFY_CREATE_PLAYLIST_URL = f"https://api.spotify.com/v1/users/{spotifyId}/playlists"
    create_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    new_playlists_info = {}
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
            new_playlists_info[new] = new_id # happines : "행복 재생목록 id" 형태
                    
    except requests.exceptions.HTTPError : raise  # spotify 관련 에러 
    except Exception: raise # 이외 뮤지기 관련 문제
    
    return new_playlists_info
    
# 재생목록 가져오기 API - spotify에서 재생목록 존재 여부 확인
# 존재하는 재생목록 정보값 반환 (DB에는 없는 게 있다면 따로 저장해 반환)
def spotify_getUserPlaylist(spotifyToken, userDocId):
    exist_playlists_info = {} # spotify, DB에 있는 재생목록
    no_db_playlists_info = {} # spotify에 있고, DB에는 없는 재생목록
    
    SPOTIFY_GET_PLAYLIST_URL = "https://api.spotify.com/v1/me/playlists"
    get_playlist_header = { "Authorization": f"Bearer {spotifyToken}" }
    get_playlist_params = { "limit" : 50 }
    
    try:
        get_playlist_response = requests.get(SPOTIFY_GET_PLAYLIST_URL,
                                             headers=get_playlist_header,
                                             params=get_playlist_params)
        get_playlist_response.raise_for_status()
        
        curr_playlists = get_playlist_response.json().get("items")
        for item in curr_playlists:
            description = item.get("description")  # 뮤지기 관련 플리만 고정 패턴
            item_id = item.get("id")               # 뮤지기 관련 플리 id
            user_ref = db.collection("users").document(userDocId)
            user_doc = user_ref.get()
            if not user_doc.exists: 
                raise PermissionError("유효하지 않은 사용자입니다.")
                            
            user_playlistIds = user_doc.get("playlistIds") or {} # 내용 없을 수도 있음
            
            # description 패턴 기반 역매핑
            for eng, kor in emotions_mapping.items():
                if description == f"뮤지기 - 감정 {kor}에 맞는 플리":
                    try:
                        playlist_doc = db.collection("Playlist").document(item_id).get()
                        
                        if not playlist_doc.exists:
                            no_db_playlists_info[eng] = item_id
                        else:
                            exist_playlists_info[eng] = item_id
                            
                            if item_id not in user_playlistIds.values():
                                user_ref.update({ # 수정 (없었다면 추가됨)
                                    f"playlistIds.{eng}": item_id
                                })
                            
                    except Exception: raise # 뮤지기쪽 오류
                
    except requests.exceptions.HTTPError: raise # spotify 관련 오류
    
    return exist_playlists_info, no_db_playlists_info

# spotify에 음악 추가 - 반환값 X
def spotify_addItem(playlist_id, spotifyToken, trackInfo, position):
    trackId = trackInfo.get("trackId")
    
    trackInfo_db_errors = trackInfo_schema.validate(trackInfo)
    if trackInfo_db_errors:
                raise ValueError(f"곡정보의 유효하지 않은 데이터값 : {trackInfo_db_errors}")
    
    SPOTIFY_ADD_ITEMS_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    add_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    add_data = {
        "uris" : [f"spotify:track:{trackId}"],
        "position": position 
    }    
    try:
        # TODO - 조회 API 만들고 나서 이미 있는 노래면 추가 X
        add_response = requests.post(SPOTIFY_ADD_ITEMS_URL, headers=add_headers, json=add_data)
        add_response.raise_for_status()
        
        playlist_ref = db.collection("Playlist").document(playlist_id)        
        playlist_ref.update({
            f"tracks.{str(position)}": trackInfo
        })
    
    except requests.exceptions.HTTPError : raise
    except Exception : raise
    
# spotify 재생목록 내 아이템 조회 -> 반환값: 음악 개수
def spotify_getItems(spotifyToken, playlist_id):
    SPOTIFY_GET_ITEM_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    get_item_header = { "Authorization": f"Bearer {spotifyToken}" }
    get_item_params = {'market' : 'KR',
                       'fields': 'total, items(track(id, name, artists(name)))',
                       'limit':50}
    
    try:
        get_item_response = requests.get(SPOTIFY_GET_ITEM_URL,
                                         headers=get_item_header, params=get_item_params)
        get_item_response.raise_for_status()
        
        tracks_cnt = get_item_response.json().get("total") # 음악 개수
        items = get_item_response.json().get("items")
        
    except requests.exceptions.HTTPError : raise # spotify 관련 에러

    return tracks_cnt, items

# --- DB 관련 함수 
# DB에서 사용자가 갖고 있는 재생목록 가져오기 - spotify에는 이제 없는 재생목록 정보가 있을 수 있음
# userDoc에서 playlist id들 가져온 다음에 그 문서들이 Playlist 컬렉션에도 있는지 확인
def DB_checkPlaylist(userDocId):
    playlists_info = {}
    
    try:
        user_ref = db.collection("users").document(userDocId)
        user_doc = user_ref.get()
        if not user_doc.exists: 
            raise PermissionError("유효하지 않은 사용자입니다.")
        
        user_playlistIds = user_doc.get("playlistIds")
        
        for playlistDocId in user_playlistIds.values():
            playlist_ref = db.collection("Playlist").document(playlistDocId)
            playlist_doc = playlist_ref.get()
            if playlist_doc.exists: 
                emotionName = playlist_doc.get("emotionName")         
                playlists_info[emotionName] = playlistDocId
        
    except Exception : raise
    
    return playlists_info

# Playlist, users 컬렉션에 업뎃 - 반환 값 X
def DB_update(new_playlists_info, userDocId):
    try:
        for emo in new_playlists_info.keys():        
            
            # Firestore - Playlist 컬렉션            
            new_playli = db.collection("Playlist").document(new_playlists_info.get(emo))
            new_data = {
                "emotionName" : f"{emo}", 
                "playlistId":  new_playli.id,
                "tracks" : {}
            }
            playli_db_errors = playlist_schema.validate(new_data) # schema로 유효성 검사
            if playli_db_errors:
                raise ValueError(f"재생목록 컬렉션에 저장하려 했으나, 유효하지 않은 입력값 : {playli_db_errors}")                      
            
            new_playli.set(new_data)
            
            # Firestore - users 컬렉션
            user_ref = db.collection("users").document(userDocId)
            user_doc = user_ref.get()
            if not user_doc.exists: 
                raise PermissionError("유효하지 않은 사용자입니다.")
            
            user_ref.update({ # 수정 (없었다면 추가됨)
                f"playlistIds.{emo}": new_playli.id
            })
            
    except Exception : raise
    
# spotify와 DB의 재생목록내역 비교 -> 반환값: spotify의 재생목록 내역
def DB_checkHistory(playlist_id, items):
    tracks = {}
    for i in range(len(items)):
        spoti_trackDoc = items[i]
        spoti_track = spoti_trackDoc.get("track")
        title = spoti_track.get("name")
        trackId = spoti_track.get("id")

        artists = spoti_track.get("artists")
        if len(artists) > 1:
            artist = " / ".join([a.get("name") for a in artists])
        else:
            artist = artists[0].get("name")

        trackInfo = {
            "title" : title,
            "artist" : artist,
            "trackId" : trackId
        }
        trackInfo_db_errors = trackInfo_schema.validate(trackInfo)
        if trackInfo_db_errors:
            raise ValueError(f"곡 정보의 유효하지 않은 입력값 : {trackInfo_db_errors}")

        tracks[str(i)] = trackInfo

    try:
        playlist_ref = db.collection("Playlist").document(playlist_id)
        playlist_snapshot = playlist_ref.get()
        existing_tracks = playlist_snapshot.get("tracks") or {}

        if existing_tracks != tracks:
            # 다른 내용이면 업데이트
            playlist_ref.update({"tracks": tracks})

    except Exception : raise
    
    return tracks

def DB_getHistory(userDocId, emotionName):
    try:
        user_ref = db.collection("users").document(userDocId)
        user_doc = user_ref.get()
        if not user_doc.exists: 
            raise PermissionError("유효하지 않은 사용자입니다.")
            
        user_playlistIds = user_doc.get("playlistIds")
        
        playlistDocId = user_playlistIds.get(f"{emotionName}")
        playlist_ref = db.collection("Playlist").document(playlistDocId)
        playlist_doc = playlist_ref.get()
        if not playlist_doc.exists: 
            raise FileNotFoundError(f"조회하려는 감정의 재생목록이 없습니다. 감정: {emotionName}")
        
        history = playlist_doc.get("tracks") or {} # 아직 내용이 없을 수 있음
        
        """
        만약 전체 재생목록을 보내야 한다면 그때의 코드... 
        (이 경우 위의 코드는 삭제하고 emotionName은 Path Parameter로 받지 않음, 반환 값은 hisotrys)
        historys = {}
        for emo in emotions_mapping.keys():
            playlistDocId = user_playlistIds.get(f"{emo}")
            playlist_ref = db.collection("Playlist").document(playlistDocId)
            playlist_doc = playlist_ref.get()
            if not playlist_doc.exists: 
                raise FileNotFoundError(f"조회하려는 감정의 재생목록이 없습니다. 감정: {emo}")
            
            historys[f"{emo}"] = playlist_doc.get("tracks") or {}
        """
        
    except Exception : raise
    
    return history