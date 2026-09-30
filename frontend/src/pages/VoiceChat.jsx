import { useState, useRef, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import useAudioRecorder from '../hooks/useAudioRecorder';
import { voiceApi, queryApi } from '../api';
import toast from 'react-hot-toast';

export default function VoiceChat() {
  const { isRecording, startRecording, stopRecording } = useAudioRecorder();
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const audioPlayerRef = useRef(null);

  useEffect(() => {
    // Add initial greeting
    setMessages([
      { role: 'assistant', text: 'Hello! Press the microphone button and ask me a question.' }
    ]);
  }, []);

  const handleMicClick = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      processAudioInput(audioBlob);
    } else {
      try {
        await startRecording();
      } catch (err) {
        toast.error("Could not access microphone.");
      }
    }
  };

  const processAudioInput = async (audioBlob) => {
    if (!audioBlob) return;
    setIsProcessing(true);
    let toastId = toast.loading('Transcribing your voice...');
    
    try {
      // 1. Transcribe STT
      const transcribeRes = await voiceApi.transcribe(audioBlob);
      const userText = transcribeRes.data.text;
      
      if (!userText || !userText.trim()) {
        toast.error('No speech detected. Please try again.', { id: toastId });
        setIsProcessing(false);
        return;
      }
      
      toast.loading('Analyzing query...', { id: toastId });
      setMessages(prev => [...prev, { role: 'user', text: userText }]);

      // 2. Get LLM response
      const queryRes = await queryApi.ask({ query: userText, session_id: null });
      const aiText = queryRes.data.answer;
      
      setMessages(prev => [...prev, { role: 'assistant', text: aiText }]);
      
      // 3. Synthesize TTS
      toast.loading('Generating voice response...', { id: toastId });
      const synthRes = await voiceApi.synthesize(aiText);
      const audioUrl = URL.createObjectURL(synthRes.data);
      
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = audioUrl;
        audioPlayerRef.current.play().catch(err => {
          console.warn('Autoplay blocked:', err);
          toast.error('Autoplay blocked by browser. Click play on the audio player.', { id: toastId });
        });
      }
      
      toast.success('Done!', { id: toastId });
    } catch (error) {
      console.error(error);
      const errMsg = error.response?.data?.detail || 'Voice interaction failed.';
      toast.error(errMsg, { id: toastId });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <AppLayout>
      <div className="page-content animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100%', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
        <header style={{ marginBottom: 'var(--space-8)', textAlign: 'center' }}>
          <h1 style={{ margin: 0, fontSize: '2.5rem' }}>Hands-free Voice Chat</h1>
          <p style={{ marginTop: 'var(--space-2)', color: 'var(--color-text-muted)' }}>
            Speak naturally. The system will transcribe, think, and reply with voice.
          </p>
        </header>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 'var(--space-4)' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.role === 'user' ? 'var(--color-primary)' : 'var(--color-bg-elevated)',
              color: msg.role === 'user' ? 'white' : 'var(--color-text-primary)',
              padding: 'var(--space-4)',
              borderRadius: 'var(--radius-lg)',
              maxWidth: '80%',
              boxShadow: 'var(--shadow-sm)',
              fontSize: '1.1rem',
              lineHeight: '1.5'
            }}>
              {msg.text}
            </div>
          ))}
          {isProcessing && (
            <div style={{ alignSelf: 'center', color: 'var(--color-primary)', marginTop: 'var(--space-4)' }}>
              <span className="spinner" style={{ marginRight: '8px' }} /> Processing your request...
            </div>
          )}
        </div>

        <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', justifyContent: 'center', alignItems: 'center' }}>
          <button
            onClick={handleMicClick}
            disabled={isProcessing}
            style={{
              width: '80px', height: '80px',
              borderRadius: '50%',
              backgroundColor: isRecording ? 'var(--color-danger)' : 'var(--color-primary)',
              color: 'white',
              border: 'none',
              boxShadow: isRecording ? '0 0 20px var(--color-danger)' : 'var(--shadow-lg)',
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              display: 'flex', justifyContent: 'center', alignItems: 'center',
              fontSize: '2rem',
              transition: 'all 0.3s ease',
              animation: isRecording ? 'pulse 1.5s infinite' : 'none'
            }}
          >
            {isRecording ? '⏹' : '🎤'}
          </button>
          <audio ref={audioPlayerRef} controls style={{ opacity: isProcessing ? 0.5 : 1 }} />
        </div>
      </div>
    </AppLayout>
  );
}
