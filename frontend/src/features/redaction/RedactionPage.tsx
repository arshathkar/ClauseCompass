import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { RedactionTable } from '../../components';

interface RedactionPageProps {
  onContinue: () => void;
  onBack: () => void;
  initialItems?: Array<{ type: string; found: string; placeholder: string; hidden: boolean }>;
}

export function RedactionPage({ onContinue, onBack, initialItems = [] }: RedactionPageProps) {
  const { t } = useTranslation();
  const [items, setItems] = useState(initialItems);
  const [customTerm, setCustomTerm] = useState('');

  // Sample data if empty (for UI dev purposes if none passed)
  const displayItems = items.length > 0 ? items : [
    { type: 'Aadhaar', found: '2345 6789 0123', placeholder: '[[AADHAAR_1]]', hidden: true },
    { type: 'Phone', found: '+91 98765 43210', placeholder: '[[PHONE_1]]', hidden: true },
    { type: 'Email', found: 'meera@example.com', placeholder: '[[EMAIL_1]]', hidden: true }
  ];

  const handleToggle = (idx: number) => {
    const newItems = [...displayItems];
    newItems[idx].hidden = !newItems[idx].hidden;
    setItems(newItems);
  };

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customTerm.trim()) return;
    
    setItems([
      ...displayItems,
      {
        type: 'Custom',
        found: customTerm.trim(),
        placeholder: `[[CUSTOM_${displayItems.length + 1}]]`,
        hidden: true
      }
    ]);
    setCustomTerm('');
  };

  return (
    <div className="flex-1 max-w-4xl mx-auto w-full p-6 space-y-8 animate-in fade-in duration-500">
      <div className="text-center pt-4">
        <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 tracking-tight drop-shadow-sm pb-1 mb-2">{t('redaction.title')}</h1>
        <p className="text-gray-600 font-medium">
          {t('redaction.summary').replace('{{count}}', displayItems.length.toString())}
        </p>
      </div>

      <div className="bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white/50 shadow-xl shadow-indigo-100/50 space-y-6">
        <RedactionTable items={displayItems} onToggle={handleToggle} />

        <div className="bg-white/50 border border-white/80 p-6 rounded-2xl shadow-sm mt-6">
          <form onSubmit={handleAddCustom} className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 space-y-2 w-full">
              <label htmlFor="custom-term" className="block text-sm font-bold text-gray-800 uppercase tracking-wider">
                {t('redaction.addCustom')}
              </label>
              <input
                id="custom-term"
                type="text"
                value={customTerm}
                onChange={(e) => setCustomTerm(e.target.value)}
                placeholder="e.g., Meera Sharma"
                className="block w-full rounded-2xl bg-white/70 backdrop-blur-md border-white/50 shadow-inner focus:border-brand focus:ring-brand sm:text-base p-3 text-gray-900 transition-all"
              />
            </div>
            <button 
              type="submit"
              className="w-full sm:w-auto bg-white/80 backdrop-blur-sm border border-gray-200 text-gray-800 font-bold py-3 px-8 rounded-xl shadow-sm hover:bg-white focus:outline-none focus:ring-4 focus:ring-indigo-500/20 transition-all"
            >
              {t('redaction.add')}
            </button>
          </form>
          <p className="mt-4 text-sm text-gray-500 font-medium">
            {t('redaction.residualRisk')}
          </p>
        </div>
      </div>

      <div className="flex justify-between pt-6 border-t border-gray-300/50">
        <button 
          onClick={onBack}
          className="bg-white/60 backdrop-blur-sm text-gray-800 font-bold py-3 px-8 rounded-xl border border-white/80 shadow-sm hover:bg-white focus:outline-none focus:ring-4 focus:ring-indigo-500/20 transition-all"
        >
          {t('redaction.back')}
        </button>
        <button 
          onClick={onContinue}
          className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-bold py-3 px-8 rounded-xl hover:from-indigo-700 hover:to-blue-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/30 transition-all shadow-lg shadow-blue-500/30"
        >
          {t('redaction.continue')}
        </button>
      </div>
    </div>
  );
}
