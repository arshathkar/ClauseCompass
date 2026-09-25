const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

export interface DocumentSubmitResponse {
  doc_id: string;
  doc_type: string;
  confidence: number;
  redactions: Array<{
    id?: string;
    type: string;
    found: string;
    placeholder: string;
    is_active?: boolean;
  }>;
}

export interface SessionResponse {
  session_id: string;
}

export const api = {
  /** Create a new analysis session on the backend */
  async createSession(): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/v1/sessions`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  /** Submit document text for PII detection and AI-powered classification */
  async submitDocument(sessionId: string, text: string): Promise<DocumentSubmitResponse> {
    const res = await fetch(`${API_BASE}/v1/documents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId
      },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error('Failed to submit document');
    return res.json();
  },

  /** Update PII masking preferences before AI analysis */
  async updateRedactions(
    sessionId: string,
    docId: string,
    customTerms: string[],
    activeIds: string[]
  ): Promise<{ status: string; redactions: any[] }> {
    const res = await fetch(`${API_BASE}/v1/documents/${docId}/redactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId
      },
      body: JSON.stringify({ custom_terms: customTerms, active_ids: activeIds })
    });
    if (!res.ok) throw new Error('Failed to update redactions');
    return res.json();
  },

  /** Get the SSE URL for AI-powered document analysis */
  analyzeURL(docId: string): string {
    return `${API_BASE}/v1/documents/${docId}/analyze`;
  },

  /** Get the SSE URL for AI-powered Q&A */
  qaURL(docId: string): string {
    return `${API_BASE}/v1/documents/${docId}/qa`;
  },

  /** Delete a specific document from the session */
  async deleteDocument(sessionId: string, docId: string): Promise<void> {
    await fetch(`${API_BASE}/v1/documents/${docId}`, {
      method: 'DELETE',
      headers: { 'X-Session-Id': sessionId }
    });
  },

  /** Delete the entire session and all associated data */
  async deleteSession(sessionId: string): Promise<void> {
    await fetch(`${API_BASE}/v1/sessions/current`, {
      method: 'DELETE',
      headers: { 'X-Session-Id': sessionId }
    });
  }
};
