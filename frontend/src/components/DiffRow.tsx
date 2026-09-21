

interface DiffRowProps {
  changeType: 'Added' | 'Removed' | 'Changed';
  riskDelta?: 'Up' | 'Down' | 'Neutral';
  textOld?: string;
  textNew?: string;
  explanation: string;
}

export function DiffRow({ changeType, riskDelta, textOld, textNew, explanation }: DiffRowProps) {
  const getChangeStyle = () => {
    switch (changeType) {
      case 'Added': return 'bg-green-50 border-green-200 text-green-900';
      case 'Removed': return 'bg-red-50 border-red-200 text-red-900 line-through';
      case 'Changed': return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      default: return 'bg-gray-50 border-gray-200 text-gray-900';
    }
  };

  const getRiskDeltaIcon = () => {
    if (riskDelta === 'Up') return <span aria-hidden="true" className="text-red-600">↑ Risk increased</span>;
    if (riskDelta === 'Down') return <span aria-hidden="true" className="text-green-600">↓ Risk decreased</span>;
    return <span aria-hidden="true" className="text-gray-500">↔ Neutral</span>;
  };

  return (
    <li className="flex flex-col lg:flex-row gap-4 p-4 border-b border-gray-200 last:border-0">
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-bold uppercase rounded border ${getChangeStyle()}`}>
            {changeType}
          </span>
          {riskDelta && <span className="text-sm font-medium">{getRiskDeltaIcon()}</span>}
        </div>
        <p className="text-sm text-gray-800 font-medium">{explanation}</p>
      </div>
      
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
        {changeType !== 'Added' && (
          <div className="bg-red-50/50 p-3 rounded border border-red-100">
            <h4 className="text-xs font-bold text-red-800 uppercase mb-1">Previous version</h4>
            <p className="text-sm font-mono text-gray-700">{textOld}</p>
          </div>
        )}
        
        {changeType !== 'Removed' && (
          <div className="bg-green-50/50 p-3 rounded border border-green-100">
            <h4 className="text-xs font-bold text-green-800 uppercase mb-1">New version</h4>
            <p className="text-sm font-mono text-gray-700">{textNew}</p>
          </div>
        )}
      </div>
    </li>
  );
}
