from ... import extensions
from ...extensions import FieldFilter
from ...common.exception.customException import ErrorCode, CustomException
from .track_schema import TrackInfoSchema

import random

track_info_schema = TrackInfoSchema()

# 추천 음악 정보 리스트 반환 함수
def tracks_recommend(traits):
    try:
        danceability = traits["danceability"]
        energy = traits["energy"]
        valence = traits["valence"]
    except:
        raise CustomException(ErrorCode.FAILED_LOAD_TRACK_TRAITS)
    
    # Firestore에서 음악 특성값 기준 필터링 (kpop, 이외 각각 구한 뒤 합침)
    try:
        track_docs_kpop = list(
            extensions.db.collection("TracksKpop")
            .where(filter=FieldFilter("danceability", ">=", danceability[0]))
            .where(filter=FieldFilter("danceability", "<=", danceability[1]))
            .where(filter=FieldFilter("valence", ">=", valence[0]))
            .where(filter=FieldFilter("valence", "<=", valence[1]))
            .where(filter=FieldFilter("energy", ">=", energy[0]))
            .where(filter=FieldFilter("energy", "<=", energy[1]))
            .stream()
        )
        track_docs_foreign = list(
            extensions.db.collection("TracksPopular")
            .where(filter=FieldFilter("danceability", ">=", danceability[0]))
            .where(filter=FieldFilter("danceability", "<=", danceability[1]))
            .where(filter=FieldFilter("valence", ">=", valence[0]))
            .where(filter=FieldFilter("valence", "<=", valence[1]))
            .where(filter=FieldFilter("energy", ">=", energy[0]))
            .where(filter=FieldFilter("energy", "<=", energy[1]))
            .stream()
        )
            
    except:
        raise CustomException(ErrorCode.FAILED_FILTERING_TRACKS)
    
     # 추천 음악 문서 3개 랜덤 택
    try:
        recommend_track_docs = random.sample((track_docs_kpop + track_docs_foreign), 3)
    except:
        raise CustomException(ErrorCode.FAILED_SAMPLING_TRACKS)
    
    
    # 추천 음악 정보 리스트 구성
    recommend_track_list = []
    for doc in recommend_track_docs:
            data = doc.to_dict()
            
            track_info = {
                "trackId" : doc.id,
                "title" : data["track_name"],
                "artist": data["track_artist"]
            }
            
            error = track_info_schema.validate(track_info)
            if error:
                raise CustomException(ErrorCode.WRONG_TRACK_INFO)
            
            recommend_track_list.append(track_info)
    
    return recommend_track_list