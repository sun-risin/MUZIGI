from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from werkzeug.security import generate_password_hash, check_password_hash
from app.schemas.user_schema import UserSchema

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


# TODO: JWT로 로그인 유지
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
    
    # 비밀번호 일치 확인
    doc_password = user_docs[0].to_dict()["password"]
    password_chk = check_password_hash(doc_password, password)
    if password_chk:    # 로그인 성공
        doc_nickname = user_docs[0].to_dict()["nickname"]
        return jsonify({
            "nickname": doc_nickname,
            "message": " 로그인 성공!"
            }), 200 
    
    else:               # 비밀번호 다름 ; 로그인 실패
        return jsonify({"message": "비밀번호가 틀렸습니다."}), 409