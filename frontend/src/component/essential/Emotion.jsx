import React from 'react';
import './Emotion.css'; // CSS 파일 임포트

function Emotion({ onEmotionSelect }) {
  
  return (
    <div className="emotion"> 
      
      <button onClick={() => onEmotionSelect('행복')}>행복</button>
      <button onClick={() => onEmotionSelect('신남')}>신남</button>
      <button onClick={() => onEmotionSelect('화남')}>화남</button>
      <button onClick={() => onEmotionSelect('슬픔')}>슬픔</button>
      <button onClick={() => onEmotionSelect('긴장')}>긴장
      </button>
    </div>
  );
}

export default Emotion;