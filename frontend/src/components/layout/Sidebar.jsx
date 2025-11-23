import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight, faChevronDown, faPlus, faPen, faMusic, faMessage, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';

// 기본 감정 목록
const BASE_EMOTIONS = ["행복", "신남", "화남", "슬픔", "긴장"];

function Sidebar({ isOpen, setIsOpen, setIsLoggedIn, playlistTracks = [] }) {
  const sidebarRef = useRef(null);
  const navigate = useNavigate();
  const [openEmotions, setOpenEmotions] = useState({}); // 사이드바 재생목록 내 감정 토글 상태

  // 재생목록 감정 토글 함수(열고 닫기)
  const toggleEmotion = (emotion) => {
    setOpenEmotions(prev => ({
      ...prev, 
      [emotion]: !prev[emotion] // 상태 반대로 뒤집기
    }));
  };

  // 사이드바 닫기 버튼
  const closeSidebar = (e) => {
    e.stopPropagation();
    setIsOpen(false);
  };

  // 로그아웃 함수
  const handleLogout = async () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("spotifyAccessToken");
    localStorage.removeItem("chatId");
    localStorage.removeItem("userNickname");
    setIsLoggedIn(false);
    alert("로그아웃 되었습니다.");
    navigate("/login"); // 로그인 페이지 이동
  };

  // -------------------------------
  // 선호 표시 노래 '감정별' 표시
  const likedTracksByEmotion = playlistTracks.reduce((acc, track) => {
    const emotion = track.emotion || '기타'; 
    if (!acc[emotion]) {
      acc[emotion] = [];
    }
    acc[emotion].push(track);
    return acc;
  }, {});

  // "기본 감정"과 "좋아요" 목록을 병합
  const allCategories = {};
  for (const emotion of BASE_EMOTIONS) {
    allCategories[emotion] = likedTracksByEmotion[emotion] || [];
  }

  // ----------화면 렌더링---------------------
  return (
    <div ref={sidebarRef} className={`sidebar ${isOpen ? "open" : ""}`}>
      
      {/* 사이드바 닫기 */}
      <div className="sidebar-header">
        <button onClick={closeSidebar} className="close-btn">
          <FontAwesomeIcon icon={faChevronRight} />
        </button>
      </div>

      {/* 스크롤 영역 */}
      <div className="sidebar-scroll-area">
        
        {/* 새 채팅/ 프로필 메뉴 */}
        <div className="sidebar-section main-actions">
          <div className="action-item">
            <FontAwesomeIcon icon={faPlus} className="action-icon" />
            <span>새 채팅</span>
          </div>
          <div className="action-item">
            <FontAwesomeIcon icon={faPen} className="action-icon" />
            <span>사용자 프로필</span>
          </div>
        </div>

        {/* 재생목록 */}
        <div className="sidebar-section playlist-section">
          <h3><FontAwesomeIcon icon={faMusic} className="fa-icon"/> 재생 목록</h3>
          <div className="playlist-list">
            {Object.keys(allCategories).map((emotion) => (
              <div key={emotion} className="playlist-category">
                
                {/* 재생목록 내 토글 클릭 -> 목록 열고 닫기 */}
                <div 
                  className="playlist-emotion-header" 
                  onClick={() => toggleEmotion(emotion)}
                >
                  <span className="playlist-emotion-title">{emotion}</span>
                  {/* 토글 아이콘 */}
                  <FontAwesomeIcon 
                    icon={openEmotions[emotion] ? faChevronDown : faChevronRight} 
                    className="toggle-icon"
                    size="sm"
                  />
                </div>
                
                {/* 토글 내용 */}
                {openEmotions[emotion] && (
                  <div className="playlist-items-container">
                    {allCategories[emotion].length > 0 ? (
                      allCategories[emotion].map((track) => (
                        <div key={track.trackId} className="playlist-item">
                          <p className="playlist-item-title">{track.title}</p>
                          <p className="playlist-item-artist">{track.artist}</p>
                        </div>
                      ))
                    ) : (
                      <div className="playlist-item-empty-category">
                        (비어 있음)
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 채팅 목록(2차 완성 예정) */}
        <div className="sidebar-section chatlist-section">
          <h3><FontAwesomeIcon icon={faMessage} className="fa-icon"/> 채팅 목록</h3>
          <div className="chat-list">
            <div className="chat-item">채팅 1</div>
            <div className="chat-item">채팅 2</div>
          </div>
        </div>

      </div> {/* 스크롤 영역 끝 */}

      {/* 로그아웃 버튼 */}
      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-btn">
          <FontAwesomeIcon icon={faRightFromBracket} className="logout-icon" />
          로그아웃
        </button>
      </div>

    </div>
  );
}

export default Sidebar;