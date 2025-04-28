import { useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const sendPrompt = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setResponse("");
    try {
      const res = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setResponse("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <header className="chat-header">
          <h1>LLaMA 3 Chat</h1>
        </header>
        
        <div className="chat-messages">
          {response && (
            <div className="message response">
              <div className="message-content">
                <pre>{response}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-container">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            rows={3}
            className="chat-input"
          />
          <button 
            onClick={sendPrompt} 
            disabled={loading || !prompt.trim()}
            className="send-button"
          >
            {loading ? (
              <span className="loading-spinner"></span>
            ) : (
              "Send"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
