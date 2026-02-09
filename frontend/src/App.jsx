import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/layout/Layout'; 
import Login from './pages/Login'; 
import SignUp from './pages/SignUp';
import MainPage from './pages/MainPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      setIsLoggedIn(true); 
    }
    setIsLoading(false);

    const getSpotifyToken = async () => {
      try {
        // (1) API 명세서에 나온 "토큰 확인" API 호출
        const response = await fetch('http://127.0.0.1:5000/api/spotify/auth/token', {
          method: 'GET',
          credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
          // (2) 성공하면 (200 OK), 토큰을 로컬 스토리지에 저장
          localStorage.setItem('spotifyAccessToken', data.access_token);
          console.log("Spotify 토큰 저장 성공!");
        } else {
          // (3) 실패하면 (401 Error), 아직 Spotify 로그인 안 한 것
          console.warn("Spotify 로그인이 필요합니다.", data.error);
        }
      } catch (error) {
        console.error("Spotify 토큰 API 통신 실패:", error);
      }
    };

    getSpotifyToken(); // 앱 시작 시 Spotify 토큰 받아오기 시도

  }, []); // [] : 앱 시작 시 한 번만 실행

  if (isLoading) {
    return <div>로딩 중...</div>; 
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />}>
          <Route path="/" element={isLoggedIn ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />} />
          <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/chat" element={isLoggedIn ? <MainPage setIsLoggedIn={setIsLoggedIn} /> : <Navigate to="/login" replace />}/>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;