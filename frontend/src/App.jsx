import Sidebar from "./component/essential/Sidebar";
import Chat from "./component/essential/Chat";
import Emotion from "./component/essential/Emotion";
import "./App.css";

function App() {
  return (
    <div className="app-container">
      <div className="main-content">
        <Chat />
        <Emotion />
      </div>
      <Sidebar />
    </div>
  );
}

export default App;