import requests

from ...extensions import db
from ..playlist.playlist_schema import TrackInfoSchema
from ..emotion.emotionMapping import EmotionMapping
from ...common.exception.customException import UnknownException, ValidateException, CustomException, ErrorCode, SpotifyNotFoundException

from ..playlist.playlist_services import DB_delete_playlist, DB_update_about_playlist

trackInfo_schema = TrackInfoSchema()    
    
# 재생목록 생성 API 사용
# : 생성한 재생목록 정보 반환 (key - 감정(영어), value - 재생목록 ID)
def spotify_createPlaylist(spotifyToken, new_playlists_name):        
    SPOTIFY_CREATE_PLAYLIST_URL = "https://api.spotify.com/v1/me/playlists"
    create_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    
    new_playlists_info = {} # 생성한 재생목록 정보 담을 딕셔너리
    
    try:
        # new_playlists_name - 생성할 재생목록의 감정 리스트 (영어)
        for eng_emotion in new_playlists_name:
            
            # 감정 이름 한글 패치
            emotion = EmotionMapping.eng_to_kor(eng_emotion)            
            
            # spotify api request body json data
            create_data = {                                             
                "name": f"{emotion}",                                   # 재생목록 이름
                "description": f"뮤지기 - 감정 {emotion}에 맞는 플리",   # 재생목록 설명글
                "public": False                                         # 재생목록 공개 설정
            }
            
            # spotify api 응답 받기
            create_response = requests.post(SPOTIFY_CREATE_PLAYLIST_URL,
                                            json=create_data, headers=create_headers)
            create_response.raise_for_status()
            
            # 재생목록 정보 기록
            new_id = create_response.json().get("id")   # 생성한 재생목록 아이디
            new_playlists_info[eng_emotion] = new_id    # e.g., happines : f"{행복 재생목록 id}"
                    
    
    except requests.exceptions.HTTPError as e :                 # spotify 관련 에러 발생
        if e.response.status_code == 401:                       # 토큰 재발급 필요
            raise CustomException(ErrorCode.SPOTIFY_TOKEN_ERR)
        else:                                                   # 이외 에러 (403 or 429 등 -> 재시도 불필요)
            raise  
    except Exception as e:                              # 이외 뮤지기 에러
        raise UnknownException(f"재생목록 생성 중 뮤지기에서 에러 : {str(e)}")
    
    
    return new_playlists_info

    
# 재생목록 가져오기 API 사용
# : spotify 내 뮤지기 관련 재생목록 정보 반환 
def spotify_getUserPlaylist(spotifyToken):
    
    # 반환할 spotify 내 뮤지기 재생목록 정보 딕셔너리
    spotify_muzigi_playlists_info = {} 
    
    # spotify api 요청 준비
    SPOTIFY_GET_PLAYLIST_URL = "https://api.spotify.com/v1/me/playlists"
    get_playlist_header = { 
        "Authorization": f"Bearer {spotifyToken}" 
    }
    get_playlist_params = { 
        "limit" : 50            # 로드 개수 최대 50개 설정 (api 기준 최댓값.)
    }
    
    # spotify api 응답 받아 spotify 내 뮤지기 재생목록 정보 저장
    try:
        get_playlist_response = requests.get(SPOTIFY_GET_PLAYLIST_URL,
                                             headers=get_playlist_header,
                                             params=get_playlist_params)
        get_playlist_response.raise_for_status()
    
        # spotify 내 재생목록 중 뮤지기 관련 재생목록만 걸러내 저장하기
        spotify_playlists = get_playlist_response.json().get("items")       # spotify 내 사용자 소유 재생목록
        for playlist in spotify_playlists:
            
            if "뮤지기 - 감정 " in playlist.get("description"):             # 뮤지기 관련 재생목록 특징으로 걸러냄
                # 정보 포맷 맞춰 저장 (감정(영어) : 재생목록 id)
                emotion = EmotionMapping.kor_to_eng(playlist.get("name"))
                spotify_muzigi_playlists_info[emotion] = playlist.get("id")
                
    except requests.exceptions.HTTPError as e :                 # spotify 관련 에러 발생
        if e.response.status_code == 401:                       # 토큰 재발급 필요
            raise CustomException(ErrorCode.SPOTIFY_TOKEN_ERR)
        else:                                                   # 이외 에러 (403 or 429 등 -> 재시도 불필요)
            raise
    
    return spotify_muzigi_playlists_info

# spotify 재생목록 내 아이템 조회
# : 반환값 - 음악 개수 & 재생목록 내부 정보
def spotify_getItems(spotifyToken, playlist_id):    
    # spotify api 요청 준비
    SPOTIFY_GET_ITEM_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    get_item_header = { "Authorization": f"Bearer {spotifyToken}" }
    get_item_params = {'market' : 'KR',
                       'fields': 'items(track(id, name, artists(name)))',
                       'limit':50}
    try:
        get_item_response = requests.get(SPOTIFY_GET_ITEM_URL,
                                         headers=get_item_header, params=get_item_params)
        get_item_response.raise_for_status()
        
        items = get_item_response.json().get("items")           # 재생목록 내 음악 정보
        
    except requests.exceptions.HTTPError as e :                 # spotify 관련 에러 발생
        status = e.response.status_code
        if status == 401:                                       # 토큰 재발급 필요
            raise CustomException(ErrorCode.SPOTIFY_TOKEN_ERR)
        else:                                                   # 이외 에러 (403 or 429 등 -> 재시도 불필요)
            raise

    # 재생목록 내 음악 정보를 db 포맷에 맞게 하는 작업
    spotify_tracks = {}
    for i in range(len(items)):
        spoti_track = items[i].get("track")
        title = spoti_track.get("name")
        trackId = spoti_track.get("id")

        artists = spoti_track.get("artists")
        if len(artists) > 1:    # 2명 이상인 경우 / 기준으로 나눠 리스트로 저장
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
            raise CustomException(ErrorCode.WRONG_TRACK_INFO)

        spotify_tracks[str(i)] = trackInfo
    
    return spotify_tracks

# spotify 앱 내 재생목록 정보와 db 정보 동기화시키는 메서드 (404에만, 각 경우 1번만 호출됨)
def sync_spotify_playlists(before_playlist_id, spotifyToken, emotionName, userDocId):
    # spotify 앱 내 뮤지기 관련 재생목록 가져오기
    spotify_muzigi_playlists_info = spotify_getUserPlaylist(spotifyToken)
    
    # 업데이트할 재생목록 정보
    update_playlist_id = spotify_muzigi_playlists_info.get(f"{emotionName}")
    update_playlist_info = {
        "emotionName" : emotionName,
        "playlistDocId": update_playlist_id
    }
    update_playlist_tracks = {
        f"{emotionName}": spotify_getItems(spotifyToken, update_playlist_id)
    }
    
    # 재생목록 정보 업데이트
    DB_update_about_playlist(update_playlist_info, userDocId, update_playlist_tracks)
    
    # 잘못되었던 재생목록 정보 삭제
    DB_delete_playlist(before_playlist_id)
    

# spotify에 음악 추가 
# : 반환값 X
def spotify_addItem(spotifyToken, playlist_id, position, trackInfo):    
    trackInfo_db_errors = trackInfo_schema.validate(trackInfo)
    if trackInfo_db_errors:
        raise ValidateException(f"추가할 음악의 정보값이 유효하지 않음 : {trackInfo_db_errors}")
    
    # 추가할 음악 정보 체크 (ID, 기존 존재 여부, 저장할 위치)
    trackId = trackInfo.get("trackId")
    
    # spotify api 요청 준비
    SPOTIFY_ADD_ITEMS_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    add_headers = {
        "Authorization": f"Bearer {spotifyToken}",
        "Content-Type": "application/json"
    }
    add_data = {
        "uris" : [f"spotify:track:{trackId}"],
        "position": position 
    }    
    # spotify api 요청
    try:
        add_response = requests.post(SPOTIFY_ADD_ITEMS_URL, headers=add_headers, json=add_data)
        add_response.raise_for_status()
    
    except requests.exceptions.HTTPError as e :                 # spotify 관련 에러 발생
        status = e.response.status_code
        if status == 401:                                       # 토큰 재발급 필요
            raise CustomException(ErrorCode.SPOTIFY_TOKEN_ERR)
        elif status == 404:                                     # 없는 재생목록
            raise SpotifyNotFoundException(
                f"spotify API 처리 중 오류 발생: {str(e)}")
        else:                                                   # 이외 에러 (403 or 429 등 -> 재시도 불필요)
            raise


# --- 사용된 spotify API 설명
"""
    1. 사용자 프로필 get API - **Get Current User's Profile** -> 업데이트로 안쓰게 됨
        - 호출 예시
            
            curl --request GET \
            --url https://api.spotify.com/v1/me \
            --header 'Authorization: Bearer {access_token}'
            
        ⇒ 반환값 중 id 사용 (spotify 고유 사용자 id string임, 재생목록 생성 API에 사용됨)
        
    2. 재생목록 생성 API - **Create Playlist**
        - 호출 예시
            curl --request POST \
            --url https://api.spotify.com/v1/me/playlists \
            --header 'Authorization: Bearer 1POdFZRZbvb...qqillRxMr2z' \
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
        --url https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/items \
        --header 'Authorization: Bearer 1POdFZRZbvb...qqillRxMr2z'
        --params 'market' : 'KR', 'fields':'total, items(track(id, name, artists(name)))', 'limit':50
        => 반환값 중 total -> 들어있는 음악 개수 / items - 들어있는 요소, track(~) 음악 아이디, 제목, 가수 이름
"""

# --- 안쓰게됨
# # 사용자 프로필 가져오기 API 사용
# # : spotify 사용자 id 반환
# def spotify_getCurrentUser(spotifyToken):
#     SPOTIFY_GET_PROFILE_URL = "https://api.spotify.com/v1/me"
#     profile_header = {
#         "Authorization": f"Bearer {spotifyToken}" 
#         }
#     try:
#         get_profile_response = requests.get(SPOTIFY_GET_PROFILE_URL, headers=profile_header)
#         get_profile_response.raise_for_status()
        
#         # 사용자의 spotify 고유 회원 id 저장
#         spotifyProfileId = get_profile_response.json().get("id") 
        
#     except requests.exceptions.HTTPError as e : 
#         if e.response.status_code == 401:                       # 토큰 재발급 필요
#             raise CustomException(ErrorCode.SPOTIFY_TOKEN_ERR)
#         else:                                                   # spotify 관련 에러 발생 (403 or 429 등 -> 재시도 불필요)
#             raise

#     return spotifyProfileId