import { useState, useEffect, useCallback } from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import useSpeechSynthesis from '../hooks/useSpeechSynthesis';
import ConversationView from './ConversationView';

// ---- Mock response logic (temporary) ----
function getMockResponse(userText) {
  const lowerText = userText.toLowerCase();

  if (lowerText.includes('send') || lowerText.includes('pay')) {
    return "I heard you want to send money. Who would you like to send money to?";
  } else if (lowerText.includes('hello') || lowerText.includes('hi')) {
    return "Hi! I'm your payment assistant. Say something like 'Send Mike 20 dollars for pizza'";
  } else if (lowerText.includes('help')) {
    return "Tell me who to pay and how much. For example: 'Send Sarah 15 dollars for lunch'";
  } else {
    return "I'm listening. Try saying 'Send money to Mike' or ask for help.";
  }
}

let messageIdCounter = 0;

/**
 * Top-level component that wires voice I/O to a chat conversation.
 *
 * Flow:
 * 1. User taps mic (or types text) to send a message.
 * 2. The user message is appended to conversation history.
 * 3. A mock response is generated after a short delay (simulates processing).
 * 4. The response is spoken aloud via SpeechSynthesis and shown in chat.
 */
export default function VoiceInterface() {
  const [messages, setMessages] = useState([]);
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const {
    isListening,
    transcript,
    interimTranscript,
    error: recognitionError,
    isSupported: recognitionSupported,
    startListening,
    stopListening,
  } = useSpeechRecognition();

  const {
    isSpeaking,
    isSupported: synthesisSupported,
    speak,
    stop: stopSpeaking,
  } = useSpeechSynthesis();

  // Process a completed user message (from voice or text)
  const handleUserMessage = useCallback(
    (text) => {
      if (!text.trim()) return;

      const userMsg = { id: ++messageIdCounter, role: 'user', text: text.trim() };
      setMessages((prev) => [...prev, userMsg]);
      setIsProcessing(true);

      // Simulate a short processing delay before the assistant responds
      setTimeout(() => {
        const responseText = getMockResponse(text);
        const assistantMsg = { id: ++messageIdCounter, role: 'assistant', text: responseText };
        setMessages((prev) => [...prev, assistantMsg]);
        setIsProcessing(false);
        speak(responseText);
      }, 800);
    },
    [speak]
  );

  // When speech recognition produces a final transcript, send it as a message
  useEffect(() => {
    if (transcript) {
      handleUserMessage(transcript);
    }
  }, [transcript, handleUserMessage]);

  // Handle text input submission
  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;
    handleUserMessage(textInput);
    setTextInput('');
  };

  // Toggle the microphone on/off
  const handleMicClick = () => {
    if (isSpeaking) {
      stopSpeaking();
    }
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Determine mic button state for styling
  const micState = isListening ? 'listening' : isProcessing ? 'processing' : 'idle';

  // Browser compatibility warning
  if (!recognitionSupported) {
    return (
      <div className="browser-warning">
        <h2>Browser Not Supported</h2>
        <p>
          Speech recognition requires <strong>Google Chrome</strong> or{' '}
          <strong>Microsoft Edge</strong>. Please open this app in one of those browsers.
        </p>
      </div>
    );
  }

  return (
    <div className="voice-interface">
      <header className="voice-header">
        <h1>Payment Assistant</h1>
        {isSpeaking && (
          <div className="speaking-indicator" title="Assistant is speaking">
            <span className="speaking-dot"></span>
            Speaking...
          </div>
        )}
      </header>

      <ConversationView
        messages={messages}
        isProcessing={isProcessing}
        interimTranscript={isListening ? interimTranscript : ''}
      />

      {/* Microphone button */}
      <div className="mic-section">
        {recognitionError && <p className="mic-error">{recognitionError}</p>}
        <button
          className={`mic-button mic-button--${micState}`}
          onClick={handleMicClick}
          aria-label={isListening ? 'Stop listening' : 'Start listening'}
        >
          {isListening ? '🔴 Listening...' : '🎤 Tap to Speak'}
        </button>
      </div>

      {/* Text input fallback */}
      <form className="text-input-form" onSubmit={handleTextSubmit}>
        <input
          type="text"
          className="text-input"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Type a message..."
          disabled={isProcessing}
        />
        <button type="submit" className="send-button" disabled={isProcessing || !textInput.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
