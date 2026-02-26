from extensions import db, firestore
from common.exception.customException import ErrorCode, CustomException
from chat_schema import ChatSchema

chat_schema = ChatSchema()

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