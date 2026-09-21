
interface SeverityBadgeProps {
  severity: 'High' | 'Medium' | 'Low' | 'Info';
  size?: 'sm' | 'md';
}

export function SeverityBadge({ severity, size = 'md' }: SeverityBadgeProps) {
  const getStyles = () => {
    switch (severity) {
      case 'High': return 'bg-badge-high-bg text-badge-high-text';
      case 'Medium': return 'bg-badge-medium-bg text-badge-medium-text';
      case 'Low': return 'bg-badge-low-bg text-badge-low-text';
      case 'Info': return 'bg-badge-info-bg text-badge-info-text';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getIcon = () => {
    switch (severity) {
      case 'High': return '■'; // Filled square
      case 'Medium': return '▲'; // Triangle
      case 'Low': return '●'; // Circle
      case 'Info': return '○'; // Outlined circle
      default: return '·';
    }
  };

  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-2.5 py-0.5';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded ${sizeClass} border border-current ${getStyles()}`}>
      <span aria-hidden="true" className="text-[1.1em]">{getIcon()}</span>
      <span>{severity}</span>
    </span>
  );
}
