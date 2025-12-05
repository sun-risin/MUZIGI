import React, { useState, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner, faHeart } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId, onToggleLike, emotion, playlistTracks = [] }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const isLiked = playlistTracks?.some(item => item.trackId === music.trackId);

  /** ---------------------------------------------------------
   *  🎯 Spotify 필수 단계: 재생 전 transferPlayback
   * ---------------------------------------------------------*/
  const transferPlayback = async (token, deviceId) => {
    const res = await fetch(`https://api.spotify.com/v1/me/player`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        device_ids: [deviceId],
        play: false
      })
    });

    if (!res.ok) {
      const err = await res.json();
      console.error("TransferPlayback 오류:", err);
      throw new Error("TransferPlayback 실패 " + res.status);
    }

    console.log("TransferPlayback 성공 → 이 디바이스가 active됨!");
  };

  /** ---------------------------------------------------------
   *  🎵 재생 / 일시정지
   * ---------------------------------------------------------*/
  const handlePlayPause = async () => {
    const token = localStorage.getItem('spotifyAccessToken');
    const player = window.SpotifyPlayerInstance;

    if (!player || !isPlayerReady || !deviceId || !token) {
      console.warn("플레이어 준비 안됨 / deviceId 없음 / 토큰 없음");
      return;
    }

    // 1) 기존 타이머 클리어
    if (previewTimerRef.current) {
      clearTimeout(previewTimerRef.current);
      previewTimerRef.current = null;
    }

    // 2) 일시정지
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

    // ▶ 3) 재생
    try {
      // 3-1) 재생 전 반드시 active device 설정
      await transferPlayback(token, deviceId);

      // 3-2) 즉시 Play API 호출 (트랙 직접 재생)
      const playRes = await fetch(`https://api.spotify.com/v1/me/player/play`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          uris: [`spotify:track:${music.trackId}`]
        })
      });

      if (!playRes.ok) {
        const err = await playRes.json();
        console.error("Play API 오류:", err);
        throw new Error("Play API 실패 " + playRes.status);
      }

      console.log("Play API 성공");

      setIsPlaying(true);

      // 30초 미리듣기
      previewTimerRef.current = setTimeout(() => {
        if (window.SpotifyPlayerInstance) {
          window.SpotifyPlayerInstance.pause();
          setIsPlaying(false);
          previewTimerRef.current = null;
        }
        console.log("30초 미리듣기 자동 종료");
      }, 30000);

    } catch (error) {
      console.error("재생 실패:", error);
      setIsPlaying(false);
    }
  };

  /** ---------------------------------------------------------
   *  👍 좋아요 기능
   * ---------------------------------------------------------*/
  const handleLike = () => {
    if (isLiked) return;
    onToggleLike({ ...music, emotion });
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
