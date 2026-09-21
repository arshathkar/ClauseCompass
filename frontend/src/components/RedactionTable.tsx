
interface RedactionItem {
  type: string;
  found: string;
  placeholder: string;
  hidden: boolean;
}

interface RedactionTableProps {
  items: RedactionItem[];
  onToggle: (index: number) => void;
}

export function RedactionTable({ items, onToggle }: RedactionTableProps) {
  if (items.length === 0) {
    return <p className="text-gray-500 italic">No personal details detected automatically.</p>;
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg shadow-sm">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Found in your text</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sent to the AI as</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hide?</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item, idx) => (
            <tr key={idx} className={item.hidden ? '' : 'bg-red-50'}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.type}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className={item.hidden ? 'line-through opacity-75' : 'text-red-700 font-bold'}>{item.found}</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">{item.placeholder}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={item.hidden}
                    onChange={() => onToggle(idx)}
                    className="w-4 h-4 text-brand border-gray-300 rounded focus:ring-focus"
                    aria-label={`Hide ${item.type} ${item.found}`}
                  />
                  <span>{item.hidden ? 'Hidden' : 'Show (Not sent to AI)'}</span>
                </label>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
