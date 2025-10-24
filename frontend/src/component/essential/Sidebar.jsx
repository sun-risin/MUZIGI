import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight, faPlus, faPen, faMusic, faMessage, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';

function Sidebar({ isOpen, setIsOpen, setIsLoggedIn }) {
  const sidebarRef = useRef(null);
  const navigate = useNavigate();

  const closeSidebar = (e) => {
    e.stopPropagation();
    setIsOpen(false);
  };

  // 로그아웃 함수
  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    setIsLoggedIn(false);
    alert("로그아웃 되었습니다.");
    navigate("/login");
  };

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
            <h3><FontAwesomeIcon icon={faMusic} className="fa-icon"/> 재생 목록</h3>
            <div className="scrollable-list">
                <ul>
                    <li>음악 1</li>
                    <li>음악 2</li>
                </ul>
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