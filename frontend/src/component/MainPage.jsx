import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';

function MainPage() {
  return (
    <div className="main-page-container">
      {/* 왼쪽 컨텐츠 영역 */}
      <div className="content-area">
      <div className="chat-wrapper">
          <Chat /></div>
      <div className="emotion-wrapper">
          <Emotion /></div>
      </div>

      {/* 오른쪽 사이드바 영역 */}
      <div className="sidebar-area">
        <Sidebar /></div>
    </div>
  );
}

export default MainPage;