import React, { useState, useEffect, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faSpinner } from '@fortawesome/free-solid-svg-icons';
import './MusicPlayer.css';

function MusicPlayer({ music, isPlayerReady, deviceId }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const previewTimerRef = useRef(null); // 30초 타이머 ID 저장을 위함

  // 컴포넌트가 사라질 때(unmount) 타이머가 남아있지 않도록 정리
  useEffect(() => {
    return () => {
      if (previewTimerRef.current) {
        clearTimeout(previewTimerRef.current);
      }
    };
  }, []);

  const handlePlayPause = async () => {
    // 1. 함수가 시작될 때, 이전에 예약된 30초 타이머가 있다면 즉시 취소
    if (previewTimerRef.current) {
      clearTimeout(previewTimerRef.current);
      previewTimerRef.current = null;
    }

    const token = localStorage.getItem('spotifyAccessToken');
    const player = window.SpotifyPlayerInstance;

    if (!player || !isPlayerReady || !deviceId || !token) {
      console.warn("플레이어 준비 안됨, deviceId 또는 토큰 없음", {
        isPlayerReady,
        deviceId,
        token: !!token,
      });
      return;
    }

    // 2. UI의 'isPlaying' 상태를 기준으로 동작을 결정 (API 호출 최소화)
    if (isPlaying) {
      // --- 의도: 일시정지 ---
      // (이미 재생 중이므로, SDK의 내장 pause()만 호출)
      try {
        await player.pause();
        setIsPlaying(false); // UI를 '재생' 아이콘으로 변경
        console.log("수동 일시정지 성공");
      } catch (e) {
        console.error("수동 일시정지 실패:", e);
        setIsPlaying(false); // 실패 시에도 UI는 복구
      }
    } else {
      // --- 의도: 재생 ---
      try {
        // 💡 [핵심 수정] 1단계: 이 브라우저(deviceId)로 재생을 *전송*(활성화)합니다.
        // 이것이 Premium 계정 + 올바른 Scope에도 발생하는 404 에러의 해결책입니다.
        const transferResponse = await fetch(
          `https://api.spotify.com/v1/me/player/play...`,
          {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              device_ids: [deviceId], // 이 기기를 활성화
              play: false,           // 재생은 아직 하지 않음
            }),
          }
        );

        if (!transferResponse.ok) {
          throw new Error(
            `Spotify (Transfer) API failed: ${transferResponse.status}`
          );
        }

        console.log("재생 기기 '활성화(Transfer)' 성공.");

        // 💡 [핵심 수정] 2단계: 기기 활성화가 성공하면, *그때* 트랙 재생을 요청합니다.
        const playResponse = await fetch(
          `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
          {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              uris: [`spotify:track:${music.trackId}`], // 재생할 트랙
              position_ms: 0,
            }),
          }
        );

        if (!playResponse.ok) {
          throw new Error(`Spotify (Play) API failed: ${playResponse.status}`);
        }

        setIsPlaying(true); // UI를 '일시정지' 아이콘으로 변경
        console.log("수동 재생 시작");

        // 3. 30초 미리듣기 타이머 시작
        previewTimerRef.current = setTimeout(() => {
          if (window.SpotifyPlayerInstance) {
            window.SpotifyPlayerInstance.pause();
            setIsPlaying(false); // '재생' 아이콘으로 복구
            previewTimerRef.current = null;
            console.log("30초 미리듣기 타이머 종료");
          }
        }, 30000); // 30초

      } catch (error) {
        console.error("Spotify 재생 API 호출 실패(전송 또는 재생):", error);
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
        // (로그인 안 됨 or SDK 로딩 중)
        <a
          href="http://127.0.0.1:5000/api/spotify/auth/login"
          className="play-pause-btn"
          title="Spotify 로그인 필요"
        >
          <FontAwesomeIcon icon={faSpinner} spin />
        </a>
      )}
    </div>
  );
}

export default MusicPlayer;