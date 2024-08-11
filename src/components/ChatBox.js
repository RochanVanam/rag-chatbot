// src/components/ChatBox.js
import React, { useState } from 'react';
import axios from 'axios';
import './ChatBox.css';

const ChatBox = () => {
  const [message, setMessage] = useState('');
  const [responses, setResponses] = useState([]);

  const sendMessage = async () => {
    if (message.trim() === '') return;

    setResponses([...responses, { user: 'user', text: message }]);
    setMessage('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chat', { message });
      setResponses([...responses, { user: 'user', text: message }, { user: 'bot', text: response.data.reply }]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {responses.map((response, index) => (
          <div key={index} className={`chat-bubble ${response.user}`}>
            {response.text}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatBox;
