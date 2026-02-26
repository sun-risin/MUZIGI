from ...extensions import db, firestore
from ...common.exception.customException import ErrorCode, CustomException
from .message_schema import MessageSchema
from ..emotion.emotionMapping import EmotionMapping

import random

message_schema = MessageSchema()

# 사용자 메시지 저장 및 내용 반환. emotionName은 감정이름 (한글)
def user_save_message(userDocId, chatId, emotionName):
    content = random.choice( [
        f"제 감정은 지금 \"{emotionName}\"이에요.\n지금 들으면 좋을 음악을 추천해 주세요!",
        f"{emotionName}이라는 감정에 맞는 음악이 필요해요.",
        f"{emotionName}의 감정이 느껴질 때 듣기 좋은 음악이 있을까요?"
    ])
      
    # Firestore에 생성 및 저장
    new_message = db.collection("Message").document()
    new_message_docId = new_message.id
    new_message.set({
        "chatId":chatId,
        "messageId":new_message_docId,
        "emotionName" : EmotionMapping.kor_to_eng(emotionName),
        "content": content,
        "senderType": True,
        "senderId": userDocId,
        "recommendTracks": None, # 사용자는 음악 추천을 보내지 않음
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    error = message_schema.validate(new_message)
    if error:
        raise CustomException(ErrorCode.USER_MESSAGE_ERR)
    
    return content

# 뮤지기 버블 저장
def MUZIGI_save_message(chatId, emotionName, empathy, recommend):
    ment_recommend = ""
    for i in range(len(recommend)):
        reco = recommend[i]
        ment_recommend += f"\t({i+1}) 제목: {reco['title']}, 가수:{reco['artist']}\n"
    
    content = f"{empathy}\n\n추천 음악:\n{ment_recommend}"

    # Firestore에 생성 및 저장
    new_message = db.collection("Message").document()
    new_message_docId = new_message.id
    new_message.set({
        "chatId":chatId,
        "messageId":new_message_docId,
        "emotionName" : EmotionMapping.kor_to_eng(emotionName),
        "content": content,
        "senderType": False,
        "senderId": "MUZIGI",
        "recommendTracks": recommend,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    error = message_schema.validate(new_message)
    if error:
        raise CustomException(ErrorCode.MUZIGI_MESSAGE_ERR)
    
    return content

# 채팅방의 메시지 기록 리스트 반환
def get_messages(chatId):
    try:
        messages = (db.collection("Message")
                    .where("chatId", "==", chatId).order_by("created_at").stream())

        message_list = []
        for msg in messages:
            data = msg.to_dict()
            data.pop(chatId)
            
            message_list.append(data)
    except:
        raise CustomException(ErrorCode.FAILED_LOAD_MESSAGES)
        
    return message_list