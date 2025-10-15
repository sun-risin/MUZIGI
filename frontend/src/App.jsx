import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import Layout from './component/Layout'; 
import Login from './component/Login';   
import SignUp from './component/SignUp';
import MainPage from './component/MainPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/chat" element={<MainPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;