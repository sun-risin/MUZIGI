from flask import Blueprint, request, jsonify, current_app

from auth_services import register_user

from app.common.apiResponse import ApiResponse

from werkzeug.security import  check_password_hash
import jwt
from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError

auth_blp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 회원가입
@auth_blp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    
    register_user(data) # 회원가입 서비스 로직

    return ApiResponse.success(
        status=201, message="회원가입 성공")


# JWT 인증 로그인
@auth_blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    data["nickname"] = "for_validate"    # 유효성 검사로 인해 닉네임 채워놓음
    errors = user_schema.validate(data) # schema로 유효성 검사
    if errors:
        return jsonify({
        "error": errors,
        "message": "유효하지 않은 입력값입니다."
    }), 400
    
    userId = data["userId"]
    password = data["password"]
    
    # 아이디로 회원 정보 가져오기
    user_docs = list(db.collection("users").where("userId", "==", userId).stream())
    
    # 아이디가 존재하지 않음
    if not user_docs:
        return jsonify({"message": "존재하지 않는 아이디입니다."}), 401
    
    # 유저 정보 저장 -> 비밀번호, 닉네임
    user_info = user_docs[0].to_dict()
    user_docId = user_info["userDocId"]
    doc_password = user_info["password"]
    doc_nickname = user_info["nickname"]
    doc_firstChatId = user_info["chatIds"][0]
    
    # 비밀번호 일치 확인
    password_chk = check_password_hash(doc_password, password)
    if password_chk:    
        userToken = jwt.encode({ # 로그인 토큰
            'userDocId':user_docId, 'nickname':doc_nickname},
            current_app.config['MUZIGI_JWT_KEY'], algorithm= 'HS256') 
        
        return jsonify({
            "userToken": userToken,
            "nickname" : doc_nickname, # 뮤지기 첫 버블 위해 바로 넘겨줌,
            "firstChatId" : doc_firstChatId, # 채팅 첫 아이디 - 로그인 시 첫 채팅으로 자동 로드되게 넘겨줌
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
            payload = jwt.decode(userToken, current_app.config['MUZIGI_JWT_KEY'], algorithms=['HS256'])
            userDocId = payload["userDocId"]
            user_doc = db.collection("users").document(userDocId).get()
            
            if not user_doc.exists: 
                return jsonify({"message": "유효하지 않은 사용자입니다."}), 401
            
            curr_user = user_doc.to_dict()
            
        except ExpiredSignatureError: # 유효기간 다 된 경우, 나중에 exp로 추가 가능
            return jsonify({"message": "토큰 만료"}), 401
        except InvalidTokenError:     # 토큰 값이 이상할 경우
            return jsonify({"message": "유효하지 않은 사용자 토큰"}), 401
        
        return func(curr_user, *args, **kwargs)
    
    return decorated_func

@auth_blp.route("/tokentest", methods=["GET"])
@login_required
def login_check(curr_user):
    return jsonify({
        "message": f"{curr_user['nickname']} 님, 인증 성공!"
    }), 200