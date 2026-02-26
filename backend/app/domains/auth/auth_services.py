from ...extensions import db, FieldFilter
from ..user.user_schema import RegisterUserSchema, UserSchema
from ...common.exception.customException import ErrorCode, CustomException
from .jwt_provider import generate_token

from ..chat.chat_services import create_chat
from werkzeug.security import generate_password_hash, check_password_hash

# --- 전역변수
register_user_schema = RegisterUserSchema() # 회원가입 입력값 validate용 schema
user_schema = UserSchema()                  # 회원 저장값 validate용 schema

# --- 회원 등록
def register_user(user_data):
    info_errors = register_user_schema.validate(user_data)
    if info_errors: # 회원가입 시 비번이나 닉네임 규칙에 맞지 않음
        raise CustomException(ErrorCode.INVALID_REGISTER_INFO)
    
    userId = user_data["userId"]
    password = user_data["password"]
    nickname = user_data["nickname"]
    
    # 아이디 중복 체크
    user_doc = db.collection("users").where(filter=FieldFilter("userId", "==", userId)).stream()
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
    
# --- 로그인
def get_token_and_user_info(login_data):
    # 입력값 유효성 검사
    login_data["nickname"] = "for_validate"    # 유효성 검사로 인해 닉네임 채워놓음
    
    info_errors = user_schema.validate(login_data)
    if info_errors:
        raise CustomException(ErrorCode.INVALID_LOGIN_INFO)
    
    # 회원 정보 조회
    userId = login_data["userId"]
    password = login_data["password"]
    
    user_doc = db.collection("users").where(filter=FieldFilter("userId", "==", userId)).stream()
    if not user_doc:
        raise CustomException(ErrorCode.FAILED_LOGIN)
    
    user_info = user_doc[0].to_dict()
    user_docId = user_info["userDocId"]
    doc_password = user_info["password"]
    doc_nickname = user_info["nickname"]
    doc_firstChatId = user_info["chatIds"][0]
    
    # 비밀번호 일치 확인
    password_chk = check_password_hash(doc_password, password)
    if password_chk:    
        userToken = generate_token(user_docId, doc_nickname)
        
        response_data = {
            "userToken": userToken,
            "nickname" : doc_nickname,          # 뮤지기 첫 버블에 나타낼 닉네임
            "firstChatId" : doc_firstChatId,    # 채팅 첫 아이디 - 로그인 시 첫 채팅으로 자동 로드
        }
        
        return response_data
    
    else:               
        # 비밀번호 다름 => 로그인 실패
        raise CustomException(ErrorCode.FAILED_LOGIN)