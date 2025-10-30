from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.routes.auth_routes import login_required
import random

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")
db = firestore.client()

# TODO - 감정에 맞는 특성값 조정 필요 : 긴장, 슬픔... 이외 감정도 음악 듣고 별로면 변경해야 함

# --- 채팅 모듈 ---
# 새 채팅 생성 - 생성 채팅 아이디 반환
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
def emotion_select(emotionName):
    try:
        docId = emotion[emotionName]
    except KeyError: # 매핑되는 감정값이 없을 때
        return "매핑되는 감정값이 없음"

    emotion_doc = db.collection("emotionCategory").document(docId).get()
    if not emotion_doc.exists:
        return "감정 문서가 없음..."

    return emotion_doc.to_dict() # 선택한 감정에 따른 감정 문서 딕셔너리로 반환

# 감정 기반 음악 특성
def emotion_trackTraits(emotion_docData):
    track_traits = emotion_docData["trackTraits"]
    if not track_traits:
        return None
    
    try:
        emo_traits = {
            "danceabilityMin" : f"{track_traits['danceabilityMin']}",
            "danceabilityMax" : f"{track_traits['danceabilityMax']}",
            "energyMin" : f"{track_traits['energyMin']}",
            "energyMax" : f"{track_traits['energyMax']}",
            "valenceMin" : f"{track_traits['valenceMin']}",
            "valenceMax" : f"{track_traits['valenceMax']}"
        }
    except:
        return None
    
    return emo_traits

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
def MUZIGI_save_message(chatId, empathy, recommend):
    ment_recommend = ""
    for i in range(len(recommend)):
        reco = recommend[i]
        ment_recommend += f"\t({i+1}) 제목: {reco['title']}, 가수:{reco['artist']}\n"
    
    content = f"{empathy}\n\n추천 음악:\n{ment_recommend}"

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

# 사용자 버블 저장
def user_save_message(userDocId, chatId, emotionName):
    ments = [
        f"제 감정은 지금 \"{emotionName}\"이에요.\n 이 감정에 맞는 음악을 추천해 주세요!",
        f"\"{emotionName}\"라는 감정에 맞는 음악이 필요해요.",
        f"\"{emotionName}\"의 감정이 느껴질 때 듣기 좋은 음악이 있을까요?"
    ]
    content = random.choice(ments)
      
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
    
    return content

# --- 음악 추천 ---
def tracks_recommend(d, traits):
    traits = emotion_trackTraits(d)
    if traits is None:        return "특성 자체 못넘김"
    
    try:
        danceability = [traits["danceabilityMin"], traits["danceabilityMax"]]
        energy = [traits["energyMin"], traits["energyMax"]]
        valence = [traits["valenceMin"], traits["valenceMax"]]
    except:
        return "tratis에서 매핑을 못했어"
    
    filtered_tracks = []
    
    # Firestore에서 음악 특성값 기준 필터링 - 복합 인덱스 생성돼 있어야 함
    # TODO - 지금은 Kpop만 있음! 해외곡도 추가하기~
    try:
        track_docs = list(
            db.collection("TracksKpop")
            .where(filter=FieldFilter("danceability", ">=", float(danceability[0])))
            .where(filter=FieldFilter("danceability", "<=", float(danceability[1])))
            .where(filter=FieldFilter("valence", ">=", float(valence[0])))
            .where(filter=FieldFilter("valence", "<=", float(valence[1])))
            .where(filter=FieldFilter("energy", ">=", float(energy[0])))
            .where(filter=FieldFilter("energy", "<=", float(energy[1])))
            .stream()
        )
            
    except Exception as e:        
        print(e)
        return "db에서 못찾음"
    
    for doc in track_docs:
            data = doc.to_dict()
            filtered_tracks.append(data)
            
    try:
        recommend_track_list = random.sample(filtered_tracks, 3)
    except:
        return f"랜덤 샘플링 실패 - 결과값:{len(filtered_tracks)}"
    
    recommend_list = []
    for reco in recommend_track_list:
        song_info = {
            "title" : f'{reco["track_name"]}',
            "artist": f'{reco["track_artist"]}'}
        recommend_list.append(song_info)
    
    return recommend_list


# --- API ---
# 채팅 - 감정 선택 → 음악 추천
@chat_blp.route("/message", methods=["POST"])
@login_required
def messages(curr_user):
    if not curr_user:
        return jsonify({"message": "사용자 토큰 없음"}), 401
    
    data = request.get_json()
    emotionName = data["emotionName"]
    chat_list = curr_user["chatIds"]
    user_docId = curr_user["userDocId"]
    
    # --- 사용자 버블 ---
    try:
        user_content = user_save_message(user_docId, chat_list[0], emotionName) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "사용자 버블 저장 중 오류 발생"}), 500
    
    
    # --- 뮤지기 버블 ---
    emotion_doc = emotion_select(emotionName)
    if type(emotion_doc) is not dict:
        return jsonify({"message" : f'{emotion_doc}'}), 500
    
    muzigi_empathy_ment = emotion_empathy(emotion_doc)
    if muzigi_empathy_ment is None:
        return jsonify({"message": "공감 멘트 찾기 실패"}), 500
    
    recommend_track_traits = emotion_trackTraits(emotion_doc)
    if recommend_track_traits is None:
        return jsonify({"message": "추천 음악 특성값 찾기 실패"}), 500
    
    recommend_tracks = tracks_recommend(emotion_doc, recommend_track_traits)
    if recommend_tracks is None :
        return jsonify({"message": "추천 음악 리스트 생성 실패"}), 500
    if type(recommend_tracks) is not list:
        return jsonify({"message": f'{recommend_tracks}'}), 500
    
    try:
        muzigi_content = MUZIGI_save_message(chat_list[0], muzigi_empathy_ment, recommend_tracks) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "뮤지기 메시지 저장 오류 발생"}), 500
    
    
    # --- 로직 모두 잘 돌아감 ---
    return jsonify({
        "message": "버블 테스트 성공\n",
        "user" : user_content,
        "MUZIGI" : muzigi_content
    }), 200
    

# 채팅 기록 띄우기
@chat_blp.route("/<chatId>/messages", methods=["GET"])
@login_required
def chat_show_messages(curr_user, chatId):
    if not curr_user:
        return jsonify({"message": "사용자 토큰 없음"}), 401
    
    try:
        messages_ref = db.collection("Message").where("chatId", "==", chatId).order_by("created_at")
        messages = messages_ref.stream()

        message_list = []
        for msg in messages:
            data = msg.to_dict()
            message_list.append({
                "messageId": data.get("messageId"),
                "senderType": data.get("senderType"),
                "senderId": data.get("senderId"),
                "content": data.get("content"),
                "created_at": data.get("created_at")
            })
        
        return jsonify({"chatId": chatId, "messages": message_list}), 200

    except Exception as e:
        print("메시지 가져오다 오류 남:", e)
        return jsonify({"message": "메시지 가져오기 오류"}), 500