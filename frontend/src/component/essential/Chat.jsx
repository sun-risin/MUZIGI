import React, { useState, useEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';

function Chat({selectedChatId, messages }) {
  const [nickname, setNickname] = useState('');

  // 닉네임은 Chat 컴포넌트가 직접 로컬 스토리지에서 가져옴 (환영 메시지용)
  useEffect(() => {
    const storedNickname = localStorage.getItem('userNickname');
    if (storedNickname) {
      setNickname(storedNickname);
    } else {
      setNickname('방문자');
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

      <div className="chat-messages-list">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.sender === 'user' ? 'right' : 'left'}`}>
            
            {msg.sender === 'bot' && (
              <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
            )}
            
            <div className="message-content">
              <p>{msg.text}</p>
              
              {msg.music && (
                <ol className="music-list">
                  {msg.music.map((song, i) => (
                    <li key={i}>{song.artist} - {song.title}</li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        ))}
      </div>
      
    </div>
  );
}

export default Chat;