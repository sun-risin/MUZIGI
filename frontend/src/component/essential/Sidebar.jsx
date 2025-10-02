import "./Sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <button>닫기</button>
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
        <button>로그아웃</button>
      </div>
    </div>
  );
}

export default Sidebar;
