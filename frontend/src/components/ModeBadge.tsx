import { useSessionStore } from '../stores/sessionStore';

export function ModeBadge() {
  const { mode } = useSessionStore();

  if (mode === 'replay' || mode === 'fake') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 border border-purple-200">
        <span aria-hidden="true">▶</span> Demo (saved results)
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-200">
      <span aria-hidden="true">⚡</span> Live AI
    </span>
  );
}
