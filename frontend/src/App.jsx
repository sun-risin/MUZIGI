import { useState } from "react";
import Sidebar from "./component/essential/Sidebar";
import Chat from "./component/essential/Chat";
import Emotion from "./component/essential/Emotion";
import Login from "./component/Login";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <div className={`app-container ${isLoggedIn ? "main" : "login"}`}>
      {isLoggedIn ? (
        <>
          <div className="main-content">
            <Chat />
            <Emotion />
          </div>
          <Sidebar />
        </>
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
