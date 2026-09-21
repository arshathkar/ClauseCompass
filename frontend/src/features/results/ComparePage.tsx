import { useState } from 'react';
import { DiffRow, FileDrop } from '../../components';

export function ComparePage() {
  const [hasSecondDoc, setHasSecondDoc] = useState(false);
  const [filter, setFilter] = useState<'All' | 'RiskUp' | 'Added' | 'Removed'>('All');

  const diffs = [
    { type: 'Changed' as const, risk: 'Up' as const, explanation: 'Notice period reduced from 60 to 30 days', old: '60 days written notice', new: '30 days written notice' },
    { type: 'Added' as const, risk: 'Neutral' as const, explanation: 'New clause defining regular maintenance', old: '', new: 'Tenant shall perform standard upkeep of HVAC filters.' },
    { type: 'Removed' as const, risk: 'Down' as const, explanation: 'Arbitration clause removed', old: 'All disputes shall be subject to binding arbitration.', new: '' }
  ];

  if (!hasSecondDoc) {
    return (
      <div className="p-8 max-w-2xl mx-auto space-y-6 text-center mt-10">
        <h2 className="text-2xl font-bold text-gray-900">Compare with another version</h2>
        <p className="text-gray-600">Upload a revised draft or competing offer to see what changed and how it affects your risk.</p>
        <div className="mt-8">
          <FileDrop onFileSelect={() => setHasSecondDoc(true)} />
        </div>
        <button 
          onClick={() => setHasSecondDoc(true)} 
          className="mt-4 text-brand font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-focus rounded px-2 py-1"
        >
          Try with sample documents
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b border-gray-200 bg-gray-50 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex gap-4">
          <div className="bg-white px-3 py-1.5 rounded border border-gray-200 text-sm shadow-sm font-medium">
            <span className="text-gray-500 mr-2">V1:</span> rental_draft_1.pdf
          </div>
          <div className="bg-white px-3 py-1.5 rounded border border-gray-200 text-sm shadow-sm font-medium">
            <span className="text-gray-500 mr-2">V2:</span> rental_draft_final.pdf
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-gray-700">Filter:</span>
          {['All', 'RiskUp', 'Added', 'Removed'].map(f => (
            <button 
              key={f}
              onClick={() => setFilter(f as any)}
              className={`px-3 py-1 text-sm font-medium rounded-full border focus:outline-none focus:ring-2 focus:ring-focus ${
                filter === f ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              {f === 'RiskUp' ? '↑ Risk Increased' : f}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border-b border-blue-100 px-6 py-3 text-sm text-blue-900 font-medium">
        Found {diffs.length} material changes (2 increase your risk). Formatting changes are ignored.
      </div>

      <ul className="flex-1 overflow-y-auto divide-y divide-gray-200">
        {diffs
          .filter(d => {
            if (filter === 'All') return true;
            if (filter === 'RiskUp') return d.risk === 'Up';
            if (filter === 'Added') return d.type === 'Added';
            if (filter === 'Removed') return d.type === 'Removed';
            return true;
          })
          .map((d, i) => (
            <DiffRow 
              key={i} 
              changeType={d.type} 
              riskDelta={d.risk} 
              explanation={d.explanation} 
              textOld={d.old} 
              textNew={d.new} 
            />
        ))}
        {diffs.length === 0 && (
          <div className="p-12 text-center text-gray-500 font-medium">
            No changes found.
          </div>
        )}
      </ul>
    </div>
  );
}
