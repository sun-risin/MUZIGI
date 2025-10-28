import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

import Layout from './component/Layout'; 
import Login from './component/Login'; 
import SignUp from './component/SignUp';
import MainPage from './component/MainPage';

function App() {

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      setIsLoggedIn(true); 
    }
    setIsLoading(false); 
  }, []); 

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