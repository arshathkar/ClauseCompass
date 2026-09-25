import { create } from 'zustand';

interface SessionState {
  sessionId: string | null;
  docId: string | null;
  mode: 'live' | 'replay' | 'fake';
  capacity: 'ok' | 'low';
  freeTier: boolean;
  initSession: (id: string, mode: 'live' | 'replay' | 'fake') => void;
  setDocId: (id: string) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  docId: null,
  mode: 'live',
  capacity: 'ok',
  freeTier: true,
  initSession: (id, mode) => set({ sessionId: id, mode }),
  setDocId: (id) => set({ docId: id }),
  clearSession: () => set({ sessionId: null, docId: null, mode: 'live' })
}));
