import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./Login.css";

function Login() { 
  const navigate = useNavigate();
  
  const [userId, setUserId] = useState(''); 
  const [password, setPassword] = useState('');

  const handleLogin = async () => { 
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

      if (response.ok) {
        const data = await response.json();
        console.log("로그인 성공!", data);
        navigate('/chat'); 
      } else {
        alert("아이디 또는 비밀번호가 일치하지 않습니다.");
      }
    } catch (error) {
      console.error("로그인 중 오류 발생:", error);
      alert("서버와 통신 중 오류가 발생했습니다.");
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
        onChange={(e) => setUserId(e.target.value)} // setter 함수도 수정!
      />
      <input 
        type="password" 
        placeholder="비밀번호를 입력해주세요"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="login-button" onClick={handleLogin}>로그인</button>
      <button className="link-button" onClick={handleShowSignUp}>회원가입</button>
    </div>
  );
}

export default Login;