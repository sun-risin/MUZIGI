from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from auth_routes import login_required
import random

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")
db = firestore.client()

# --- 감정 관련 모듈 ---
emotion = { # firestore에서 emotionName으로 매핑될 문서 ID
    "행복" : "happiness",
    "신남": "excited",
    "화남" : "aggro",
    "슬픔" : "sorrow",
    "긴장" : "nervous" }

# 감정 선택 -> 감정 기반 음악 특성, 공감 멘트, UI 반환
# TODO (반환) - 음악 특성, 멘트, UI
def select_emotion(emotionName):
    try:
        docId = emotion[emotionName]
    except KeyError: # 매핑되는 감정값이 없을 때
        return jsonify({"message": "잘못된 감정값"}), 400 
    
    emotion_doc = db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists():
        return jsonify({"message" : "감정 카테고리 관련 문서를 찾을 수 없습니다."}), 400

    emotion_docData = emotion_doc.to_dict()
    
    ments = emotion_docData["empathyMent"]
    if not ments:
        return jsonify({"message": "공감 멘트 리스트를 가져오지 못했습니다."}), 400
    else:    
        empathy_ment = random.choice(ments)
    
    return empathy_ment
    
    
# --- 메시지 저장 모듈 ---


# --- 음악 추천 ---


@chat_blp.route("/message", methods=["POST"])
@login_required
def send_messages():
    data = request.get_json()
    emotionName = data["emotionName"]
    
    
    
    