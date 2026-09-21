import { create } from 'zustand';

interface Clause {
  id: string;
  text: string;
  page: number;
}

interface Finding {
  id: string;
  clauseId: string;
  severity: 'High' | 'Medium' | 'Low' | 'Info';
  category: string;
  whatItSays: string;
  whatItMeans: string;
  whyItMatters: string;
  questionToAsk?: string;
  needsReview?: boolean;
}

interface Fact {
  label: string;
  value: string;
  sourceId: string;
}

interface DocumentData {
  id: string;
  type: string;
  role: string;
  fileName?: string;
  text?: string;
  clauses: Clause[];
  findings: Finding[];
  keyFacts: Fact[];
  obligations: { party: string; obligations: Fact[] }[];
  summary: string;
  redactionReport: {
    type: string;
    found: string;
    placeholder: string;
    hidden: boolean;
  }[];
  urgency?: {
    deadline?: string;
    reason: string;
    resources: { name: string; url: string }[];
  };
}

interface DocumentState {
  document: DocumentData | null;
  secondDocument: DocumentData | null;
  setDocument: (doc: Partial<DocumentData>) => void;
  updateFinding: (finding: Finding) => void;
  clear: () => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  document: null,
  secondDocument: null,
  setDocument: (doc) => set((state) => ({ 
    document: state.document ? { ...state.document, ...doc } : doc as DocumentData 
  })),
  updateFinding: (finding) => set((state) => {
    if (!state.document) return state;
    const existing = state.document.findings.findIndex(f => f.id === finding.id);
    const newFindings = [...state.document.findings];
    if (existing >= 0) {
      newFindings[existing] = finding;
    } else {
      newFindings.push(finding);
    }
    return { document: { ...state.document, findings: newFindings } };
  }),
  clear: () => set({ document: null, secondDocument: null })
}));
