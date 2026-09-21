
interface CitationChipProps {
  clauseId: string;
  quote?: string;
  onClick: (clauseId: string) => void;
}

export function CitationChip({ clauseId, quote, onClick }: CitationChipProps) {
  return (
    <button
      onClick={() => onClick(clauseId)}
      className="inline-flex items-center text-xs font-mono bg-blue-50 text-brand border border-blue-200 rounded px-1.5 py-0.5 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-focus mx-1"
      aria-label={`Clause ${clauseId}, opens source text`}
      title={quote || `Go to clause ${clauseId}`}
    >
      §{clauseId}
    </button>
  );
}
