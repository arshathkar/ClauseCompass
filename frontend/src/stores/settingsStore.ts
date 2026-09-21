import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type Theme = 'system' | 'light' | 'dark' | 'high-contrast';
type ReadingLevel = 'simple' | 'standard' | 'detailed';
type Language = 'en' | 'hi' | 'ta';
type LineSpacing = 1.5 | 1.8 | 2.0;

interface SettingsState {
  theme: Theme;
  fontSize: number; // 100 to 200
  lineSpacing: LineSpacing;
  letterSpacing: boolean;
  dyslexiaFont: boolean;
  reducedMotion: boolean;
  readingLevel: ReadingLevel;
  outputLanguage: Language;
  
  updateSettings: (settings: Partial<Omit<SettingsState, 'updateSettings'>>) => void;
}

// Fallback memory storage if localStorage is denied
const memoryStorage: any = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {}
};

const getStorage = () => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      // Test it
      window.localStorage.setItem('__test__', '1');
      window.localStorage.removeItem('__test__');
      return window.localStorage;
    }
  } catch (e) {
    // Ignore error, fallback to memory
  }
  return memoryStorage;
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'system',
      fontSize: 100,
      lineSpacing: 1.5,
      letterSpacing: false,
      dyslexiaFont: false,
      reducedMotion: false,
      readingLevel: 'simple',
      outputLanguage: 'en',
      updateSettings: (settings) => set((state) => ({ ...state, ...settings })),
    }),
    {
      name: 'clausecompass-settings',
      storage: createJSONStorage(getStorage),
    }
  )
);
