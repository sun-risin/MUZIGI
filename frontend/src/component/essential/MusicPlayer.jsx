import React, { useState, useEffect, useRef } from 'react'; // useRef import
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner, faHeart } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId, onToggleLike, emotion, playlistTracks }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null); // 타이머 ID 저장을 위한 ref
  const isLiked = playlistTracks.some(item=>item.trackId===music.trackId);
  //1> 타이머 즉시 취소
  const handlePlayPause = async () => {
     if (previewTimerRef.current) {
       clearTimeout(previewTimerRef.current);
       previewTimerRef.current = null;
      }

     const token = localStorage.getItem('spotifyAccessToken');
     const player = window.SpotifyPlayerInstance;

     if (!player || !isPlayerReady || !deviceId || !token) {
       console.warn("플레이어 준비 안됨, deviceId 또는 토큰 없음");
       return;
     }

     //2> 일시 정지 로직
     if (isPlaying) {
       try {
         await player.pause();//Chat 컴포넌트에서 만든 sdk 인스턴스(현재 재생 음악 즉시 멈춤)
         setIsPlaying(false); // UI를 '재생' 아이콘으로 변경
         console.log("수동 일시정지 성공");
       } catch (e) {
         console.error("수동 일시정지 실패:", e);
         setIsPlaying(false);
       }
     } else { //3> 재생 로직
       try {
         const response = await fetch(// 스포티파이 웹 api 호출
           `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
           {
             method: 'PUT',
             headers: {
               'Authorization': `Bearer ${token}`,
               'Content-Type': 'application/json',
             },
           body: JSON.stringify({
             uris: [`spotify:track:${music.trackId}`],
             position_ms: 0,
             }),
           }
         );
         if (!response.ok) {
           const errorBody = await response.json();
           console.error('Spotify API 오류 본문:', errorBody); 
           throw new Error(`Spotify API failed with status ${response.status}`);
         }
         setIsPlaying(true); // UI를 '일시정지' 아이콘으로 변경
         console.log("수동 재생 시작");

         previewTimerRef.current = setTimeout(() => {
           if (window.SpotifyPlayerInstance) {
             window.SpotifyPlayerInstance.pause();
             setIsPlaying(false); // 30초 후 '재생' 아이콘으로 변경
             previewTimerRef.current = null;
             console.log("30초 미리듣기 타이머 종료");
           }
         }, 30000);

       }catch (error) {
         console.error("Spotify 재생 API 호출 실패:", error);
         setIsPlaying(false); // 실패 시 '재생' 아이콘으로 되돌림
       }
  }
 };

//좋아요 버튼 클릭 로직
const handleLike = () =>{
  onToggleLike({...music, emotion: emotion});
  if (!isLiked) {
       console.log(`${music.title} - 좋아요! (${emotion})`);
      } else {
        console.log(`${music.title} - 좋아요 취소! (${emotion})`);
      }
}

const handleLogin = () => {
  console.log("로그인 시도... 기존 토큰(spotifyAccessToken)을 삭제합니다.");
  localStorage.removeItem('spotifyAccessToken'); 
  window.location.href = 'http://127.0.0.1:5000/api/spotify/auth/login';
};

return (
     <div className="music-player-container">
     <div className="track-info">
       <p className="track-title">{music.title || '제목 정보 없음'}</p>
       <p className="track-artist">{music.artist || '아티스트 정보 없음'}</p>
     </div>

  {isPlayerReady ? (  
    <div className="player-controls"> 
     <button
       type="button"//1. 재생 버튼
       onClick={handlePlayPause}
       className="play-pause-btn"
       disabled={!deviceId}
       >
     <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
     </button>
          
     <button
       type="button" //2. 좋아요 버튼
       onClick={handleLike}
       className={`like-btn ${isLiked ? 'liked' : ''}`}
     >
      <FontAwesomeIcon icon={faHeart} />
     </button>
    </div> 

     ) : (

    <div className="player-controls">
       <button //3. 로그인 버튼
        type="button"
        onClick={handleLogin} 
        className="play-pause-btn"
        title="Spotify 로그인 필요"
      >
       <FontAwesomeIcon icon={faSpinner} spin />
       </button>
     </div>
     )}
     </div>
   );
}

export default MusicPlayer;