from flask import Blueprint, request

from common.apiResponse import ApiResponse
from auth.decorater import login_required
from chat_services import emotion_select_get_recommend

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")

# TODO - UI 반영값 제공

# 감정 선택 → 음악 추천
@chat_blp.route("/message", methods=["POST"])
@login_required
def messages(curr_user):
    
    data = request.get_json()
    emotionName = data["emotionName"]
    user_docId = curr_user["userDocId"]
    chat_list = curr_user["chatIds"]
    
    # 반환 데이터
    response_data = emotion_select_get_recommend(emotionName, user_docId, chat_list)
    
    return ApiResponse.success(
        status=201, message="뮤지기와 채팅 성공", 
        data=response_data)
    

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