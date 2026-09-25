import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { WelcomePage } from './features/welcome/WelcomePage';
import { UploadPage } from './features/upload/UploadPage';
import { RedactionPage } from './features/redaction/RedactionPage';
import { ResultsPage } from './features/results/ResultsPage';
import { useDocumentStore } from './stores/documentStore';
import { useSettingsStore } from './stores/settingsStore';
import { useSessionStore } from './stores/sessionStore';
import { SkipLink, StatusRegion, announce, ModeBadge } from './components';
import { SettingsPanel } from './features/settings/SettingsPanel';
import { api } from './lib/api';
import { useSSE } from './lib/sse';

export default function App() {
  const { setDocument } = useDocumentStore();
  const { sessionId, docId, initSession, setDocId } = useSessionStore();
  const { i18n } = useTranslation();
  const outputLanguage = useSettingsStore(state => state.outputLanguage);
  
  const [redactionItems, setRedactionItems] = useState<any[]>([]);
  const { startStream, events } = useSSE();
  
  // Keep i18n in sync with settings
  useEffect(() => {
    if (i18n.language !== outputLanguage) {
      i18n.changeLanguage(outputLanguage);
    }
  }, [outputLanguage, i18n]);

  // Create session on mount
  useEffect(() => {
    const setupSession = async () => {
      try {
        if (!sessionId) {
          const res = await api.createSession();
          initSession(res.session_id, 'live');
        }
      } catch (err) {
        console.error('Failed to create session', err);
      }
    };
    setupSession();
  }, [sessionId, initSession]);

  // Simple state machine for routing
  const [currentStep, setCurrentStep] = useState<'welcome' | 'upload' | 'redaction' | 'results'>('welcome');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleUploadContinue = async (text: string, type: string, role: string, fileName: string) => {
    try {
      if (!sessionId) throw new Error('No session');
      
      const res = await api.submitDocument(sessionId, text);
      setDocId(res.doc_id);
      
      // Convert API redactions to UI format
      const uiRedactions = res.redactions.map((r: any) => ({
        id: r.id || Date.now().toString() + Math.random(),
        type: r.type,
        found: r.found,
        placeholder: r.placeholder,
        hidden: r.is_active !== false // default true
      }));
      setRedactionItems(uiRedactions);
      
      setDocument({ type: res.doc_type, role, text, fileName, findings: [], keyFacts: [] });
      announce('Read 1 page.');
      setCurrentStep('redaction');
      announce(`We found ${uiRedactions.length} personal details and hid them. Review before continuing.`);
    } catch (err) {
      console.error('Upload failed', err);
      // Fallback for demo
      setDocument({ type, role, text, fileName, findings: [], keyFacts: [] });
      setRedactionItems([]);
      setCurrentStep('redaction');
    }
  };

  const handleRedactionContinue = async (items: any[]) => {
    setCurrentStep('results');
    announce('Analysis started.');
    
    try {
      if (!sessionId || !docId) throw new Error('No session or doc');
      
      const activeIds = items.filter(i => i.hidden).map(i => i.id).filter(Boolean);
      await api.updateRedactions(sessionId, docId, [], activeIds);
      
      // Start analysis SSE
      const role = useDocumentStore.getState().document?.role || 'User';
      startStream(api.analyzeURL(docId), { user_role: role }, { 'X-Session-Id': sessionId });
    } catch (err) {
      console.error('Analysis failed', err);
    }
  };
  
  // Process analysis SSE events
  useEffect(() => {
    if (events.length === 0) return;
    const lastEvent = events[events.length - 1];
    
    if (lastEvent.event === 'key_facts') {
      const data = lastEvent.data;
      setDocument({ 
        keyFacts: data.facts || [], 
        summary: data.summary_standard || data.summary_simple || ''
      });
    } else if (lastEvent.event === 'finding') {
      // Use finding.clause_id, severity, etc. Needs mapping to UI format
      const f = lastEvent.data;
      useDocumentStore.getState().updateFinding({
        id: f.id || Math.random().toString(),
        clauseId: f.citation?.clause_id || 'N/A',
        severity: f.severity,
        category: f.category || 'General',
        whatItSays: f.plain_summary || 'No summary',
        whatItMeans: f.what_it_means || '',
        whyItMatters: f.why_it_matters || '',
        questionToAsk: f.suggested_question,
        needsReview: false
      });
    }
  }, [events]);

  const handleDelete = () => {
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    try {
      if (sessionId) {
        await api.deleteSession(sessionId);
      }
    } catch (e) {
      // ignore
    }
    localStorage.removeItem('clausecompass-session');
    localStorage.removeItem('clausecompass-document');
    window.location.reload();
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'welcome':
        return <WelcomePage onContinue={() => setCurrentStep('upload')} />;
      case 'upload':
        return <UploadPage onContinue={handleUploadContinue} />;
      case 'redaction':
        return <RedactionPage 
                 onContinue={() => handleRedactionContinue(redactionItems)} 
                 onBack={() => setCurrentStep('upload')} 
                 initialItems={redactionItems}
               />;
      case 'results':
        return <ResultsPage />;
      default:
        return <WelcomePage onContinue={() => setCurrentStep('upload')} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50/30 font-sans text-gray-900 bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <SkipLink />
      <StatusRegion />
      
      {/* Universal Header */}
      <header className="sticky top-0 backdrop-blur-md bg-white/70 border-b border-gray-200/50 px-6 py-4 flex items-center justify-between shadow-sm z-30 shrink-0">
        <div className="flex items-center gap-4 cursor-pointer" onClick={() => setCurrentStep('welcome')}>
          <div className="bg-gradient-to-r from-brand to-cyan-500 text-transparent bg-clip-text font-black text-2xl tracking-tight">ClauseCompass</div>
          <ModeBadge />
        </div>
        <div className="flex gap-5 text-sm font-semibold items-center">
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="text-gray-600 hover:text-brand focus:outline-none focus:ring-2 focus:ring-brand rounded-lg px-2 py-1 transition-colors"
          >
            Settings
          </button>
          
          {showDeleteConfirm ? (
            <div className="flex items-center gap-2 bg-red-50 px-3 py-1.5 rounded-full border border-red-200 shadow-sm animate-in fade-in zoom-in duration-200">
              <span className="text-red-700 text-xs font-bold mr-1">Sure?</span>
              <button onClick={confirmDelete} className="bg-red-600 text-white text-xs px-2 py-1 rounded hover:bg-red-700 transition-colors">Yes</button>
              <button onClick={() => setShowDeleteConfirm(false)} className="bg-white text-gray-600 text-xs border border-gray-300 px-2 py-1 rounded hover:bg-gray-100 transition-colors">Cancel</button>
            </div>
          ) : (
            <button 
              onClick={handleDelete}
              className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 rounded-lg px-2 py-1 transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </header>

      <main id="main-content" className="flex-1 flex flex-col overflow-hidden relative">
        {renderCurrentStep()}
      </main>

      <SettingsPanel isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}
