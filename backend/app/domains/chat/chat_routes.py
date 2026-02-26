from flask import Blueprint, request

from ...common.apiResponse import ApiResponse
from ...common.exception.customException import ErrorCode, CustomException

from ..auth.decorater import login_required
from ..message.message_services import get_messages
from .chat_services import emotion_select_get_recommend

chat_blp = Blueprint("chat", __name__, url_prefix="/api/chat")

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
    # 채팅 주인이 맞는지 확인
    if chatId not in curr_user["chatIds"]:
        raise CustomException(ErrorCode.NOT_CHAT_OWNER)
    
    # 메시지 모음 리스트 받아오기
    message_list = get_messages(chatId) 
    
    return ApiResponse.success(
        status=200, message="채팅 기록 가져오기 성공",
        data={
            "chatId": chatId,
            "messages": message_list
        })