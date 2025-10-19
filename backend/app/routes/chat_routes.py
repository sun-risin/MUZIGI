from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from app.routes.auth_routes import login_required
import random

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")
db = firestore.client()


# --- 채팅 모듈 ---
def create_chat(userDocId):
    # Firestore에 생성 및 저장
    new_chat_doc = db.collection("Chat").document() # 문서 생성
    new_chat_docId = new_chat_doc.id
    new_chat_doc.set({
        "chatId":new_chat_docId,
        "userDocId":userDocId,
        "createdAt": firestore.SERVER_TIMESTAMP
    })

    return new_chat_docId

# --- 감정 관련 모듈 ---
# firestore에서 emotionName으로 매핑될 문서 ID
emotion = {
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
        return None

    emotion_doc = db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists:
        return None

    return emotion_doc.to_dict() # 선택한 감정에 따른 감정 문서 딕셔너리로 반환

# 감정 기반 음악 특성
def emotion_trackTraits(emotion_docData):
    track_traits = emotion_docData["trackTraits"]
    if not track_traits:
        return None
    
    return track_traits

# 감정에 따른 공감 멘트 제공
def emotion_empathy(emotion_docData):
    ments = emotion_docData["empathyMent"]
    if not ments:
        return None
    else:    
        empathy_ment = random.choice(ments)
        
    return empathy_ment
    
# TODO - UI 반영값 제공

    
# --- 메시지 저장 모듈 ---
# 뮤지기 버블 저장
def MUZIGI_save_message(chatId, empathy, recommand):
    content = f"{empathy}\n\n추천 음악 특성:{recommand}"

    # Firestore에 생성 및 저장
    new_message = db.collection("Message").document()
    new_message_docId = new_message.id
    new_message.set({
        "chatId":chatId,
        "messageId":new_message_docId,
        "content": content,
        "senderType": False,
        "senderId": "MUZIGI",
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    return content

def user_save_message(userDocId, chatId, content):  
    # Firestore에 생성 및 저장
    new_message = db.collection("Message").document()
    new_message_docId = new_message.id
    new_message.set({
        "chatId":chatId,
        "messageId":new_message_docId,
        "content": content,
        "senderType": True,
        "senderId": userDocId,
        "created_at": firestore.SERVER_TIMESTAMP
    })

# --- 음악 추천 ---



@chat_blp.route("/messages", methods=["POST"])
@login_required
def messages(curr_user):
    if not curr_user:
        return jsonify({"message": "사용자 토큰 없음"}), 401
    
    data = request.get_json()
    emotionName = data["emotionName"]
    user_content = data["sentence"]
    chat_list = curr_user["chatIds"]
    user_docId = curr_user["userDocId"]
    
    # --- 사용자 버블 ---
    try:
        user_save_message(user_docId, chat_list[0], user_content) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "사용자 버블 저장 중 오류 발생"}), 400
    
    
    # --- 뮤지기 버블 ---
    emotion_doc = select_emotion(emotionName)
    if emotion_doc is None:
        return jsonify({"message" : "감정 문서 찾기 실패"}), 400
    
    muzigi_empathy_ment = emotion_empathy(emotion_doc)
    if muzigi_empathy_ment is None:
        return jsonify({"message": "공감 멘트 찾기 실패"}), 400
    
    recommend_track_traits = emotion_trackTraits(emotion_doc)
    if recommend_track_traits is None:
        return jsonify({"message": "추천 음악 특성값 찾기 실패"}), 400
    
    try:
        muzigi_content = MUZIGI_save_message(chat_list[0], muzigi_empathy_ment, recommend_track_traits) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "뮤지기 메시지 저장 오류 발생"}), 400
    
    
    # --- 로직 모두 잘 돌아감 ---
    return jsonify({
        "message": "버블 테스트 성공\n",
        "user" : user_content,
        "MUZIGI" : muzigi_content
    }), 200
    