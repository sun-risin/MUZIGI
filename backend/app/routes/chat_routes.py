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

# 모듈 호출 순서: (선) 감정 선택 -> (후) 감정 기반 음악 특성, 공감 멘트, UI 반환
# 감정 선택
def select_emotion(emotionName):
    try:
        docId = emotion[emotionName]
    except KeyError: # 매핑되는 감정값이 없을 때
        return jsonify({"message": "잘못된 감정값"}), 400 

    emotion_doc = db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists:
        return jsonify({"message" : "선택한 감정 카테고리 관련 문서를 찾을 수 없습니다."}), 400

    return emotion_doc.to_dict() # 선택한 감정에 따른 감정 문서 딕셔너리로 반환

# 감정 기반 음악 특성
def emotion_trackTraits(emotion_docData):
    track_traits = emotion_docData["trackTraits"]
    if not track_traits:
        return jsonify({"message" : "해당 감정 음악 특성 리스트를 찾지 못했습니다."}), 400
    
    return track_traits

# 감정에 따른 공감 멘트 제공
def emotion_empathy(emotion_docData):
    ments = emotion_docData["empathyMent"]
    if not ments:
        return jsonify({"message": "공감 멘트 리스트를 가져오지 못했습니다."}), 400
    else:    
        empathy_ment = random.choice(ments)
        
    return empathy_ment
    
# TODO - UI 반영값 제공

    
# --- 메시지 저장 모듈 ---


# --- 음악 추천 ---


@chat_blp.route("/message", methods=["POST"])
@login_required
def send_messages():
    data = request.get_json()
    emotionName = data["emotionName"]
    
    # 뮤지기 버블 내용 만드는 곳
    emotion_doc = select_emotion(emotionName)
    muzigi_empathy_ment = emotion_empathy(emotion_doc)
    recommend_track_traits = emotion_trackTraits(emotion_doc)