import React, { useState, useEffect } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';

function MainPage({ setIsLoggedIn }) { 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]); 
  const [selectedChatId, setSelectedChatId] = useState(null);
  
  // 1. 한글 -> 영어 (서버 요청용)
  const moodMap = {
    "행복": "happiness",
    "신남": "excited",
    "화남": "aggro",
    "슬픔": "sorrow",
    "긴장": "nervous"
  };

  // [추가] 2. 영어 -> 한글 (화면 표시용 역방향 매핑)
  const engToKor = {
    "happiness": "행복",
    "excited": "신남",
    "aggro": "화남",
    "sorrow": "슬픔",
    "nervous": "긴장"
  };

  const [playlistTracks, setPlaylistTracks] = useState([]); 

  // 1. 재생목록 조회
  const fetchPlaylists = async () => {
    const muzigiToken = localStorage.getItem('accessToken');
    if (!muzigiToken) return;
    const emotions = ['행복', '신남', '화남', '슬픔', '긴장'];
    
    const promises = emotions.map(async (emotion) => {
      try {
        const engEmotion = moodMap[emotion]; 
        const response = await fetch(`http://localhost:5000/api/playlist/${engEmotion}/show`, {
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
              emotion: emotion // 여기는 이미 한글로 잘 들어가고 있음
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
      const uniqueTracks = allTracks.filter((v, i, a) => a.findIndex(t => (t.trackId === v.trackId)) === i);
      
      setPlaylistTracks(prev => {
         if (uniqueTracks.length === 0 && prev.length > 0) return prev;
         return uniqueTracks;
      });
    } catch (e) {
      console.error("재생목록 로드 실패");
    }
  };

  // 2. 좋아요 기능 (수정됨: 화면엔 한글로, 서버엔 영어로)
  const handleToggleLike = async (track) => {
    const isAlreadyLiked = playlistTracks.some(item => item.trackId === track.trackId);
    if (isAlreadyLiked) return; 

    if (!track.emotion) {
      console.error("❌ 오류: 감정 정보(emotion)가 없습니다.", track);
      alert("이 곡의 감정 정보를 찾을 수 없어 좋아요를 누를 수 없습니다.");
      return;
    }

    // [핵심 수정] 화면에 보여줄 때는 무조건 '한글'로 통일해야 사이드바에 뜹니다!
    // track.emotion이 'excited'라면 '신남'으로 바꾸고, 이미 '신남'이면 그대로 둡니다.
    const uiEmotion = engToKor[track.emotion] || track.emotion;

    console.log(`좋아요 클릭: ${track.title} (화면용: ${uiEmotion})`);

    const newTrack = {
      title: track.title,
      artist: track.artist,
      trackId: track.trackId,
      emotion: uiEmotion // <--- 한글 이름표 부착!
    };

    setPlaylistTracks(prev => {
      if (prev.some(t => t.trackId === newTrack.trackId)) return prev;
      return [...prev, newTrack];
    });

    const muzigiToken = localStorage.getItem('accessToken');
    const spotifyToken = localStorage.getItem('spotifyAccessToken');
    
    // 서버에 보낼 때는 다시 영어로 (또는 원래 값 사용)
    const engEmotion = moodMap[track.emotion] || track.emotion;

    try {
      const response = await fetch(`http://localhost:5000/api/playlist/${engEmotion}/add`, {
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
      const response = await fetch('http://localhost:5000/api/playlist/new', {
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

  // 4. 초기 실행
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');

    if (accessToken) {
      localStorage.setItem('spotifyAccessToken', accessToken);
      window.history.pushState({}, document.title, window.location.pathname);
      callNewPlaylist(accessToken); 
      fetchPlaylists(); 
    } else if (localStorage.getItem('spotifyAccessToken')) {
      fetchPlaylists();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); 

  useEffect(() => {
    const initialChatId = localStorage.getItem('chatId');
    if (initialChatId) setSelectedChatId(initialChatId);
  }, []);

  // 감정 선택
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