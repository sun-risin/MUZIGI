import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';

function Chat() {
  return (
    <div className="chat-container">

      <div className="chat-welcome">
        <img src={Muzigi} alt="헤드폰 로고" className="headphone-logo" />
        <div className="speech-bubble">
          <p>현재 감정을 뮤지기에게 알려주세요</p>
          <p>선택 시 {} 님에게 알맞은 음악을 추천해 드릴게요!</p>
        </div>
      </div>

      {/* 기존 채팅 버블들은 이 아래에 위치하거나, 나중에 동적으로 추가될 수 있습니다. */}
      {/* <div className="chat-bubble left">...</div>
      <div className="chat-bubble right">...</div> 
      */}
    </div>
  );
}

export default Chat;