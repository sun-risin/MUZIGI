import React, { useState, useEffect } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';

function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]); // 모든 채팅 메시지 관리
  const [selectedChatId, setSelectedChatId] = useState(null);

  useEffect(() => {
    const initialChatId = localStorage.getItem('chatId'); // Login.jsx가 저장한 ID
    if(initialChatId){
      setSelectedChatId(initialChatId);
    }
    else{
      console.warn("로컬스토리지에 chatId 없음, 채팅방 로드 불가");
    }
  }, []);

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

      // 1. 사용자 메시지 생성
      const newUserMessage = { 
        senderType: true, // (Firestore 기준: true=사용자)
        content: data.user 
      };

      const botMessage = { 
        senderType: false, // (Firestore 기준: false=봇)
        content: data.MUZIGI,    // 봇 멘트 텍스트
        recommendTracks: data.recommendTracks
      };
      
      // 3. 두 메시지를 한꺼번에 추가
      setMessages(prevMessages => [...prevMessages, newUserMessage, botMessage]);

    } catch (error) {
      console.error("API 오류:", error);
      const errorMsg = { senderType: false, content: '메시지를 처리하는 데 실패했어요. (콘솔 확인!)' };
      setMessages(prevMessages => [...prevMessages, errorMsg]);
    }
  };

  return (
    <div className="main-page-container">
      <div className= {`content-area ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="chat-wrapper">
          {/* Chat 컴포넌트에 props 3개 전달 */}
          <Chat selectedChatId={selectedChatId} messages={messages} setMessages={setMessages} />
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
      
      {!isSidebarOpen&&(
        <button onClick={()=>setIsSidebarOpen(true)} className='sidebar-open-btn'>
          <FontAwesomeIcon icon={faBars}/>
        </button>
      )}
    </div>
  );
}

export default MainPage;