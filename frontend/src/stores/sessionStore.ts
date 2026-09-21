import { create } from 'zustand';

interface SessionState {
  sessionId: string | null;
  mode: 'live' | 'replay' | 'fake';
  capacity: 'ok' | 'low';
  freeTier: boolean;
  initSession: (id: string, mode: 'live' | 'replay' | 'fake') => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  mode: 'live',
  capacity: 'ok',
  freeTier: true,
  initSession: (id, mode) => set({ sessionId: id, mode }),
  clearSession: () => set({ sessionId: null, mode: 'live' })
}));
