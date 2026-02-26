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

# 토큰 까기
def extract_token(userToken: str):
    payload = jwt.decode(
        userToken, 
        current_app.config['MUZIGI_JWT_KEY'], algorithms=['HS256'])
    
    userDocId = payload["userDocId"]
    
    return userDocId