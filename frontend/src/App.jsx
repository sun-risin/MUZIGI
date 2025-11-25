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
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

    // 1. 함수 정의: TDZ 오류 방지를 위해 컴포넌트 내부에 정의합니다.
    const getSpotifyToken = async () => {
        const muzigiToken = localStorage.getItem('accessToken');
        
        // Muzigi 토큰 없으면 호출을 중단합니다. (이미 하위 useEffect에서 체크하지만 안전장치)
        if (!muzigiToken) {
            console.warn("Muzigi 토큰이 없어 Spotify 토큰 확인을 건너뜁니다.");
            return; 
        }

        try {
            // Muzigi JWT를 Authorization 헤더에 담아 보냅니다. (401 에러 해결)
            const response = await fetch(`${API_BASE_URL}/api/spotify/auth/token`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Authorization': muzigiToken 
                }
            });

            const data = await response.json();

            if (response.ok) {
                // 성공하면 (200 OK), 토큰을 로컬 스토리지에 저장
                localStorage.setItem('spotifyAccessToken', data.access_token);
                console.log("Spotify 토큰 저장 성공!");
            } else {
                // 실패하면 (401 Error), 아직 Spotify 로그인 안 한 것
                console.warn("Spotify 로그인이 필요합니다.", data.error);
            }
        } catch (error) {
            console.error("Spotify 토큰 API 통신 실패:", error);
        }
    };
    
    // 2. 첫 번째 useEffect: 앱 시작 시, 초기 Muzigi 로그인 상태만 확인 (최초 1회 실행)
    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            setIsLoggedIn(true); // Muzigi JWT가 있으면 로그인 상태 True
        }
        setIsLoading(false); // 초기 로딩 상태 종료
    }, []); 

    // 3. 두 번째 useEffect: isLoggedIn 상태가 True로 바뀔 때만 Spotify 토큰 요청 (Timing Fix)
    useEffect(() => {
        // 로그인 상태가 True로 확정되었을 때만 토큰 확인 함수를 실행합니다.
        if (isLoggedIn) {
            getSpotifyToken(); 
        }
    }, [isLoggedIn]); // isLoggedIn 상태 변화에 의존하여 실행

    if (isLoading) {
        return <div>로딩 중...</div>; 
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route element={<Layout isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />}>
                    {/* 기본 경로 Fix */}
                    <Route index element={isLoggedIn ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />} /> 
                    
                    {/* Login/Signup Route */}
                    <Route path="/signup" element={<SignUp />} />
                    <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} /> 
                    
                    {/* Chat Route */}
                    <Route path="/chat" element={isLoggedIn ? <MainPage setIsLoggedIn={setIsLoggedIn} /> : <Navigate to="/login" replace />}/>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}
export default App;