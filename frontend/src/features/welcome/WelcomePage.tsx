import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSettingsStore } from '../../stores/settingsStore';
import { useSessionStore } from '../../stores/sessionStore';

interface WelcomePageProps {
  onContinue: () => void;
}

export function WelcomePage({ onContinue }: WelcomePageProps) {
  const { t } = useTranslation();
  const { outputLanguage, updateSettings } = useSettingsStore();
  const { initSession } = useSessionStore();
  const [understood, setUnderstood] = useState(false);

  const handleSample = () => {
    initSession('demo-session', 'replay');
    onContinue(); // Or maybe we just skip to results directly, but standard flow is continue
  };

  const handleStart = () => {
    if (understood) {
      initSession('live-session-' + Date.now(), 'live');
      onContinue();
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-2xl mx-auto space-y-10 w-full animate-in fade-in duration-500">
      <div className="text-center space-y-5">
        <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 tracking-tight drop-shadow-sm pb-2">ClauseCompass</h1>
        <p className="text-xl text-gray-700 font-medium leading-relaxed max-w-lg mx-auto">
          {t('welcome.scope')}
        </p>
      </div>

      <div className="w-full space-y-6 bg-white/60 backdrop-blur-xl border border-white/50 p-8 rounded-3xl shadow-xl shadow-indigo-100/50">
        <div className="flex flex-col space-y-2">
          <label htmlFor="lang-select" className="text-sm font-bold text-gray-700 uppercase tracking-wider">Language / भाषा / மொழி</label>
          <select 
            id="lang-select"
            value={outputLanguage} 
            onChange={(e) => updateSettings({ outputLanguage: e.target.value as 'en' | 'hi' | 'ta' })}
            className="block w-full rounded-2xl bg-white/50 backdrop-blur-md border-white/50 shadow-sm focus:border-brand focus:ring-brand focus:bg-white text-gray-900 font-medium text-base p-3 transition-all cursor-pointer"
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
          </select>
        </div>

        <div className="bg-blue-50/70 border border-blue-200/50 p-5 rounded-2xl text-left flex gap-4 items-start backdrop-blur-sm">
          <span aria-hidden="true" className="text-blue-500 text-2xl drop-shadow-sm">ℹ</span>
          <div className="space-y-3">
            <h2 className="font-extrabold text-blue-900 text-sm uppercase tracking-widest">{t('welcome.freeNotice').split('.')[0]}</h2>
            <p className="text-sm text-blue-800/90 font-medium">{t('welcome.freeNotice').split('.').slice(1).join('.')}</p>
            <label className="flex items-center gap-3 cursor-pointer mt-3 group">
              <input 
                type="checkbox" 
                checked={understood} 
                onChange={(e) => setUnderstood(e.target.checked)}
                className="w-5 h-5 text-indigo-600 bg-white/50 border-gray-300 rounded-md focus:ring-indigo-500 transition-colors"
              />
              <span className="text-sm font-bold text-blue-900 group-hover:text-indigo-700 transition-colors">{t('welcome.understand')}</span>
            </label>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row w-full gap-4 pt-2">
          <button 
            onClick={handleStart}
            disabled={!understood}
            className="flex-1 bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-bold text-lg py-4 px-6 rounded-2xl hover:from-indigo-700 hover:to-blue-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30"
          >
            {t('welcome.continue')}
          </button>
          <button 
            onClick={handleSample}
            className="flex-1 bg-white/80 backdrop-blur-sm text-gray-800 border border-gray-200 font-bold text-lg py-4 px-6 rounded-2xl hover:bg-white focus:outline-none focus:ring-4 focus:ring-indigo-500/20 transition-all shadow-sm"
          >
            {t('welcome.trySample')}
          </button>
        </div>
      </div>
    </div>
  );
}
