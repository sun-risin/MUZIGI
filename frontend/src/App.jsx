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

    let content;
        if (isLoggedIn) {
            content = ( 
                <> <div className="main-content"> <Chat /> <Emotion /> </div> 
                <Sidebar /></>);
        } 
        else {
            content = <Login onLogin={handleLogin} />;
        }

    return <div className="app-container">{content}</div>;
    }

export default App;
