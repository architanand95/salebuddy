import React, { useState, useEffect } from "react";
import "./App.css"; // Ensure you have an App.css file with the styles provided
import logo from './logo.svg'; // Adjust the path as necessary

const App = () => {
  const [clientId, setClientId] = useState("");
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [metrics, setMetrics] = useState({
    lead_interest: "Neutral",
    engagement_level: 0,
    conversion_likelihood: 0,
  });

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    websocket.onmessage = (event) => {
      const parsedData = JSON.parse(event.data);
      setChatLog((prevLog) => [...prevLog, parsedData.message]);
      setMetrics(parsedData.metrics);
    };

    return () => {
      websocket.close();
    };
  }, [clientId]);

  const sendMessage = () => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
    websocket.send(JSON.stringify({ message }));
    setMessage("");
  };

  return (
    <div className="container">
      <header className="app-header">
        <img src={logo} alt="People.ai logo" className="app-logo" />
        {/* <h1>Sales Chat Application</h1> */}
      </header>
      <div className="chat-window">
        <div>
          <input
            className="chat-input"
            type="text"
            value={clientId}
            placeholder="Enter your client ID"
            onChange={(e) => setClientId(e.target.value)}
          />
        </div>
        <div>
          <input
            className="chat-input"
            type="text"
            value={message}
            placeholder="Enter your message"
            onChange={(e) => setMessage(e.target.value)}
          />
          <button className="send-button" onClick={sendMessage}>Send</button>
        </div>
        <div className="chat-log">
          <h2>Chat Log</h2>
          {chatLog.map((log, index) => (
            <p key={index} className="chat-bubble">{log}</p>
          ))}
        </div>
        <div className="metrics-panel">
          <h2>Metrics</h2>
          <p>Lead Interest: {metrics.lead_interest}</p>
          <p>Engagement Level: {metrics.engagement_level}</p>
          <p>Conversion Likelihood: {metrics.conversion_likelihood}%</p>
        </div>
      </div>
    </div>
  );
};

export default App;
