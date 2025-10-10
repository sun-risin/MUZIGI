import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import Layout from './component/Layout'; // Layout.jsx 경로에 맞게 수정
import Login from './component/Login';   // Login.jsx 경로에 맞게 수정
import SignUp from './component/SignUp'; // SignUp.jsx 경로에 맞게 수정
import MainPage from './component/MainPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/chat" element={<MainPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;