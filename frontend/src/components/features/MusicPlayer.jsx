import React, { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner, faHeart } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId, onToggleLike, emotion, playlistTracks = [] }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  // 1. 좋아요 상태 판별 (안전하게 처리)
  const isLiked = playlistTracks?.some(item => item.trackId === music.trackId);

  // 2. 재생/일시정지 로직
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

    if (isPlaying) {
      try {
        await player.pause();
        setIsPlaying(false);
        console.log("수동 일시정지 성공");
      } catch (e) {
        console.error("수동 일시정지 실패:", e);
        setIsPlaying(false);
      }
    } else {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/spotify/play`, // 👈 백엔드 프록시 엔드포인트로 교체`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
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
        setIsPlaying(true);
        console.log("수동 재생 시작");

        previewTimerRef.current = setTimeout(() => {
          if (window.SpotifyPlayerInstance) {
            window.SpotifyPlayerInstance.pause();
            setIsPlaying(false);
            previewTimerRef.current = null;
            console.log("30초 미리듣기 타이머 종료");
          }
        }, 30000);
      } catch (error) {
        console.error("Spotify 재생 API 호출 실패:", error);
        setIsPlaying(false);
      }
    }
  };

  // 3. 좋아요 버튼 클릭 핸들러
  const handleLike = () => {
    // [핵심] 이미 좋아요 상태라면 아무것도 하지 않음 (취소 불가)
    if (isLiked) {
      console.log("이미 좋아요한 곡입니다. (변화 없음)");
      return;
    }
    // 좋아요가 아닐 때만 API 호출
    onToggleLike({ ...music, emotion: emotion });
    console.log(`${music.title} - 좋아요 요청! (${emotion})`);
  };

  const handleLogin = () => {
    localStorage.removeItem('spotifyAccessToken');
    window.location.href = `${API_BASE_URL}/api/spotify/auth/login`;
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
            type="button"
            onClick={handlePlayPause}
            className="play-pause-btn"
            disabled={!deviceId}
          >
            <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
          </button>

          <button
            type="button"
            onClick={handleLike}
            className={`like-btn ${isLiked ? 'liked' : ''}`}
          >
            <FontAwesomeIcon icon={faHeart} />
          </button>
        </div>
      ) : (
        <div className="player-controls">
          <button
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