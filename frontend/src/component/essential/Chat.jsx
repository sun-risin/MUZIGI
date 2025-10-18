import React, { useState, useEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';

function Chat() {

  const [nickname, setNickname] = useState('');

  useEffect(() => {
    // 로컬 스토리지에서 닉네임 가져오기
    const storedNickname = localStorage.getItem('userNickname');
    if (storedNickname) {
      setNickname(storedNickname);
    } else {
      setNickname('방문자'); // 오류 대비해 만들어놓음
    }
  }, []); 

  return (
    <div className="chat-container">

      <div className="chat-welcome">
        <img src={Muzigi} alt="헤드폰 로고" className="headphone-logo" />
        <div className="speech-bubble">
          <p>현재 감정을 뮤지기에게 알려주세요</p>
          <p>선택 시 {nickname} 님에게 알맞은 음악을 추천해 드릴게요!</p>
        </div>
      </div>
      </div>
  );
}

export default Chat;