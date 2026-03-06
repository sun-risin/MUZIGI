from ... import extensions
from ...common.exception.customException import ErrorCode, CustomException
from .emotionMapping import EmotionMapping

import random

# 감정 기반 음악 특성 최대최소값 반환
def emotion_trackTraits(emotion_docData):
    track_traits = emotion_docData["trackTraits"]
    if not track_traits:
        raise CustomException(ErrorCode.FAILED_LOAD_TRACK_TRAITS)
    
    try:
        emo_traits = {
            "danceability" : [track_traits['danceabilityMin'], track_traits['danceabilityMax']],
            "energy" : [track_traits['energyMin'], track_traits['energyMax']],
            "valence" : [track_traits['valenceMin'], track_traits['valenceMax']]
        }
    except:
        raise CustomException(ErrorCode.FAILED_LOAD_TRACK_TRAITS)
    
    return emo_traits


# 감정에 따른 공감 멘트 반환
def emotion_empathy(emotion_docData):
    ments = emotion_docData["empathyMent"]
    if not ments:
        raise CustomException(ErrorCode.FAILED_LOAD_EMPATHY)
    else:    
        empathy_ment = random.choice(ments)
        
    return empathy_ment

# 뮤지기 메시지 구성 반환
def get_muzigi_message_config(emotionName):
    # 감정 선택, 문서 찾기
    docId = EmotionMapping.kor_to_eng(emotionName)
    if docId == "wrong":
        raise CustomException(ErrorCode.WRONG_EMOTION_VAL)

    emotion_doc = extensions.db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists:
        raise CustomException(ErrorCode.FAILED_LOAD_EMOTION_DOC)
    
    # 뮤지기 버블 구성
    muzigi_ment = emotion_empathy(emotion_doc.to_dict())
    track_traits = emotion_trackTraits(emotion_doc.to_dict())

    return muzigi_ment, track_traits