import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

/**
 * Scrollable conversation area that renders all messages and an optional
 * typing indicator. Auto-scrolls to the bottom whenever content changes.
 */
export default function ConversationView({ messages, isProcessing, interimTranscript }) {
  const bottomRef = useRef(null);

  // Scroll to bottom whenever messages change or interim text updates
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing, interimTranscript]);

  return (
    <div className="conversation-view">
      {messages.length === 0 && (
        <div className="conversation-empty">
          <p>Say &quot;Hello&quot; or &quot;Send Mike 20 dollars&quot; to get started.</p>
        </div>
      )}

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {/* Show what the user is currently saying (interim speech results) */}
      {interimTranscript && (
        <div className="message-row message-row--user">
          <div className="message-bubble message-bubble--user message-bubble--interim">
            <p className="message-text">{interimTranscript}</p>
          </div>
        </div>
      )}

      {/* Typing indicator while "processing" the mock response */}
      {isProcessing && (
        <div className="message-row message-row--assistant">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
