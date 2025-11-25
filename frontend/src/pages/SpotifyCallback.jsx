import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function SpotifyCallbackHandler() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const spotifyAccessToken = params.get('access_token');
    
    if (spotifyAccessToken) {
      localStorage.setItem('spotifyAccessToken', spotifyAccessToken);
      console.log("Spotify 토큰 저장 완료 및 /chat으로 리다이렉트");
      navigate('/chat', { replace: true });
    } else {
      navigate('/login', { replace: true });
    }
  }, [location, navigate]);

  return <div>Spotify 인증 처리 중...</div>;
}

export default SpotifyCallbackHandler;
