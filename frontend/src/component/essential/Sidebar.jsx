import React, { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom"; 
import "./Sidebar.css";

function Sidebar({ isOpen, setIsOpen, setIsLoggedIn }) {
  const sidebarRef = useRef(null);
  const navigate = useNavigate();

  const toggleSidebar = (e) => {
    e.stopPropagation();
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken"); // 로컬 스토리지에서 토큰 삭제
    setIsLoggedIn(false);
    alert("로그아웃 되었습니다.");
    navigate("/login"); // 로그인 페이지로 이동
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        isOpen &&
        sidebarRef.current &&
        !sidebarRef.current.contains(e.target)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [isOpen, setIsOpen]);

  return (
    <div className={`sidebar-container ${isOpen ? "open" : "closed"}`}>
      <button className="toggle-btn" onClick={toggleSidebar}>
        {isOpen ? ">" : "<"}
      </button>

      <div ref={sidebarRef} className="sidebar-content">
        <div className="sidebar-top">
          <button>새 채팅 +</button>
          <div className="profile">사용자 프로필 ✏️</div>
        </div>

        <div className="sidebar-middle">
          <h4>재생 목록</h4>
          <p>음악 1</p>
          <p>음악 2</p>

          <h4>채팅 목록</h4>
          <p>채팅 1</p>
          <p>채팅 2</p>
        </div>

        <div className="sidebar-bottom">
          <button onClick={handleLogout}>로그아웃</button>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;