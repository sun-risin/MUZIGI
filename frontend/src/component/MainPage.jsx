import React, { useState } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';

function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [messages, setMessages] = useState([]); // 모든 채팅 메시지 관리

  const handleEmotionSelect = async (emotion) => {
    try {
      const token = localStorage.getItem('accessToken');
      
      const response = await fetch("http://localhost:5000/api/chat/message", { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `${token}` 
        },
        body: JSON.stringify({ emotionName: emotion })
      });

      if (!response.ok) throw new Error('서버 응답 실패');
      
      const data = await response.json(); 

      const newUserMessage = { 
        sender: 'user', 
        text: data.user 
      };

      const botMessage = { 
        sender: 'bot', 
        text: data.MUZIGI
      };
      
      setMessages(prevMessages => [...prevMessages, newUserMessage, botMessage]);

    } catch (error) {
      console.error("API 오류:", error);
      const errorMsg = { sender: 'bot', text: '메시지를 처리하는 데 실패했어요. (콘솔 확인!)' };
      setMessages(prevMessages => [...prevMessages, errorMsg]);
    }
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