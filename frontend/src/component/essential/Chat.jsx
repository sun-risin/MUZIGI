import "./Chat.css";

function Chat() {
  return (
    <div className="chat">
      <div className="chat-bubble left">
        현재 감정을 뮤지기에게 알려주세요.<br />
        선택 시 {}님에게 알맞은 음악을 추천해 드릴게요!
      </div>
      <div className="chat-bubble right">
        현재 내가 느끼는 감정은 {} 입니다
      </div>
      <div className="chat-bubble left">
        {}님에게 알맞은 음악을 추천할게요!
      </div>
    </div>
  );
}

export default Chat;
