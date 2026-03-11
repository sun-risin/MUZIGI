import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./Login.css"; 

function Login({ setIsLoggedIn }) { 
  const navigate = useNavigate();
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleLogin = async () => {
    if (!userId || !password) {
      alert("아이디와 비밀번호를 모두 입력해주세요.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, password }),
      });

      const responseData = await response.json();

      if (responseData.success && responseData.data) {
        const {firstChatId, nickname, userToken,} = responseData.data;

        if (userToken && nickname&&firstChatId) {
          localStorage.setItem('chatId', firstChatId); 
          localStorage.setItem('userNickname', nickname);
          localStorage.setItem('accessToken', userToken);

          alert(responseData.message);//로그인 성공
          setIsLoggedIn(true); 
          navigate('/chat'); // 채팅 페이지로 이동
        } else {
          alert("로그인 정보가 부족합니다. 서버 데이터 확인 요망");
        }
      } else {
        alert(responseData.message);
      }
    } catch (error) {
      console.error("로그인 중 오류 발생:", error);
      alert("서버와 통신 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowSignUp = () => {
    navigate('/signup');
  };

  return (
    <div className="login">
      <h2 className="login-title">로그인</h2>
      <input
        type="text"
        placeholder="아이디를 입력해주세요"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        disabled={isLoading}
      />
      <input
        type="password"
        placeholder="비밀번호를 입력해주세요"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={isLoading}
      />
      <button className="login-button" onClick={handleLogin} disabled={isLoading}>
        {isLoading ? "로그인 중..." : "로그인"}
      </button>
      <button className="link-button" onClick={handleShowSignUp} disabled={isLoading}> 회원가입 </button>
    </div>
  );
}

export default Login;