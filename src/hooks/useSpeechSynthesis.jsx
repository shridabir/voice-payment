import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Custom hook wrapping the Web Speech API's SpeechSynthesis interface.
 *
 * SpeechSynthesis is the browser's text-to-speech engine:
 * - window.speechSynthesis: the global synth controller
 * - SpeechSynthesisUtterance: a "thing to say" with voice/rate/pitch settings
 * - speechSynthesis.speak(utterance): queues the utterance for playback
 * - speechSynthesis.cancel(): stops all queued speech immediately
 *
 * Voice selection: voices load asynchronously in some browsers, so we listen
 * for the `voiceschanged` event and pick a good default English voice.
 */
export default function useSpeechSynthesis() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const voiceRef = useRef(null);

  useEffect(() => {
    if (!window.speechSynthesis) {
      setIsSupported(false);
      return;
    }

    // Voices may not be available immediately in some browsers.
    // The `voiceschanged` event fires when the list is ready.
    const pickVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      // Prefer a natural-sounding English voice. Common high-quality voices
      // include "Google US English", "Samantha", or any voice whose name
      // suggests it's not a robotic fallback.
      const preferred = voices.find(
        (v) =>
          v.lang.startsWith('en') &&
          (v.name.includes('Google') ||
            v.name.includes('Samantha') ||
            v.name.includes('Natural'))
      );
      voiceRef.current = preferred || voices.find((v) => v.lang.startsWith('en')) || voices[0];
    };

    pickVoice();
    window.speechSynthesis.addEventListener('voiceschanged', pickVoice);
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', pickVoice);
    };
  }, []);

  const speak = useCallback((text) => {
    if (!window.speechSynthesis) return;

    // Cancel any in-progress speech before starting new output
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // --- Configuration ---
    // rate: speaking speed. 0.9 is slightly slower than normal for clarity.
    utterance.rate = 0.9;
    // pitch: voice pitch. 1.0 is the default natural pitch.
    utterance.pitch = 1.0;
    // volume: 0.0 (silent) to 1.0 (loudest).
    utterance.volume = 1.0;

    if (voiceRef.current) {
      utterance.voice = voiceRef.current;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  const stop = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  return { isSpeaking, isSupported, speak, stop };
}
