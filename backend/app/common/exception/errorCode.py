# custom exception code 모음 파일

from enum import Enum

class ErrorCode(Enum):
    # --- 400
    UNVALID_REGISTER_INFO = ("4_000_UNVALID_REGISTER_INFO", "유효하지 않은 회원가입 입력값", 400)
    UNVALID_LOGIN_INFO = ("4_001_UNVALID_LOGIN_INFO", "유효하지 않은 로그인 입력값", 400)
    
    # --- 401
    FAILED_LOGIN = ("100_FAILED_LOGIN", "로그인 실패", 401)
    
    # --- 409
    DUPLICATE_USER = ("900_DUPLICATE_USER", "동일 아이디 존재", 409)
    
    # --- 500
    UNKNOWN_ERR = ("000_UNKNOWN_ERR", "알 수 없는 서버 내부 에러 발생", 500)
    FAILED_CREATE_CHAT = ("001_FAILED_CREATE_CHAT", "채팅 생성 중 에러 발생", 500)
    FAILED_REGISTER_USER = ("002_FAILED_REGISTER_USER", "회원가입 정보 저장 중 에러 발생", 500)
    
    # --- 생성자 메서드
    def __init__(self, code: str, message: str, status: int):
        self.code = code
        self.message = message
        self.status = status