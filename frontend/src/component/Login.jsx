import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./Login.css";

function Login() {
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

    // ================================================================
    // 토큰 확인하고 주석 풀기
    // ================================================================
    /*
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
        // 'data.token'임시로 이름 지정, 나중에 변경
        if (data.token) {
          localStorage.setItem('accessToken', data.token);
          alert("로그인 성공!");
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
    */

    // ================================================================
    //아래로 임시코드
    // ================================================================
    console.log("임시 로그인 성공! '/chat' 페이지로 이동합니다.");
    setTimeout(() => { 
      navigate('/chat');
      setIsLoading(false);
    }, 500); // 0.5초
  };
// 여기까지

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