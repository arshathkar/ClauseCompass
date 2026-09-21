import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './styles/tokens.css';
import './styles/globals.css';
import './i18n';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// Initialize settings from localStorage before render to avoid flash
try {
  const settingsStr = localStorage.getItem('clausecompass-settings');
  if (settingsStr) {
    const settings = JSON.parse(settingsStr).state;
    if (settings.theme && settings.theme !== 'system') {
      document.documentElement.setAttribute('data-theme', settings.theme);
    }
    if (settings.dyslexiaFont) {
      document.documentElement.setAttribute('data-dyslexia', 'true');
    }
    if (settings.reducedMotion) {
      document.documentElement.setAttribute('data-reduced-motion', 'true');
    }
  }
} catch {
  // Ignore localStorage errors
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);
