import { useState, useEffect } from 'react';
import { useSettingsStore } from '../stores/settingsStore';

interface ReadAloudButtonProps {
  text: string;
}

export function ReadAloudButton({ text }: ReadAloudButtonProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [supported, setSupported] = useState(true);
  const { outputLanguage } = useSettingsStore();

  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      setSupported(false);
    }
    
    return () => {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isSpeaking]);

  const toggleSpeech = () => {
    if (!supported) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set language hint
      if (outputLanguage === 'hi') utterance.lang = 'hi-IN';
      else if (outputLanguage === 'ta') utterance.lang = 'ta-IN';
      else utterance.lang = 'en-IN'; // Default to Indian English if available
      
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  if (!supported) return null;

  return (
    <button
      onClick={toggleSpeech}
      aria-pressed={isSpeaking}
      className="inline-flex items-center justify-center p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-focus"
      title={isSpeaking ? "Stop reading" : "Read aloud"}
      aria-label={isSpeaking ? "Stop reading" : "Read aloud"}
    >
      <span aria-hidden="true" className="text-lg">
        {isSpeaking ? '⏹' : '🔊'}
      </span>
    </button>
  );
}
