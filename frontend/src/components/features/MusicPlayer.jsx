import React, { useState, useEffect } from 'react';
import Chat from '../components/features/Chat';
import Emotion from '../components/features/Emotion';
import Sidebar from '../components/layout/Sidebar';
import './MainPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';

// 1. 감정 변환 테이블 (FE-BE 통신 및 UI 표시용)
const moodMap = {
  "행복": "happiness",
  "신남": "excited",
  "화남": "aggro",
  "슬픔": "sorrow",
  "긴장": "nervous"
};

const engToKor = {
  "happiness": "행복",
  "excited": "신남",
  "aggro": "화남",
  "sorrow": "슬픔",
  "nervous": "긴장"
};

function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]); 
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [playlistTracks, setPlaylistTracks] = useState([]); 
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  // 1. 재생목록 조회 (Sidebar 로드용)
  const fetchPlaylists = async () => {
    const muzigiToken = localStorage.getItem('accessToken');
    if (!muzigiToken) return;
    const emotions = ['행복', '신남', '화남', '슬픔', '긴장'];
    
    const promises = emotions.map(async (emotion) => {
      try {
        // DB/API에 필요한 영어 감정으로 변환하여 URL에 사용
        const engEmotion = moodMap[emotion]; 
        const response = await fetch(`${API_BASE_URL}/api/playlist/${engEmotion}/show`, {
          method: 'GET',
          headers: { 'Authorization': `${muzigiToken}` }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.tracks) {
            return Object.values(data.tracks).map(track => ({
              title: track.title,
              artist: track.artist,
              trackId: track.trackId,
              emotion: emotion // 한국어로 저장하여 UI 표시용으로 사용
            }));
          }
        } 
        return [];
      } catch (error) {
        return [];
      }
    });

    try {
      const results = await Promise.all(promises);
      const allTracks = results.flat();
      // 중복 트랙 제거 로직
      const uniqueTracks = allTracks.filter((v, i, a) => a.findIndex(t => (t.trackId === v.trackId)) === i);
      
      setPlaylistTracks(prev => {
         if (uniqueTracks.length === 0 && prev.length > 0) return prev;
         return uniqueTracks;
      });
    } catch (e) {
      console.error("재생목록 로드 실패");
    }
  };

  // 2. 좋아요 기능
  const handleToggleLike = async (track) => {
    const isAlreadyLiked = playlistTracks.some(item => item.trackId === track.trackId);
    if (isAlreadyLiked) return; 

    if (!track.emotion) {
      console.error("❌ 오류: 감정 정보(emotion)가 없습니다.", track);
      alert("이 곡의 감정 정보를 찾을 수 없어 좋아요를 누를 수 없습니다.");
      return;
    }

  const uiEmotion = engToKor[track.emotion] || track.emotion;

    console.log(`좋아요 클릭: ${track.title} (화면용: ${uiEmotion})`);

    const newTrack = {
      title: track.title,
      artist: track.artist,
      trackId: track.trackId,
      emotion: uiEmotion 
    };

    setPlaylistTracks(prev => {
      if (prev.some(t => t.trackId === newTrack.trackId)) return prev;
      return [...prev, newTrack];
    });

    const muzigiToken = localStorage.getItem('accessToken');
    const spotifyToken = localStorage.getItem('spotifyAccessToken');
    
    const engEmotion = moodMap[track.emotion] || track.emotion; // 한국어 -> 영어 변환

    try { 
      const response = await fetch(`${API_BASE_URL}/api/playlist/${engEmotion}/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `${muzigiToken}`
        },
        body: JSON.stringify({
          spotifyToken: spotifyToken,
          trackInfo: { 
            title: track.title,
            artist: track.artist,
            trackId: track.trackId
          }
        })
      });

      if (!response.ok) {
        throw new Error("서버 저장 실패");
      }
    } catch (error) {
      console.error("좋아요 실패, 되돌립니다.", error);
      setPlaylistTracks(prev => prev.filter(t => t.trackId !== track.trackId));
      alert("오류가 발생해 좋아요가 취소되었습니다.");
    }
  };

  // 3. 재생목록 생성 API 호출
  const callNewPlaylist = async (spotifyToken) => {
    const muzigiToken = localStorage.getItem('accessToken'); 
    if (!muzigiToken || !spotifyToken) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/playlist/new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `${muzigiToken}`
        },
        body: JSON.stringify({ 'spotifyToken': spotifyToken })
      });

      if (response.ok) { 
        console.log("재생목록 준비 완료");
      }
    } catch (error) {
      console.error("재생목록 생성 연결 실패");
    }
  };

  // 4. 초기 실행 (URL 파라미터 처리)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');

    if (accessToken) {
      // Spotify OAuth 성공 후 토큰을 URL에서 받았을 때
      localStorage.setItem('spotifyAccessToken', accessToken);
      window.history.pushState({}, document.title, window.location.pathname);
      callNewPlaylist(accessToken); 
      fetchPlaylists(); 
    } else if (localStorage.getItem('spotifyAccessToken')) {
      // 이미 토큰이 localStorage에 있을 때 (새로고침 등)
      fetchPlaylists();
    }
  }, []); 

  // 5. 채팅 ID 로드
  useEffect(() => {
    const initialChatId = localStorage.getItem('chatId');
    if (initialChatId) setSelectedChatId(initialChatId);
  }, []);

  // 6. 🏆 UX FIX: Spotify 토큰 상태 감시 및 재생목록 자동 새로고침 (새로 추가된 로직)
  useEffect(() => {
    const intervailId = setInterval(() => {
      const spotifyToken = localStorage.getItem('spotifyAccessToken');
      
      // 토큰이 있고, 재생목록이 비어있다면 (즉, 방금 로그인하여 로드해야 할 때)
      if (spotifyToken && playlistTracks.length === 0) {
        fetchPlaylists();
        clearInterval(intervailId); // 성공했으니 interval 중지
      }
    }, 200); 

    // 컴포넌트 정리 함수
    return () => clearInterval(intervailId);
    
  }, [playlistTracks]); 

  // 감정 선택
  const handleEmotionSelect = async (emotion) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `${token}`
        },
        body: JSON.stringify({ emotionName: emotion })
      });

      if (!response.ok) throw new Error('서버 응답 실패');
      const data = await response.json();

      const newUserMessage = { senderType: true, content: data.user };
      const botMessage = {
        senderType: false,
        content: data.MUZIGI,
        recommendTracks: data.recommendTracks,
        emotion: emotion 
      };
      setMessages(prev => [...prev, newUserMessage, botMessage]);
    } catch (error) {
      console.error("API 오류:", error);
      setMessages(prev => [...prev, { senderType: false, content: '오류가 발생했습니다.' }]);
    }
  };

  return (
    <div className="main-page-container">
      <div className={`content-area ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="chat-wrapper">
          <Chat
            selectedChatId={selectedChatId}
            messages={messages}
            setMessages={setMessages}
            onToggleLike={handleToggleLike}
            playlistTracks={playlistTracks}
          />
        </div>
        <div className="emotion-wrapper">
          <Emotion onEmotionSelect={handleEmotionSelect} />
        </div>
      </div>

      <Sidebar
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        setIsLoggedIn={setIsLoggedIn}
        playlistTracks={playlistTracks}
      />

      {!isSidebarOpen && (
        <button onClick={() => setIsSidebarOpen(true)} className='sidebar-open-btn'>
          <FontAwesomeIcon icon={faBars} />
        </button>
      )}
    </div>
  );
}

export default MainPage;