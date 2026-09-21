import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { EscalationBanner, SeverityBadge, CitationChip } from '../../components';
import { ClauseDetail } from './ClauseDetail';
import { AskPage } from './AskPage';
import { ComparePage } from './ComparePage';
import { ActionsPage } from './ActionsPage';

import { useDocumentStore } from '../../stores/documentStore';

export function ResultsPage() {
  const { t: _t } = useTranslation();
  const { document } = useDocumentStore();
  const [activeTab, setActiveTab] = useState<'Overview' | 'Risks' | 'Ask' | 'Compare' | 'Actions'>('Overview');

  const [selectedClause, setSelectedClause] = useState<any>(null);

  const urgency = {
    deadline: '27 Sep 2026',
    reason: 'This notice requires you to vacate the premises by the stated deadline or face legal action.',
    resources: [{ name: 'Tenant Rights Association', url: '#' }]
  };

  const sampleFindings = [
    {
      id: 'f1', clauseId: '5.2', severity: 'High' as const, category: 'Deposit', 
      whatItSays: 'The landlord can keep the deposit for any wear and tear.',
      whatItMeans: 'You might not get your money back even if you take good care of the place.',
      whyItMatters: 'Standard leases only allow deductions for actual damages, not normal wear.',
      questionToAsk: 'Can we specify that standard wear and tear is exempt from deductions?',
      needsReview: true,
      sourceText: 'The Licensor shall be entitled to deduct from the Security Deposit any amounts for wear and tear...'
    },
    {
      id: 'f2', clauseId: '4.1', severity: 'High' as const, category: 'Termination', 
      whatItSays: 'The agreement can be terminated without cause at any time.',
      whatItMeans: 'You could be forced to move out with no notice.',
      whyItMatters: 'This provides zero housing security.',
      sourceText: 'The Licensor may terminate this Agreement at any time without assigning any reason.'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'Overview':
        return (
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
              <div className="bg-gray-50 px-5 py-3 border-b border-gray-200 font-bold text-gray-800">
                Key Facts
              </div>
              <div className="p-0">
                <table className="min-w-full divide-y divide-gray-200">
                  <tbody className="bg-white divide-y divide-gray-100">
                    <tr><td className="px-5 py-3 whitespace-nowrap text-sm font-medium text-gray-500 w-1/3">Rent</td><td className="px-5 py-3 text-sm font-bold text-gray-900 w-1/3">₹25,000 / month</td><td className="px-5 py-3 text-right"><CitationChip clauseId="2.1" onClick={() => {}} /></td></tr>
                    <tr><td className="px-5 py-3 whitespace-nowrap text-sm font-medium text-gray-500">Deposit</td><td className="px-5 py-3 text-sm font-bold text-gray-900">₹75,000</td><td className="px-5 py-3 text-right"><CitationChip clauseId="5.2" onClick={() => {}} /></td></tr>
                    <tr><td className="px-5 py-3 whitespace-nowrap text-sm font-medium text-gray-500">Lock-in</td><td className="px-5 py-3 text-sm font-bold text-gray-900">11 months</td><td className="px-5 py-3 text-right"><CitationChip clauseId="3.4" onClick={() => {}} /></td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
              <h3 className="font-bold text-gray-900 mb-3">Summary</h3>
              <p className="text-gray-700 leading-relaxed">
                This is a standard leave and licence agreement for 11 months. You are required to pay a security deposit of ₹75,000. 
                There are significant risks regarding the termination clause and deposit deductions. 
                Read the Risks tab for more details.
              </p>
            </div>
          </div>
        );
      case 'Risks':
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 flex items-center justify-between">
              <span className="font-bold text-gray-900">Risk Radar</span>
              <div className="flex gap-3 text-sm">
                <SeverityBadge severity="High" /> <span className="font-medium">2</span>
                <SeverityBadge severity="Medium" /> <span className="font-medium">3</span>
                <SeverityBadge severity="Low" /> <span className="font-medium">2</span>
              </div>
            </div>
            
            <div className="space-y-3">
              {sampleFindings.map(f => (
                <button 
                  key={f.id}
                  onClick={() => setSelectedClause(f)}
                  className="w-full text-left bg-white border border-gray-200 rounded-lg p-4 hover:border-brand hover:shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-focus flex flex-col sm:flex-row sm:items-center gap-4"
                >
                  <div className="flex-shrink-0 w-24">
                    <SeverityBadge severity={f.severity} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-gray-900 mb-1">{f.whatItSays}</h4>
                    <p className="text-sm text-gray-600 line-clamp-1">{f.whyItMatters}</p>
                  </div>
                  <div className="text-sm font-mono text-gray-400 font-medium">§{f.clauseId}</div>
                  <div className="text-brand">→</div>
                </button>
              ))}
            </div>
          </div>
        );
      case 'Ask': return <AskPage />;
      case 'Compare': return <ComparePage />;
      case 'Actions': return <ActionsPage />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-transparent">
      <div className="flex-1 flex overflow-hidden">
        {/* Document pane - Desktop only */}
        <div className="hidden lg:flex flex-col w-1/2 border-r border-gray-200/50 bg-white/40 backdrop-blur-sm">
          <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between shrink-0">
            <div>
              <h2 className="font-bold text-gray-800 uppercase tracking-wider text-xs mb-1">DOCUMENT</h2>
              <p className="font-medium text-gray-900">{document?.fileName || 'Document'}</p>
            </div>
            <div className="text-right">
              <span className="inline-block bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded font-medium">{document?.role || 'User'}</span>
            </div>
          </div>
          <div className="flex-1 p-8 overflow-y-auto font-serif text-gray-800 leading-[1.8] text-[1.1rem] whitespace-pre-wrap">
            {document?.text ? (
              document.text.includes('[[SAMPLE:') ? (
                <>
                  <h2 className="text-xl font-bold mb-4 font-sans text-center uppercase">Sample Agreement</h2>
                  <p className="mb-4">This is a sample document...</p>
                  
                  <h3 className="text-lg font-bold mt-6 mb-2 font-sans" id="clause-2.1">2. RENT</h3>
                  <p className="mb-4">2.1 The Licensee shall pay a monthly compensation of ₹25,000...</p>

                  <h3 className="text-lg font-bold mt-6 mb-2 font-sans" id="clause-4.1">4. TERMINATION</h3>
                  <p className="mb-4 bg-red-50 border-l-4 border-red-400 pl-3 py-1">
                    <mark className="bg-transparent font-bold">4.1 The Licensor may terminate this Agreement at any time without assigning any reason.</mark>
                  </p>

                  <h3 className="text-lg font-bold mt-6 mb-2 font-sans" id="clause-5.2">5. SECURITY DEPOSIT</h3>
                  <p className="mb-4 bg-red-50 border-l-4 border-red-400 pl-3 py-1">
                    <mark className="bg-transparent font-bold">5.2 The Licensor shall be entitled to deduct from the Security Deposit any amounts for wear and tear...</mark>
                  </p>
                </>
              ) : (
                document.text
              )
            ) : (
              <p className="text-gray-500 italic">No document text available.</p>
            )}
          </div>
        </div>

        {/* Insights pane */}
        <div className="flex-1 flex flex-col bg-white overflow-hidden">
          {urgency && (
            <div className="shrink-0">
              <EscalationBanner {...urgency} />
            </div>
          )}

          <div className="border-b border-gray-200 flex overflow-x-auto shrink-0 scrollbar-hide">
            {['Overview', 'Risks', 'Ask', 'Compare', 'Actions'].map((tab) => (
              <button 
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-6 py-4 font-bold text-sm border-b-2 whitespace-nowrap focus:outline-none focus:bg-gray-50 transition-colors ${
                  activeTab === tab 
                    ? 'border-brand text-brand' 
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
            <div className="max-w-2xl mx-auto h-full">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>

      <ClauseDetail isOpen={!!selectedClause} onClose={() => setSelectedClause(null)} finding={selectedClause} />
    </div>
  );
}
