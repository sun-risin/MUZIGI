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

useEffect(()=>{
  const initialChatId = localStorage.getItem('chatId');
  if(initialChatId){
    setSelectedChatId(initialChatId);
  }
  else{
    console.warn("로컬스토리지에 chatId 없음, 채팅방 로드 불가");
  }
},[])//[]는 컴포넌트가 처음 마운트될 때 한 번만 실행

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

  const openSidebar = () =>{
    setIsSidebarOpen(true);
  }

  return (
    <div className="main-page-container">
      <div className= {`content-area ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="chat-wrapper">
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
        // onChatSelect={handleChatSelect} 나중에 주석 해제
        // currentChatId={selectedChatId}
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