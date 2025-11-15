import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';
import MusicPlayer from './MusicPlayer';

function Chat({ selectedChatId, messages, setMessages, onToggleLike, playlistTracks }) {
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const chatListRef = useRef(null);//스크롤할 ref 생성 
  const isInitialLoad=useRef(true);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [deviceId, setDeviceId] = useState(null);

  //1> 스포티파이 sdk 초기화
 useEffect(() => {
    const delay = 2500;
    // 2. "재생목록 생성" API 호출 함수 
    const createPlaylistsIfNeeded = async (spotifyToken) => {
      const muzigiToken = localStorage.getItem('accessToken');
      console.log("--- API 호출 직전 토큰 확인 ---");
      console.log("Muzigi 토큰 (accessToken):", muzigiToken);
      console.log("Spotify 토큰 (spotifyAccessToken):", spotifyToken);

      if (!muzigiToken || !spotifyToken){
        console.error("Muzigi 또는 Spotify 토큰이 null입니다! API 호출을 중단합니다.");
        return;
      } 

      try {
        console.log("감정별 재생목록 생성을 시도합니다...");
        const response = await fetch('http://localhost:5000/api/playlist/new', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `${muzigiToken}`
          },
          body: JSON.stringify({ 'spotifyToken': spotifyToken })
        });
        
        if (response.status === 201 || response.status === 200) {
          console.log("재생목록이 성공적으로 준비되었습니다.");
        } else {
          const errorData = await response.json();
          console.error("재생목록 생성 실패: ", errorData);
        }
      } catch (error) {
        console.error("재생목록 생성 API 호출 실패:", error);
      }
    };

    // 3. SDK 콜백을 *즉시* 정의
    window.onSpotifyWebPlaybackSDKReady = () => {
      console.log("Spotify SDK Ready 콜백 실행됨!");
      
      // 4. 콜백 *내용물*의 실행을 "delay"만큼 (항상 2.5초) 지연
      setTimeout(() => {
        console.log(`딜레이(${delay}ms) 종료. SDK 초기화 시작.`);
        const token = localStorage.getItem('spotifyAccessToken');
        if (!token) {
          console.warn("Spotify SDK: 토큰이 없어 플레이어를 초기화할 수 없습니다.");
          return; 
        }

        // 💡 [추가] 5. SDK를 초기화하기 *직전에* "재생목록 생성" 함수를 호출합니다.
        createPlaylistsIfNeeded(token); 
        
        console.log("토큰 확인, Spotify Player 초기화 시작...");
        if (window.SpotifyPlayerInstance) {
          window.SpotifyPlayerInstance.disconnect();
        }
        
        const spotifyPlayer = new window.Spotify.Player({
          name: 'Muzigi Web Player',
          getOAuthToken: (cb) => { cb(token); },
          volume: 0.5
        });

        spotifyPlayer.addListener('ready', ({ device_id }) => {
         console.log('Spotify 플레이어 준비 완료, Device ID:', device_id);
          setIsPlayerReady(true);
          setDeviceId(device_id);
          window.SpotifyPlayerInstance = spotifyPlayer;

          const activateDevice = async () => {
            try {
              const res = await fetch("https://api.spotify.com/v1/me/player", {
                method: "PUT",
                headers: {
                  Authorization: `Bearer ${token}`,
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  device_ids: [device_id],
                  play: false, // 재생은 하지 않음
                }),
              });

              if (!res.ok) {
                console.error("디바이스 활성화 실패", await res.json());
              } else {
                console.log("🎧 Spotify 디바이스 활성화 성공");
              }
            } catch (err) {
              console.error("디바이스 활성화 오류:", err);
            }
          };
          activateDevice();
         });

        spotifyPlayer.addListener('authentication_error', ({ message }) => {
          console.error('Spotify 인증 실패 (토큰 만료 가능성):', message);
        });
        spotifyPlayer.connect().then(success => {
          if (success) console.log("Spotify 플레이어 성공적으로 연결됨");
        });
      }, delay);
    }; 

    const scriptId = 'spotify-playback-sdk';
    if (document.getElementById(scriptId)) {
      if (window.Spotify && window.onSpotifyWebPlaybackSDKReady) {
         console.log("Spotify SDK가 이미 로드됨. 콜백을 재실행합니다.");
         window.onSpotifyWebPlaybackSDKReady();
      }
    } else {
      const script = document.createElement('script');
      script.id = scriptId;
      script.src = 'https://sdk.scdn.co/spotify-player.js';
      script.async = true;
      document.body.appendChild(script);
    }

    // 클린업 로직
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
         //  봇 메시지(false)이고, 짝지을 trackIds가 있는지 확인
           if (msg.senderType === false && msg.recommendTracks && msg.recommendTracks.length > 0) {
             return (
             // 봇 챗버블 (플레이어 포함)
             <div key={index} className="chat-bubble left">
               <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
               <div className="message-content">
                 <p>{msg.content}</p>
                 <div className="music-list-container">
                   {msg.recommendTracks.map((track, i)=>(
                     <MusicPlayer 
                       key={i}
                       music={track}
                       isPlayerReady={isPlayerReady}
                       deviceId={deviceId}
                       playlistTracks={playlistTracks}
                       onToggleLike={onToggleLike}
                       emotion={msg.emotion}/>
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