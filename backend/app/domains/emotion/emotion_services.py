from extensions import db
from common.exception.customException import ErrorCode, CustomException
from emotionMapping import EmotionMapping

import random

# 감정 기반 음악 특성 최대최소값 반환
def emotion_trackTraits(emotion_docData):
    track_traits = emotion_docData["trackTraits"]
    if not track_traits:
        raise CustomException(ErrorCode.FAILED_LOAD_TRACK_TRAITS)
    
    try:
        emo_traits = {
            "danceabilityMin" : f"{track_traits['danceabilityMin']}",
            "danceabilityMax" : f"{track_traits['danceabilityMax']}",
            "energyMin" : f"{track_traits['energyMin']}",
            "energyMax" : f"{track_traits['energyMax']}",
            "valenceMin" : f"{track_traits['valenceMin']}",
            "valenceMax" : f"{track_traits['valenceMax']}"
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

# 감정 문서 및 뮤지기 메시지 구성 반환
def get_emotion_doc_and_muzigi_message(emotionName):
    # 감정 선택, 문서 찾기
    docId = EmotionMapping.kor_to_eng(emotionName)
    if docId == "wrong":
        raise CustomException(ErrorCode.FAILED_EMOTION_MAPPING)

    emotion_doc = db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists:
        raise CustomException(ErrorCode.FAILED_LOAD_EMOTION_DOC)
    
    # 뮤지기 버블 구성
    muzigi_ment = emotion_empathy(emotion_doc)
    track_traits = emotion_trackTraits(emotion_doc)

    return emotion_doc.to_dict(), muzigi_ment, track_traits