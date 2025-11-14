import React, { useState, useEffect, useRef } from 'react'; // useRef import
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null); // 타이머 ID 저장을 위한 ref

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

      } catch (error) {
        console.error("Spotify 재생 API 호출 실패:", error);
        setIsPlaying(false); // 실패 시 '재생' 아이콘으로 되돌림
      }
    }
  };

  return (
    <div className="music-player-container">
      <div className="track-info">
        <p className="track-title">{music.title || '제목 정보 없음'}</p>
        <p className="track-artist">{music.artist || '아티스트 정보 없음'}</p>
      </div>

      {isPlayerReady ? (
        <button
          type="button"
          onClick={handlePlayPause}
          className="play-pause-btn"
          disabled={!deviceId} // deviceId가 없으면 버튼 비활성화
        >
          <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
        </button>
      ) : (
        // (로그인 안 됨 or SDK 로딩 중) -> 로그인 버튼 / 스피너
        <a
          href="http://127.0.0.1:5000/api/spotify/auth/login"
          className="play-pause-btn"
          title="Spotify 로그인 필요"
        >
          {/* isPlayerReady가 false인 이유는 1.로그인 안함 or 2.SDK 로딩중
              두 경우 모두 스피너가 적절해 보입니다. */}
          <FontAwesomeIcon icon={faSpinner} spin />
        </a>
      )}
    </div>
  );
}

export default MusicPlayer;