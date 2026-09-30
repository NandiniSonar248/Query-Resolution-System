import { useState, useEffect, useCallback } from 'react';

export default function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        setIsSupported(true);
        const recog = new SpeechRecognition();
        recog.continuous = false;
        recog.interimResults = true;
        recog.lang = 'en-US';

        recog.onresult = (event) => {
          let currentTranscript = '';
          for (let i = 0; i < event.results.length; i++) {
            currentTranscript += event.results[i][0].transcript;
          }
          setTranscript(currentTranscript);
        };

        recog.onstart = () => setIsListening(true);
        recog.onend = () => setIsListening(false);
        recog.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'not-allowed') {
            alert('Microphone access was denied. Please allow microphone access in your browser settings.');
          } else if (event.error !== 'no-speech') {
            alert('Speech recognition error: ' + event.error);
          }
          setIsListening(false);
        };

        setRecognition(recog);
      }
    }
  }, []);

  const start = useCallback(() => {
    if (recognition) {
      try {
        recognition.start();
      } catch (err) {
        console.error('Failed to start recognition', err);
      }
    }
  }, [recognition]);

  const stop = useCallback(() => {
    if (recognition) {
      recognition.stop();
    }
  }, [recognition]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return { start, stop, transcript, isListening, isSupported, resetTranscript };
}
