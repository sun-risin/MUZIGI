from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from werkzeug.security import generate_password_hash, check_password_hash
from app.schemas.user_schema import UserSchema
import jwt
from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError

auth_blp = Blueprint("auth", __name__, url_prefix="/api/auth")
db = firestore.client()
user_schema = UserSchema()

# 회원가입
@auth_blp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    errors = user_schema.validate(data) # schema로 유효성 검사
    if errors:                          # 비번이나 닉네임 문제이므로 error 따로 출력
        return jsonify({
        "error": errors,
        "message": "유효하지 않은 입력값입니다."
    }), 400

    userId = data["userId"]
    password = data["password"]
    nickname = data["nickname"]

    # 아이디 중복 체크
    user_ref = db.collection("users").where("userId", "==", userId).stream()
    if any(user_ref):
        return jsonify({"error": "이미 존재하는 아이디입니다."}), 409

    # 비밀번호 해싱 후 저장 예정
    hashed_pw = generate_password_hash(password)

    # Firestore에 생성 및 저장
    db.collection("users").add({
        "userId": userId,
        "password": hashed_pw,
        "nickname": nickname
    })

    return jsonify({"message": "회원가입 성공"}), 201


# JWT 인증 로그인
@auth_blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    userId = data["userId"]
    password = data["password"]
    
    # 아이디로 회원 정보 가져오기
    user_docs = list(db.collection("users").where("userId", "==", userId).stream())
    
    # 아이디가 존재하지 않음
    if not user_docs:
        return jsonify({"message": "존재하지 않는 아이디입니다."}), 400 
    
    # 유저 정보 저장 -> 비밀번호, 닉네임
    user_info = user_docs[0].to_dict()
    doc_password = user_info["password"]
    doc_nickname = user_info["nickname"]
    
    # 비밀번호 일치 확인
    password_chk = check_password_hash(doc_password, password)
    if password_chk:    
        userToken = jwt.encode({ # 로그인 토큰
            'userId':userId, 'nickname':doc_nickname},
            current_app.config['MUZIGI_JWT_KEY'], algorithm='HS256') 
        
        return jsonify({
            "userToken": userToken,
            "message": " 로그인 성공!"
            }), 200     # 로그인 성공
    
    else:               # 비밀번호 다름 ; 로그인 실패
        return jsonify({"message": "비밀번호가 틀렸습니다."}), 409

    
# 로그인 유지 확인 데코레이터 함수 
def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        userToken = request.headers.get("Authorization")
        # 유저 토큰 없음
        if not userToken:
            return jsonify({"message": "토큰이 없습니다."}), 401

        # 나중에 유효기간 추가할 수도 있으니 포함해서 로직 구현
        try:
            # 토큰 디코딩 -> payload
            payload = jwt.decode(userToken, current_app.config['MUZIGI_JWT_KEY'], algorithm='HS256')
            userId = payload["userId"]
            user_docs = list(db.collection("users").where("userId", "==", userId))
            
            if not user_docs: 
                return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
            
            curr_user = user_docs[0].to_dict()
            
        except ExpiredSignatureError: # 유효기간 다 된 경우, 나중에 exp로 추가 가능
            return jsonify({"message": "토큰 만료"}), 401
        except InvalidTokenError:     # 토큰 값이 이상할 경우
            return jsonify({"message": "유효하지 않은 사용자 토큰"}), 401
        
        return func(curr_user, *args, *kwargs)
    
    return decorated_func