from flask import request
from ... import extensions
from ...common.exception.customException import ErrorCode, CustomException
from .jwt_provider import extract_token

from jwt import ExpiredSignatureError, InvalidTokenError
from functools import wraps

# 로그인 유지 확인 데코레이터 함수 
def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        userToken = request.headers.get("Authorization")
        
        # 토큰 없음
        if not userToken:
            raise CustomException(ErrorCode.NONE_TOKEN)

        # TODO - 유효기간 추가 논의
        try:
            userDocId = extract_token(userToken)           # payload에서 사용자 문서 ID 까줌
            
            user_doc = extensions.db.collection("users").document(userDocId).get()
            if not user_doc.exists: 
                raise CustomException(ErrorCode.INVALID_USER)
            
            # 사용자 문서 데이터 저장
            curr_user = user_doc.to_dict()
            
        # 유효기간 만료 & 토큰 문제    
        except ExpiredSignatureError:                       
            raise CustomException(ErrorCode.EXPIRED_TOKEN)
        except InvalidTokenError:                           
            raise CustomException(ErrorCode.INVALID_TOKEN)
        
        return func(curr_user, *args, **kwargs)
    
    return decorated_func