import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import './Chat.css';
import Muzigi from '../../assets/Muzigi.png';
import MusicPlayer from './MusicPlayer';

function Chat({ selectedChatId, messages, setMessages, onToggleLike, playlistTracks }) {
  const [nickname, setNickname] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const chatListRef = useRef(null);
  const isInitialLoad = useRef(true);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [deviceId, setDeviceId] = useState(null);

  // 1. 스포티파이 SDK 초기화
  useEffect(() => {
    const delay = 2500;
    const createPlaylistsIfNeeded = async (spotifyToken) => {
      const muzigiToken = localStorage.getItem('accessToken');
      if (!muzigiToken || !spotifyToken) return;
      try {
        const response = await fetch('http://localhost:5000/api/playlist/new', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `${muzigiToken}`
          },
          body: JSON.stringify({ 'spotifyToken': spotifyToken })
        });
        if (response.ok) console.log("재생목록 준비 완료");
      } catch (error) {
        console.error("재생목록 생성 API 호출 실패:", error);
      }
    };

    window.onSpotifyWebPlaybackSDKReady = () => {
      setTimeout(() => {
        const token = localStorage.getItem('spotifyAccessToken');
        if (!token) return;
        createPlaylistsIfNeeded(token);

        if (window.SpotifyPlayerInstance) window.SpotifyPlayerInstance.disconnect();

        const spotifyPlayer = new window.Spotify.Player({
          name: 'Muzigi Web Player',
          getOAuthToken: (cb) => { cb(token); },
          volume: 0.5
        });

        spotifyPlayer.addListener('ready', ({ device_id }) => {
          setIsPlayerReady(true);
          setDeviceId(device_id);
          window.SpotifyPlayerInstance = spotifyPlayer;
          
          fetch("https://api.spotify.com/v1/me/player", {
             method: "PUT",
             headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
             body: JSON.stringify({ device_ids: [device_id], play: false }),
          }).catch(e => console.error(e));
        });

        spotifyPlayer.connect();
      }, delay);
    };

    if (!document.getElementById('spotify-playback-sdk')) {
      const script = document.createElement('script');
      script.id = 'spotify-playback-sdk';
      script.src = 'https://sdk.scdn.co/spotify-player.js';
      script.async = true;
      document.body.appendChild(script);
    } else if (window.Spotify && window.onSpotifyWebPlaybackSDKReady) {
      window.onSpotifyWebPlaybackSDKReady();
    }
    return () => { if (window.SpotifyPlayerInstance) window.SpotifyPlayerInstance.disconnect(); };
  }, []);

  // 2. 채팅 기록 불러오기
  useEffect(() => {
    isInitialLoad.current = true;
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
          const historyData = await response.json();
          
          let fetchedMessages = [];
          if (historyData && Array.isArray(historyData.messages)) {
            fetchedMessages = historyData.messages;
          } else if (Array.isArray(historyData)) {
            fetchedMessages = historyData;
          }
          setMessages(fetchedMessages);
        } catch (error) {
          console.error(error);
          setMessages([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setMessages([]);
        setIsLoading(false);
      }
    };
    fetchChatHistory();
  }, [selectedChatId, setMessages]);

  // 3. 스크롤 처리
  useLayoutEffect(() => {
    if (chatListRef.current) {
      const container = chatListRef.current;
      if (isInitialLoad.current && messages.length > 0) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'auto' });
        isInitialLoad.current = false;
      } else if (container.scrollHeight - container.scrollTop - container.clientHeight <= 50) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
      }
    }
  }, [messages]);

  // 4. 렌더링
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
          if (msg.senderType === false && msg.recommendTracks && msg.recommendTracks.length > 0) {
            return (
              <div key={index} className="chat-bubble left">
                <img src={Muzigi} alt="봇 프로필" className="bot-profile-in-chat" />
                <div className="message-content">
                  <p>{msg.content}</p>
                  <div className="music-list-container">
                    {msg.recommendTracks.map((track, i) => {
                      const likedTrackInfo = playlistTracks.find(
                        likedItem => likedItem.trackId === track.trackId
                      );
                      const isLiked = !!likedTrackInfo;

                      // [핵심 수정] 백엔드가 보내주는 이름(emotionName)도 같이 확인!
                      // msg.emotionName : 백엔드 DB에서 불러온 값 (새로고침 후)
                      // msg.emotion     : 방금 프론트에서 생성한 값 (새로고침 전)
                      const resolvedEmotion = msg.emotionName || msg.emotion || track.emotion || likedTrackInfo?.emotion;

                      return (
                        <MusicPlayer
                          key={i}
                          music={track}
                          isPlayerReady={isPlayerReady}
                          deviceId={deviceId}
                          playlistTracks={playlistTracks}
                          isLiked={isLiked}
                          onToggleLike={onToggleLike}
                          emotion={resolvedEmotion} // 이제 DB 값을 제대로 읽어서 전달합니다
                        />
                      );
                    })}
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