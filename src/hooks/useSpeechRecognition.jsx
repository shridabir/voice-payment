import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Custom hook wrapping the Web Speech API's SpeechRecognition interface.
 *
 * The Web Speech API is built into Chrome and Edge. It provides:
 * - webkitSpeechRecognition: the constructor for a recognition session
 * - onresult: fires as the browser processes audio into text
 * - results[i].isFinal: whether the browser is confident in the transcript
 * - interimResults: when true, we get partial text while the user is still speaking
 *
 * Returns state (isListening, transcript, interimTranscript, error) and controls
 * (startListening, stopListening) so the UI can drive a mic button.
 */
export default function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);

  const recognitionRef = useRef(null);

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
    }
  }, []);

  const startListening = useCallback(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    // Clear previous state
    setError(null);
    setTranscript('');
    setInterimTranscript('');

    const recognition = new SpeechRecognition();

    // --- Configuration ---
    // continuous: false means recognition stops after detecting a pause.
    // This is ideal for command-style input (single utterances).
    recognition.continuous = false;

    // interimResults: true gives us partial transcripts in real time,
    // so the user sees text appearing as they speak.
    recognition.interimResults = true;

    // lang: the BCP-47 language tag for recognition.
    recognition.lang = 'en-US';

    // --- Event handlers ---

    // onresult fires each time the recognizer produces new text.
    // event.results is a SpeechRecognitionResultList.
    // Each result has .isFinal (boolean) and .[0].transcript (string).
    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        setTranscript(final.trim());
        setInterimTranscript('');
      } else {
        setInterimTranscript(interim);
      }
    };

    // onerror handles microphone permission denials and other failures.
    recognition.onerror = (event) => {
      let message;
      switch (event.error) {
        case 'not-allowed':
          message = 'Microphone access denied. Please allow microphone permissions in your browser settings.';
          break;
        case 'no-speech':
          message = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          message = 'No microphone found. Please check your audio input device.';
          break;
        case 'network':
          message = 'Network error during speech recognition. Please check your connection.';
          break;
        default:
          message = `Speech recognition error: ${event.error}`;
      }
      setError(message);
      setIsListening(false);
    };

    // onend fires when recognition stops (either naturally or due to error).
    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
  };
}
