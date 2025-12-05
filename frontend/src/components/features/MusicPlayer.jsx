import React, { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner, faHeart } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId, onToggleLike, emotion, playlistTracks = [] }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const isLiked = playlistTracks?.some(item => item.trackId === music.trackId);

  const handlePlayPause = async () => {
    const token = localStorage.getItem('spotifyAccessToken');
    const player = window.SpotifyPlayerInstance;

    if (!player || !isPlayerReady || !deviceId || !token) {
      console.warn("플레이어 준비 안됨 / deviceId 없음 / 토큰 없음");
      return;
    }

    // 미리듣기 타이머 초기화
    if (previewTimerRef.current) {
      clearTimeout(previewTimerRef.current);
      previewTimerRef.current = null;
    }

    // ★ 일시정지
    if (isPlaying) {
      try {
        await player.pause();
        setIsPlaying(false);
        console.log("일시정지 성공");
      } catch (e) {
        console.error("일시정지 실패:", e);
      }
      return;
    }

    // ★ 재생 (정답 코드)
    try {
      console.log("▶ 재생 요청:", music.trackId);

      const playRes = await fetch("https://api.spotify.com/v1/me/player/play", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          uris: [`spotify:track:${music.trackId}`]   // ★ device_id 절대 넣지 않는다
        })
      });

      if (!playRes.ok) {
        const err = await playRes.json();
        console.error("Play API 오류:", err);
        throw new Error("Play API 실패 " + playRes.status);
      }

      console.log("Play API 성공");

      // SDK 재생
      await player.resume();
      setIsPlaying(true);

      // 30초 미리듣기 타이머
      previewTimerRef.current = setTimeout(() => {
        if (window.SpotifyPlayerInstance) {
          window.SpotifyPlayerInstance.pause();
          setIsPlaying(false);
          previewTimerRef.current = null;
        }
        console.log("30초 미리듣기 자동 종료");
      }, 30000);

    } catch (e) {
      console.error("재생 실패:", e);
      setIsPlaying(false);
    }
  };

  const handleLike = () => {
    if (isLiked) {
      console.log("이미 좋아요한 곡");
      return;
    }
    onToggleLike({ ...music, emotion });
  };

  const handleLogin = () => {
    localStorage.removeItem("spotifyAccessToken");
    window.location.href = `${API_BASE_URL}/api/spotify/auth/login`;
  };

  return (
    <div className="music-player-container">
      <div className="track-info">
        <p className="track-title">{music.title || "제목 정보 없음"}</p>
        <p className="track-artist">{music.artist || "아티스트 정보 없음"}</p>
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
            className={`like-btn ${isLiked ? "liked" : ""}`}
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
