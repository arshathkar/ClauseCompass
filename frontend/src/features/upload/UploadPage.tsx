import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileDrop } from '../../components';
import { useSessionStore } from '../../stores/sessionStore';
import { extractText } from '../../lib/extract';

interface UploadPageProps {
  onContinue: (text: string, type: string, role: string, fileName: string) => void;
}

const DOCUMENT_TYPES = [
  { id: 'rental', label: 'Rental Agreement', roles: ['Tenant', 'Landlord'] },
  { id: 'employment', label: 'Employment / Offer Letter', roles: ['Employee', 'Employer'] },
  { id: 'loan', label: 'Loan Agreement', roles: ['Borrower', 'Lender'] },
  { id: 'freelance', label: 'Freelance / Service', roles: ['Service Provider', 'Client'] },
  { id: 'nda', label: 'Non-Disclosure Agreement (NDA)', roles: ['Receiving Party', 'Disclosing Party'] },
  { id: 'insurance', label: 'Insurance Policy', roles: ['Policyholder', 'Insurer'] },
  { id: 'tos', label: 'Terms of Service / Privacy', roles: ['User', 'Company'] },
  { id: 'other', label: 'Other', roles: ['Party A', 'Party B'] }
];

export function UploadPage({ onContinue }: UploadPageProps) {
  const { t } = useTranslation();
  const { mode } = useSessionStore();
  
  const [docType, setDocType] = useState(DOCUMENT_TYPES[0].id);
  const [role, setRole] = useState(DOCUMENT_TYPES[0].roles[0]);
  const [pastedText, setPastedText] = useState('');
  
  const [isExtracting, setIsExtracting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const currentTypeRoles = DOCUMENT_TYPES.find(d => d.id === docType)?.roles || [];

  const handleDocTypeChange = (newType: string) => {
    setDocType(newType);
    const newRoles = DOCUMENT_TYPES.find(d => d.id === newType)?.roles || [];
    setRole(newRoles[0]);
  };

  const processFile = async (file: File) => {
    setIsExtracting(true);
    setProgress(0);
    setError(null);
    try {
      const { text } = await extractText(file, (current, total) => {
        setProgress(Math.round((current / total) * 100));
      });
      onContinue(text, docType, role, file.name);
    } catch (err: any) {
      setError(err.message || 'Failed to extract text. Try pasting it instead.');
    } finally {
      setIsExtracting(false);
    }
  };

  const handlePasteContinue = () => {
    if (!pastedText.trim()) {
      setError('Please paste some text first.');
      return;
    }
    onContinue(pastedText, docType, role, 'Pasted text');
  };

  const loadSample = (sampleId: string) => {
    // For demo/replay, we can just pass some dummy text to go to the next stage,
    // or trigger specific sample flow.
    onContinue(`[[SAMPLE:${sampleId}]]`, 'rental', 'Tenant', `${sampleId}_sample.pdf`);
  };

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-6 space-y-8 animate-in fade-in duration-500">
      <div className="text-center pt-4">
        <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 tracking-tight drop-shadow-sm pb-1 mb-2">Upload your document</h1>
        <p className="text-gray-600 font-medium">Select a document to understand its contents and risks.</p>
      </div>

      {error && (
        <div className="bg-red-50/80 backdrop-blur-sm border-l-4 border-red-500 p-4 mb-4 rounded-r-xl shadow-sm" role="alert">
          <p className="text-red-700 font-bold">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white/50 shadow-xl shadow-indigo-100/50">
        <div className="space-y-2">
          <label htmlFor="doc-type" className="block text-sm font-bold text-gray-700 uppercase tracking-wider">{t('upload.docType')}</label>
          <select 
            id="doc-type"
            value={docType}
            onChange={(e) => handleDocTypeChange(e.target.value)}
            className="block w-full rounded-2xl bg-white/60 backdrop-blur-md border-white/50 shadow-sm focus:border-brand focus:ring-brand focus:bg-white text-gray-900 font-medium p-3 transition-all cursor-pointer"
          >
            {DOCUMENT_TYPES.map(d => <option key={d.id} value={d.id}>{d.label}</option>)}
          </select>
        </div>
        <div className="space-y-2">
          <label htmlFor="user-role" className="block text-sm font-bold text-gray-700 uppercase tracking-wider">{t('upload.role')}</label>
          <select 
            id="user-role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="block w-full rounded-2xl bg-white/60 backdrop-blur-md border-white/50 shadow-sm focus:border-brand focus:ring-brand focus:bg-white text-gray-900 font-medium p-3 transition-all cursor-pointer"
          >
            {currentTypeRoles.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      <div className="bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white/50 shadow-xl shadow-indigo-100/50 space-y-6">
        <FileDrop onFileSelect={processFile} isProcessing={isExtracting} progress={progress} />

        <div className="relative py-4">
          <div className="absolute inset-0 flex items-center" aria-hidden="true">
            <div className="w-full border-t border-gray-300/50"></div>
          </div>
          <div className="relative flex justify-center">
            <span className="px-4 bg-[#f8fafc] text-sm text-gray-500 uppercase font-bold tracking-widest rounded-full shadow-sm">Or</span>
          </div>
        </div>

        <div className="space-y-3">
          <label htmlFor="paste-text" className="block text-sm font-bold text-gray-700 uppercase tracking-wider">
            {t('upload.paste')}
          </label>
          <textarea
            id="paste-text"
            rows={5}
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            className="w-full block rounded-2xl bg-white/70 backdrop-blur-md border-white/50 shadow-inner p-4 focus:ring-brand focus:border-brand text-gray-900 font-medium placeholder-gray-400 transition-all"
            placeholder="Paste your legal text here..."
          />
          <div className="flex justify-end pt-2">
            <button 
              onClick={handlePasteContinue}
              disabled={isExtracting || !pastedText.trim()}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-bold py-3 px-8 rounded-xl hover:from-indigo-700 hover:to-blue-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30"
            >
              {t('upload.continue')}
            </button>
          </div>
        </div>
      </div>

      {mode === 'replay' && (
        <div className="pt-8 space-y-4">
          <h2 className="text-xl font-black text-gray-900 drop-shadow-sm">Try a sample</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <button onClick={() => loadSample('rental')} className="p-5 bg-white/70 backdrop-blur-md border border-white/80 rounded-3xl text-left hover:bg-white hover:scale-105 hover:shadow-xl transition-all focus:ring-4 focus:ring-indigo-500/30 outline-none shadow-md shadow-indigo-100/30 group">
              <h3 className="font-bold text-base text-gray-900 group-hover:text-indigo-600 transition-colors">Rental Agreement</h3>
              <p className="text-sm text-gray-600 mt-2 font-medium">Leave and licence with notice period</p>
            </button>
            <button onClick={() => loadSample('offer')} className="p-5 bg-white/70 backdrop-blur-md border border-white/80 rounded-3xl text-left hover:bg-white hover:scale-105 hover:shadow-xl transition-all focus:ring-4 focus:ring-indigo-500/30 outline-none shadow-md shadow-indigo-100/30 group">
              <h3 className="font-bold text-base text-gray-900 group-hover:text-indigo-600 transition-colors">Offer Letter</h3>
              <p className="text-sm text-gray-600 mt-2 font-medium">Employment with non-compete</p>
            </button>
            <button onClick={() => loadSample('loan')} className="p-5 bg-white/70 backdrop-blur-md border border-white/80 rounded-3xl text-left hover:bg-white hover:scale-105 hover:shadow-xl transition-all focus:ring-4 focus:ring-indigo-500/30 outline-none shadow-md shadow-indigo-100/30 group">
              <h3 className="font-bold text-base text-gray-900 group-hover:text-indigo-600 transition-colors">Loan Agreement</h3>
              <p className="text-sm text-gray-600 mt-2 font-medium">Personal loan with penalties</p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
