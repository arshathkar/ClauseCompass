const API_BASE = '/v1';

export interface DocumentSubmitResponse {
  documentId: string;
  pii: any[];
}

export const api = {
  async createSession() {
    const res = await fetch(`${API_BASE}/session`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },
  async getStatus() {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },
  async submitDocument(sessionId: string, text: string, type: string, role: string) {
    const res = await fetch(`${API_BASE}/document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId
      },
      body: JSON.stringify({ text, type, role })
    });
    if (!res.ok) throw new Error('Failed to submit document');
    return res.json() as Promise<DocumentSubmitResponse>;
  },
  async updateRedactions(sessionId: string, documentId: string, customTerms: string[], disabledPii: string[]) {
    const res = await fetch(`${API_BASE}/document/${documentId}/redactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId
      },
      body: JSON.stringify({ customTerms, disabledPii })
    });
    if (!res.ok) throw new Error('Failed to update redactions');
    return res.json();
  },
  async deleteSession(sessionId: string) {
    const res = await fetch(`${API_BASE}/session`, {
      method: 'DELETE',
      headers: { 'X-Session-Id': sessionId }
    });
    if (!res.ok) throw new Error('Failed to delete session');
  }
};
