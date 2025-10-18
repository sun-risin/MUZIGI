import { useState } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';

// 1. App.jsx로부터 { setIsLoggedIn }을 props로 받습니다.
function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="main-page-container">
      <div className= 'content-area'>
        <div className="chat-wrapper">
          <Chat />
        </div>
        <div className="emotion-wrapper">
          <Emotion />
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