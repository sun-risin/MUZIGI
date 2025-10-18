from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore

emotion_blp = Blueprint("emotion", __name__, url_prefix="/api/emotion")
db = firestore.client()

emotion = { # firestore에서 emotionName으로 매핑될 문서 ID
    "행복" : "happiness",
    "신남": "excited",
    "화남" : "aggro",
    "슬픔" : "sorrow",
    "긴장" : "nervous" }

# 감정 선택, 
@emotion_blp.route("/select", methods=["POST"])
def emotion_select():
    data = request.get_json()
    emotionName = data["emotionName"]
    try:
        docId = emotion[emotionName]
    except: # 매핑되는 감정값이 없을 때
        return jsonify({"message": "잘못된 감정값"}), 400 
    
    
    emotion_doc = db.collection("emotionCategory").document(docId).get()
    