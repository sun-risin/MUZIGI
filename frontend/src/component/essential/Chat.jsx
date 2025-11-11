import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';
import MusicPlayer from './MusicPlayer';

function Chat({ selectedChatId, messages, setMessages }) {
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const chatListRef = useRef(null);//스크롤할 ref 생성 
  const isInitialLoad=useRef(true);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [deviceId, setDeviceId] = useState(null);

// Chat.jsx

  useEffect(() => {
    // 1. 콜백 함수를 *먼저* 전역(window)에 정의
    window.onSpotifyWebPlaybackSDKReady = () => {
      console.log("Spotify SDK Ready 콜백 실행됨!");
      const token = localStorage.getItem('spotifyAccessToken');
      if (!token) {
        console.warn("Spotify SDK: 토큰이 없어 플레이어를 초기화할 수 없습니다.");
        return; 
      }

      console.log("토큰 확인, Spotify Player 초기화 시작...");
      if (window.SpotifyPlayerInstance) {
        window.SpotifyPlayerInstance.disconnect();
      }
      
      const spotifyPlayer = new window.Spotify.Player({
        name: 'Muzigi Web Player',
        getOAuthToken: (cb) => { cb(token); },
        volume: 0.5
      });

      // 💡 [수정됨] 이 부분이 핵심입니다.
      spotifyPlayer.addListener('ready', ({ device_id }) => {
        console.log('Spotify 플레이어 준비 완료, Device ID:', device_id);
        
        // 1. deviceId와 전역 인스턴스는 즉시 저장합니다.
        setDeviceId(device_id);
        window.SpotifyPlayerInstance = spotifyPlayer;
        
        // 2. ❌ [기존 코드] setIsPlayerReady(true); 
        //    -> 이렇게 즉시 버튼으로 바꾸면 서버가 준비 안 돼서 404 에러 발생
        
        // 3. ✅ [수정 코드] 1.5초의 "안전 시간"을 줍니다.
        //    이 시간 동안 서버가 device_id를 등록할 시간을 버는 것입니다.
        setTimeout(() => {
          console.log("1.5초 지연 후 플레이어 UI (버튼) 활성화");
          // 1.5초 뒤에 스피너를 '재생' 버튼으로 바꿉니다.
          setIsPlayerReady(true); 
        }, 1500); // 1.5초 딜레이 (이 시간은 1000~2000 사이로 조절 가능)
      });

      spotifyPlayer.addListener('authentication_error', ({ message }) => {
        console.error('Spotify 인증 실패 (토큰 만료 가능성):', message);
        // (추후 토큰 갱신 로직 추가)
      });

      spotifyPlayer.connect().then(success => {
        if (success) console.log("Spotify 플레이어 성공적으로 연결됨");
      });
    };
    
    // 2. 스크립트 태그가 이미 DOM에 있는지 ID로 확인합니다.
    const scriptId = 'spotify-playback-sdk';
    if (document.getElementById(scriptId)) {
      if (window.Spotify) {
         console.log("Spotify SDK가 이미 로드됨. 콜백을 재실행합니다.");
         window.onSpotifyWebPlaybackSDKReady();
      }
    } else {
      // 스크립트 태그가 없다면 새로 생성합니다.
      console.log("Spotify SDK 스크립트 로딩 시작...");
      const script = document.createElement('script');
      script.id = scriptId; 
      script.src = 'https://api.spotify.com/v1/me/player/play3...';
      script.async = true;
      document.body.appendChild(script);
    }

    // 클린업 (컴포넌트가 사라질 때)
    return () => {
      if (window.SpotifyPlayerInstance) {
        window.SpotifyPlayerInstance.disconnect();
        console.log("Spotify 플레이어 연결 해제됨.");
      }
    };
  }, []); // [] : Chat 컴포넌트 마운트 시 *단 한 번* 실행

  // selectedChatId가 바뀔 때마다 채팅 기록 불러오기
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

  useLayoutEffect(() => {
    if (chatListRef.current) {
      const container = chatListRef.current;
      // 첫 로드인지, 스크롤이 현재 맨 아래에 있는지 확인
      const isFirstLoad = isInitialLoad.current;
      const isScrolledToBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= 30;
      // 렌더링이 확실히 끝난 후(setTimeout 0) 스크롤을 실행
      setTimeout(() => {
        // (Case 1) 첫 로드인 경우 (반드시 실행)
        if (isFirstLoad && messages.length > 0) {
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'auto' // 즉시 이동
          });
          isInitialLoad.current = false; // 플래그 해제
        }         
        // (Case 2) 새 메시지이고, 사용자가 이미 맨 아래에 있었던 경우
        else if (isScrolledToBottom) {
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 0);
    }
  }, [messages]); // 'messages' 배열이 바뀔 때마다 실행

  // 렌더링 로직
  return (
    <div className="chat-container" ref={chatListRef}>
          <div className="chat-welcome">
             <img src={Muzigi} alt="헤드폰 로고" className="headphone-logo" />
             <div className="speech-bubble">
               <p>현재 감정을 뮤지기에게 알려주세요</p>
               <p>선택 시 {nickname} 님에게 알맞은 음악을 추천해 드릴게요!</p>
             </div>
           </div>

      <div className="chat-messages-list">
        {messages.map((msg, index) => {
          //  봇 메시지(false)이고, 짝지을 trackIds가 있는지 확인
          if (msg.senderType === false && msg.recommendTracks && msg.recommendTracks.length > 0) {
            return (
              // 봇 챗버블 (플레이어 포함)
              <div key={index} className="chat-bubble left">
                <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
                <div className="message-content">
                  <p>{msg.content}</p> {/* 멘트 텍스트 */}
                  <div className="music-list-container">
                    {msg.recommendTracks.map((track, i)=>(
                      <MusicPlayer 
                        key={i}
                        music={track}
                        isPlayerReady={isPlayerReady}
                        deviceId={deviceId}/>
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