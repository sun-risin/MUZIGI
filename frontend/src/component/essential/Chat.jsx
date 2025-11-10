import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';
import MusicPlayer from './MusicPlayer'; // 👈 1. MusicPlayer 임포트

// 2. (신규!) 봇 멘트 텍스트를 파싱(해석)해서 노래 목록과 짝짓는 함수
function parseAndZipMusic(muzikiText, trackIds) {
  if (!muzikiText || !trackIds || trackIds.length === 0) {
    return { botMent: muzikiText, musicList: [] };
  }
  
  const lines = muzikiText.split('\n');
  const botMent = lines[0] || ''; // 봇 멘트 (첫 줄)
  const musicList = [];

  // 텍스트에서 제목/가수 추출
  const musicLines = lines.slice(1).filter(line => line.trim().startsWith('(')); // "(1) 제목: ..." 줄만 필터링
  
  musicLines.forEach((line, index) => {
    const match = line.match(/제목:\s*(.+?),\s*가수:(.+)/);
    
    if (match && trackIds[index]) { // 짝이 맞으면
      musicList.push({
        title: match[1].trim(),   // (1) 제목
        artist: match[2].trim(), // (2) 가수
        trackId: trackIds[index] // (3) 짝지어진 ID
      });
    }
  });

  return { botMent, musicList };
}

function Chat({ selectedChatId, messages, setMessages }) {
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const chatListRef = useRef(null);//스크롤할 ref 생성 
  const isInitialLoad=useRef(true);

  // 3. (신규!) selectedChatId가 바뀔 때마다 채팅 기록 불러오기
  useEffect(() => {
    isInitialLoad.current=true;
    const fetchChatHistory = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('accessToken');
      setNickname(localStorage.getItem('userNickname') || '방문자');

      if (selectedChatId && token) {
        try {
          const response = await fetch(`http://localhost:5000/api/chat/${selectedChatId}/messages`, {
            method: 'GET',
            headers: { 'Authorization': `${token}` }
          });
          if (!response.ok) throw new Error('채팅 기록 조회 실패');

          const historyData = await response.json();
          
          if (historyData && Array.isArray(historyData.messages)) {
            setMessages(historyData.messages);
          } else if (Array.isArray(historyData)) {
            setMessages(historyData);
          } else {
            console.error("API 응답 형식이 배열이 아닙니다:", historyData);
            setMessages([]);
          }
        } catch (error) {
          console.error("채팅 기록 조회 API 오류:", error);
          setMessages([{ senderType: false, content: '기록 조회 실패.' }]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setMessages([]);
        setIsLoading(false);
      }
    };
    fetchChatHistory();
  }, [selectedChatId, setMessages]); // selectedChatId가 바뀔 때마다 실행!

  // 🟢 Chat.jsx의 useLayoutEffect 훅을 이걸로 통째로 교체하세요

useLayoutEffect(() => {
  if (chatListRef.current) {
    const container = chatListRef.current;

    // 1. (먼저) 현재 상태를 체크합니다.
    //    - 지금이 첫 로드인가?
    //    - (또는) 사용자가 이미 맨 아래에 스크롤해 있는가?
    const isFirstLoad = isInitialLoad.current;
    const isScrolledToBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= 30;

    // 2. (나중에) 렌더링이 확실히 끝난 후(setTimeout 0) 스크롤을 실행합니다.
    setTimeout(() => {
      
      // (Case 1) 첫 로드인 경우 (반드시 실행)
      if (isFirstLoad && messages.length > 0) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'auto' // 'auto' (즉시 이동)
        });
        isInitialLoad.current = false; // 플래그 해제
      } 
      
      // (Case 2) 새 메시지이고, 사용자가 이미 맨 아래에 있었던 경우
      else if (isScrolledToBottom) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth' // 'smooth' (부드럽게 이동)
        });
      }

    }, 0); // 👈 이 setTimeout(0)이 두 경우 모두에 적용되는 것이 핵심입니다.
  }
}, [messages]); // 'messages' 배열이 바뀔 때마다 실행

  // 4. (수정!) 렌더링 로직
  return (
    <div className="chat-container" ref={chatListRef}>
      {messages.length === 0 && !isLoading && (
          <div className="chat-welcome">
             <img src={Muzigi} alt="헤드폰 로고" className="headphone-logo" />
             <div className="speech-bubble">
               <p>현재 감정을 뮤지기에게 알려주세요</p>
               <p>선택 시 {nickname} 님에게 알맞은 음악을 추천해 드릴게요!</p>
             </div>
           </div>
      )}

      <div className="chat-messages-list">
        {messages.map((msg, index) => {
          
          //  봇 메시지(false)이고, 짝지을 trackIds가 있는지 확인
          if (msg.senderType === false && msg.trackIds && msg.trackIds.length > 0) {
            // 텍스트를 파싱하고 trackId와 짝을 맞춤
            const { botMent, musicList } = parseAndZipMusic(msg.content, msg.trackIds);

            return (
              // 봇 챗버블 (플레이어 포함)
              <div key={index} className="chat-bubble left">
                <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
                <div className="message-content">
                  <p>{botMent}</p> {/* 멘트 텍스트 */}
                  <div className="music-list-container">
                    {musicList.map((track, i) => (
                      <MusicPlayer key={i} music={track} />
                    ))}
                  </div>
                </div>
              </div>
            );
          }

          return (
            <div key={index} className={`chat-bubble ${msg.senderType ? 'right' : 'left'}`}>
              {!msg.senderType && (
                <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
              )}
              <div className="message-content">
                <p>{msg.content}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Chat;