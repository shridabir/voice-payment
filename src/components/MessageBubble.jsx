/**
 * A single chat bubble. User messages are blue and right-aligned;
 * assistant messages are gray and left-aligned.
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'message-row--user' : 'message-row--assistant'}`}>
      <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--assistant'}`}>
        <p className="message-text">{message.text}</p>
      </div>
    </div>
  );
}
