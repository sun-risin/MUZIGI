from flask import Blueprint, request

from auth.decorater import login_required
from emotion.emotion_services import get_muzigi_message_config
from message.message_services import user_save_message, MUZIGI_save_message
from track.track_services import tracks_recommend

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")

# TODO - UI 반영값 제공

# 감정 선택 → 음악 추천
@chat_blp.route("/message", methods=["POST"])
@login_required
def messages(curr_user):
    
    data = request.get_json()
    emotionName = data["emotionName"]
    chat_list = curr_user["chatIds"]
    user_docId = curr_user["userDocId"]
    
    # --- 사용자 메시지 ---
    try:
        user_content = user_save_message(user_docId, chat_list[0], emotionName) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "사용자 버블 저장 중 오류 발생"}), 500
    
    
    # --- 뮤지기 메시지 ---
    # 감정 문서, 뮤지기 공감 멘트, 추천 음악 특성값 받기
    muzigi_ment, track_traits = get_muzigi_message_config(emotionName)
    
    # 추천 음악 리스트 받기
    recommend_tracks = tracks_recommend(track_traits)
    
    try:
        muzigi_content = MUZIGI_save_message(chat_list[0], emotionName, muzigi_ment, recommend_tracks) # TODO - 일단 채팅 1개인 상태, 추후 변경해야 됨
    except:
        return jsonify({"message": "뮤지기 메시지 저장 오류 발생"}), 500
    
    
    # --- 로직 모두 잘 돌아감 ---
    return jsonify({
        "message": "버블 테스트 성공\n",
        "user" : user_content,
        "MUZIGI" : muzigi_content,
        "recommendTracks" : recommend_tracks # 직접 넘겨주기도 함
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
                "recommendTracks" : data.get("recommendTracks"),
                "emotionName" : data.get("emotionName"),
                "created_at": data.get("created_at")
            })
        
        return jsonify({"chatId": chatId, "messages": message_list}), 200

    except Exception as e:
        print("메시지 가져오다 오류 남:", e)
        return jsonify({"message": "메시지 가져오기 오류"}), 500