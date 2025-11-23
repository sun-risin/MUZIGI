import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight, faPlus, faPen, faMusic, faMessage, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';

const BASE_EMOTIONS=["행복", "신남", "화남", "슬픔", "긴장"];

function Sidebar({ isOpen, setIsOpen, setIsLoggedIn, playlistTracks }) {
  const sidebarRef = useRef(null);
  const navigate = useNavigate();

  const closeSidebar = (e) => {
    e.stopPropagation();
    setIsOpen(false);
  };

  // 로그아웃 함수
  const handleLogout = async() => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("chatId");
    localStorage.removeItem("userNickname");
    setIsLoggedIn(false);
    alert("로그아웃 되었습니다.");
    navigate("/login");
  };

  // "좋아요" 목록을 감정별로 그룹핑
  const likedTracksByEmotion = playlistTracks.reduce((acc, track) => {
    const emotion = track.emotion || '기타'; 
    if (!acc[emotion]) {
      acc[emotion] = [];
    }
    acc[emotion].push(track);
    return acc;
  }, {});

  // "기본 감정"과 "좋아요" 목록을 병합
  // (기본 감정 5개를 항상 보여주고, "좋아요"가 있으면 채워넣음)
  const allCategories = {};
  for (const emotion of BASE_EMOTIONS) {
    allCategories[emotion] = likedTracksByEmotion[emotion] || [];
  }

  return (
   <div ref={sidebarRef} className={`sidebar ${isOpen ? "open" : ""}`}>
       <div className="sidebar-header">
         <button onClick={closeSidebar} className="close-btn">
         <FontAwesomeIcon icon={faChevronRight} />
         </button>
       </div>

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

     <div className="sidebar-section playlist-section">
       <h3>
         <FontAwesomeIcon icon={faMusic} className="fa-icon" /> 재생 목록
       </h3>
       <div className="scrollable-list">
         {Object.keys(allCategories).map((emotion) => (
           <div key={emotion} className="playlist-category">
           <h4 className="playlist-emotion-title">{emotion}</h4>
           {allCategories[emotion].length > 0 ? (
             allCategories[emotion].map((track) => (
               <div key={track.trackId} className="playlist-item">
                 <p className="playlist-item-title">{track.title}</p>
                 <p className="playlist-item-artist">{track.artist}</p>
               </div>
              ))
             ) : (
             <div className="playlist-item-empty-category">
               좋아요를 눌러 음악을 추가하세요. </div>
            )}
           </div>
         ))}
       </div>
     </div>

        <div className="sidebar-section chatlist-section">
            <h3><FontAwesomeIcon icon={faMessage} className="fa-icon"/> 채팅 목록</h3>
            <div className="scrollable-list">
                <ul>
                    <li>채팅 1</li>
                    <li>채팅 2</li>
                </ul>
            </div>
        </div>

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