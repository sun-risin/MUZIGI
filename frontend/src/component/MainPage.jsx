import React, { useState } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';

const emotionSentences = {
  "행복": "현재 내가 느끼는 감정은 행복 입니다",
  "신남": "현재 내가 느끼는 감정은 신남 입니다",
  "화남": "현재 내가 느끼는 감정은 화남 입니다",
  "슬픔": "현재 내가 느끼는 감정은 슬픔 입니다",
  "긴장": "현재 내가 느끼는 감정은 긴장 입니다",
};

function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [messages, setMessages] = useState([]);

  const handleEmotionSelect = async (emotion) => {
    
    const userText = emotionSentences[emotion] || `현재 내가 느끼는 감정은 ${emotion} 입니다`;//메시지 자동 생성
    const newUserMessage = {
      sender: 'user',
      text: userText
    };

    setMessages(prevMessages => [...prevMessages, newUserMessage]);

    // 4. (나중에 주석 풀기) 실제 API 호출 코드 (지금은 CORS 에러로 실패)
    /*
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('http://127.0.0.1:5000/api/recommend', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ emotion: emotion, sentence: userText }) // 5. 문장도 함께 전송
      });

      if (!response.ok) throw new Error('서버 응답 실패');
      
      const data = await response.json(); 

      const botMessage = { 
        sender: 'bot', 
        text: data.botReply, // 멘트는 백엔드에서 받음
        music: data.music 
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);

    } catch (error) {
      console.error("음악 추천 API 오류:", error);
      const errorMsg = { sender: 'bot', text: '음악을 추천하는 데 실패했어요. (CORS 확인!)' };
      setMessages(prevMessages => [...prevMessages, errorMsg]);
    }
    */

    

    // 임시화면, 실제 실행 시 코드 삭제
    // ================================================================
    const nickname = localStorage.getItem('userNickname') || '사용자';
    const botMessage = {
      sender: 'bot',
      text: `네, '${emotion}'에 알맞은 음악을 ${nickname} 님에게 추천해드릴게요!`,
      music: [
        { "artist": "최유리", "title": "밤, 바다" },
        { "artist": "구름", "title": "Prologue" }
      ]
    };
    //여기까지
    setTimeout(() => {
      setMessages(prevMessages => [...prevMessages, botMessage]);
    }, 1000);
  };

  return (
    <div className="main-page-container">
      <div className= 'content-area'>
        <div className="chat-wrapper">
          <Chat messages={messages} />
        </div>
        <div className="emotion-wrapper">
          <Emotion onEmotionSelect={handleEmotionSelect} />
        </div>
      </div>

      <Sidebar 
        isOpen={isSidebarOpen} 
        setIsOpen={setIsSidebarOpen} 
        setIsLoggedIn={setIsLoggedIn}
      />
    </div>
  );
}

export default MainPage;