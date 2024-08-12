// src/App.js
import React from 'react';
import ReactDOM from 'react-dom';
import ChatBox from './components/ChatBox';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>RAG Chatbot</h1>
      </header>
      <ChatBox />
    </div>
  );
}

export default App;

// ReactDOM.render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>,
//   document.getElementById('root')
// );
