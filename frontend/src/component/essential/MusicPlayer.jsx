import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

// 💡 music 객체 { title, artist, trackId }를 props로 받습니다.
function MusicPlayer({ music }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [player, setPlayer] = useState(null);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [deviceId, setDeviceId] = useState(null);

  // 1. Spotify SDK(리모컨) 초기화 (전역으로 관리)
  useEffect(() => {
    // SDK 중복 초기화 방지
    if (window.SpotifyPlayerInstance) {
        setPlayer(window.SpotifyPlayerInstance);
        setIsPlayerReady(window.SpotifyPlayerInstance.isReady || false);
        setDeviceId(window.SpotifyPlayerInstance.deviceId || null);
        return;
    }

    // App.jsx가 index.html에 SDK를 로드하면 이 함수가 실행됨
    window.onSpotifyWebPlaybackSDKReady = () => {
      // App.jsx가 저장한 Spotify 토큰을 가져옴
      const token = localStorage.getItem('spotifyAccessToken');
      
      // 🚨 토큰이 없으면 SDK 초기화 자체를 멈춤 (로그인 안 된 상태)
      if (!token) {
        console.warn("Spotify SDK: 토큰이 없어 플레이어를 초기화할 수 없습니다.");
        setIsPlayerReady(false); // 👈 isPlayerReady를 false로 유지
        return; 
      }

      // (토큰이 있을 때만) 플레이어 초기화 진행
      const spotifyPlayer = new window.Spotify.Player({
        name: 'Muzigi Web Player',
        getOAuthToken: (cb) => { cb(token); },
        volume: 0.5
      });

      spotifyPlayer.addListener('ready', ({ device_id }) => {
        console.log('Spotify 플레이어 준비 완료, Device ID:', device_id);
        setIsPlayerReady(true); // 👈 (중요) 이때 true로 변경
        setDeviceId(device_id);
        // ⭐️ 플레이어 인스턴스와 상태를 전역 객체에 저장
        window.SpotifyPlayerInstance = spotifyPlayer;
        window.SpotifyPlayerInstance.isReady = true;
        window.SpotifyPlayerInstance.deviceId = device_id;
      });

      spotifyPlayer.addListener('player_state_changed', (state) => {
        if (!state) return;
        setIsPlaying(!state.paused);
      });

      spotifyPlayer.addListener('authentication_error', ({ message }) => {
        console.error('Spotify 인증 실패:', message);
        // (선택) 여기서 토큰 갱신 API 호출
      });

      spotifyPlayer.connect();
      setPlayer(spotifyPlayer);
    };

    if (!window.Spotify) console.error("Spotify SDK 스크립트가 index.html에 없습니다.");
  }, []); // [] : 컴포넌트 마운트 시 한 번만 실행

  // 2. (수정됨) 재생/일시정지 전용 함수
  // (로그인 로직은 <a> 태그가 처리하므로 여기서 빠짐)
  const handlePlayPause = async () => {
    // 1. 플레이어가 준비되었는지 확인 (버튼이 보이므로 항상 true여야 함)
    if (!player || !isPlayerReady || !deviceId) {
      console.warn("Spotify 플레이어가 아직 준비되지 않았습니다.");
      return; 
    }
    
    const token = localStorage.getItem('spotifyAccessToken');

    // 2. 진짜 재생/일시정지 로직 실행
    try {
      const currentState = await player.getCurrentState();

      // (A) 이미 이 노래가 재생 중이면 -> 일시정지
      if (currentState && !currentState.paused && currentState.track_window.current_track.id === music.trackId) {
        player.pause();
      } else {
        // (B) 다른 노래거나 정지 상태면 -> 이 trackId로 재생
        await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            uris: [`spotify:track:${music.trackId}`],
            position_ms: 0
          })
        });

        // 30초 뒤 멈춤 기능
        setTimeout(() => {
          if (player && typeof player.pause === 'function') {
            player.pause();
          }
        }, 30000); 
      }
    } catch (error) {
      console.error("Spotify 재생 API 호출 실패:", error);
    }
  };

  // 3. (수정됨) 렌더링 로직
  return (
    <div className="music-player-container">
      <div className="track-info">
        <p className="track-title">{music.title || "제목 정보 없음"}</p>
        <p className="track-artist">{music.artist || "아티스트 정보 없음"}</p>
      </div>

      {isPlayerReady ? (
        // 로그인 된 상태-> 플레이어가 준비되면 -> 재생/일시정지 "버튼"
        <button 
          type="button" 
          onClick={handlePlayPause} 
          className="play-pause-btn" 
        >
          <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
        </button>
      ) : (
        // 로그인 안 된 상태-> 스포티파이로 이동-> 로그인 후 다시 돌아옴
        <a 
          href="http://127.0.0.1:5000/api/spotify/auth/login" 
          className="play-pause-btn"
        >
          <FontAwesomeIcon icon={faSpinner} spin />
        </a>
      )}
    </div>
  );
}

export default MusicPlayer;