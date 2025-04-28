import { useState, useRef, useEffect } from "react";
import "./App.css";

import { Mic, StopCircle } from "lucide-react";

// OPTIONAL: Uncomment to use SVG icons
// import { Mic, StopCircle } from "lucide-react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [isUploadCollapsed, setIsUploadCollapsed] = useState(true);
  const [isListening, setIsListening] = useState(false);

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setPrompt((prev) => (prev ? `${prev} ${transcript}` : transcript));
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } else {
      alert("Speech recognition is not supported in this browser.");
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

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
        body: JSON.stringify({
          model: "llama2",
          prompt: prompt,
          stream: false
        })
      });

      const data = await res.json();
      setResponse(data.response || "No response received.");
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

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadStatus({ message: "Uploading...", type: "loading" });

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      if (response.ok) {
        setUploadStatus({ 
          message: `Successfully uploaded ${file.name}`, 
          type: "success" 
        });
      } else {
        setUploadStatus({ 
          message: `Error: ${data.error}`, 
          type: "error" 
        });
      }
    } catch (err) {
      setUploadStatus({ 
        message: `Error: ${err.message}`, 
        type: "error" 
      });
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const toggleUpload = () => {
    setIsUploadCollapsed(!isUploadCollapsed);
  };

  return (
    <div className="App">
      <div className="main-container">
        <div className="chat-container">
          <header className="chat-header">
            <h1>ChatBot with RAG  </h1>
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
            <button 
              onClick={toggleListening}
              className={`mic-button ${isListening ? "listening" : ""}`}
              title={isListening ? "Stop Listening" : "Start voice input"}
            >
              {/* Emoji version */}
              {isListening ? <StopCircle size={18} /> : <Mic size={18} />}


              {/* Uncomment below for SVG icon version */}
              {/* {isListening ? <StopCircle size={18} /> : <Mic size={18} />} */}
            </button>
          </div>
        </div>

        <div className={`upload-container ${isUploadCollapsed ? 'collapsed' : ''}`}>
          <div className="upload-header" onClick={toggleUpload}>
            <h2>Upload Documents</h2>
            <button className="toggle-button">
              {isUploadCollapsed ? '▶' : '◀'}
            </button>
          </div>
          <div className="upload-content">
            <div className="upload-section">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".txt,.md,.pdf"
                style={{ display: 'none' }}
              />
              <button 
                className="upload-button"
                onClick={triggerFileInput}
                disabled={uploadStatus.type === "loading"}
              >
                {uploadStatus.type === "loading" ? (
                  <>
                    <span className="upload-spinner"></span>
                    Uploading...
                  </>
                ) : (
                  <>
                    <span className="icon">📁</span>
                    Upload Document
                  </>
                )}
              </button>
              {uploadStatus.message && (
                <div className={`upload-status ${uploadStatus.type}`}>
                  {uploadStatus.message}
                </div>
              )}
            </div>
          </div>
          <button 
            className="floating-upload-button"
            onClick={toggleUpload}
            title="Expand Upload Section"
          >
            📁
          </button>
          <button 
            className="floating-upload-button top"
            onClick={toggleUpload}
            title="Expand Upload Section"
          >
            📁
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
