from ...extensions import db, firestore
from ...common.exception.customException import ErrorCode, CustomException
from .chat_schema import ChatSchema

from ..emotion.emotion_services import get_muzigi_message_config
from ..message.message_services import user_save_message, MUZIGI_save_message
from ..track.track_services import tracks_recommend

chat_schema = ChatSchema()

# TODO - UI 반영값 제공

# 새 채팅 생성 - 생성 채팅 아이디 반환
def create_chat(userDocId):
    # Firestore에 생성 및 저장
    new_chat_doc = db.collection("Chat").document() # 문서 생성
    new_chat_docId = new_chat_doc.id
    new_chat_doc.set({
        "chatId":new_chat_docId,
        "userDocId":userDocId,
        "createdAt": firestore.SERVER_TIMESTAMP
    })
    
    error = chat_schema.validate(new_chat_doc)
    if error:
        raise CustomException(ErrorCode.FAILED_CREATE_CHAT)

    return new_chat_docId

def emotion_select_get_recommend(emotionName, user_docId, chat_list):
    # --- 사용자 메시지
    # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    user_content = user_save_message(user_docId, chat_list[0], emotionName) 
    
    # --- 뮤지기 메시지 ---
    # 감정 문서, 뮤지기 공감 멘트, 추천 음악 특성값 받기
    muzigi_ment, track_traits = get_muzigi_message_config(emotionName)
    
    # 추천 음악 리스트 받기
    recommend_tracks = tracks_recommend(track_traits)
    
    # 메시지 저장 및 내용 얻기
    # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    muzigi_content = MUZIGI_save_message(chat_list[0], emotionName, muzigi_ment, recommend_tracks)
    
    
    # --- 반환 데이터
    response_data = {
        "user" : user_content,
        "MUZIGI" : muzigi_content,
        "recommendTracks" : recommend_tracks
    }
    
    return response_data