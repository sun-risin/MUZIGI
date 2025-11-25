import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function SpotifyCallbackHandler() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const spotifyAccessToken = params.get('access_token');
    
    if (spotifyAccessToken) {
      // 토큰을 로컬 스토리지에 저장하고
      localStorage.setItem('spotifyAccessToken', spotifyAccessToken);
      console.log("Spotify 토큰 저장 완료 및 리다이렉트");

      // URL 매개변수를 제거한 깨끗한 '/chat' 주소로 이동합니다.
      navigate('/chat', { replace: true });
    } else {
      // 토큰을 받지 못했다면 로그인 페이지로 이동
      navigate('/login', { replace: true });
    }
  }, [location, navigate]);

  return <div>Spotify 인증 처리 중...</div>;
}

export default SpotifyCallbackHandler;