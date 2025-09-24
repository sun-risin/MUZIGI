import { useState } from 'react'
import './App.css'
import Hello from './component/hello';
import Welcome from './component/welcome';


function App() {
  return <div className="App">
    <Hello />
    <Hello />
    <Welcome />
  </div>;
}

export default App
