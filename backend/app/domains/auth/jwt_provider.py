import jwt
from flask import current_app

# jwt 토큰 생성
def generate_token(user_docId: str, doc_nickname: str):
    token = jwt.encode(
                { 
                    "userDocId":user_docId, 
                    "nickname":doc_nickname
                },
                current_app.config['MUZIGI_JWT_KEY'], algorithm= 'HS256')
    
    return token