from extensions import db
from backend.app.domains.user.user_schema import RegisterUserSchema, UserSchema
from app.common.exception.customException import ErrorCode, CustomException

from werkzeug.security import generate_password_hash
from backend.app.domains.chat.chat_routes import create_chat

register_user_schema = RegisterUserSchema()
user_schema = UserSchema()

def register_user(user_data):
    info_errors = register_user_schema.validate(user_data)
    if info_errors: # 회원가입 시 비번이나 닉네임 규칙에 맞지 않음
        raise CustomException(ErrorCode.UNVALID_REGISTER_INFO)
    
    userId = user_data["userId"]
    password = user_data["password"]
    nickname = user_data["nickname"]
    
    # 아이디 중복 체크
    user_doc = db.collection("users").where("userId", "==", userId).stream()
    if any(user_doc):
        raise CustomException(ErrorCode.DUPLICATE_USER)

    # 비밀번호 해싱
    hashed_pw = generate_password_hash(password)

    # 새로운 사용자 문서 & 첫 채팅 생성
    new_user_doc = db.collection("users").document() # 문서 생성
    new_user_docId = new_user_doc.id
    try:
        first_chatId = create_chat(new_user_docId)      # 첫 채팅 생성
    except:
        raise CustomException(ErrorCode.FAILED_CREATE_CHAT)
    
    # Firestore에 저장
    new_user_doc.set({
        "userId" : userId,                  # 사용자 설정 id
        "password" : hashed_pw,             # 암호화된 비밀번호
        "nickname" : nickname,              # 사용자 닉네임
        "userDocId" : new_user_docId,       # db 조회용 사용자 문서 id
        "chatIds": [first_chatId],          # 사용자 소유 채팅 아이디 리스트
        "playlistIds" : {}                  # 사용자 소유 감정 재생목록 아이디 딕셔너리
    })
    
    user_errors = user_schema.validate(new_user_doc)
    if user_errors:
        raise CustomException(ErrorCode.FAILED_REGISTER_USER)