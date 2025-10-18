import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./Login.css";

function Login({setIsLoggedIn}) {
  const navigate = useNavigate();

  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!userId || !password) {
      alert("아이디와 비밀번호를 모두 입력해주세요.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: userId,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.userToken) {
          localStorage.setItem('accessToken', data.userToken); // 로컬 스토리지에 토큰 저장
          alert("로그인 성공!");
          setIsLoggedIn(true);
          navigate('/chat');
        } else {
          alert("로그인에 성공했으나 토큰을 받지 못했습니다.");
        }
      } else {
        alert(data.message || "아이디 또는 비밀번호가 일치하지 않습니다.");
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
      <button
        className="login-button"
        onClick={handleLogin}
        disabled={isLoading}
      >
        {isLoading ? "로그인 중..." : "로그인"}
      </button>
      <button
        className="link-button"
        onClick={handleShowSignUp}
        disabled={isLoading}
      >
        회원가입
      </button>
    </div>
  );
}

export default Login;