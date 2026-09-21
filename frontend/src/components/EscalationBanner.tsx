import { useEffect, useRef } from 'react';

interface Resource {
  name: string;
  url: string;
}

interface EscalationBannerProps {
  deadline?: string;
  reason: string;
  resources: Resource[];
}

export function EscalationBanner({ deadline, reason, resources }: EscalationBannerProps) {
  const bannerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Receive focus on load
    if (bannerRef.current) {
      bannerRef.current.focus();
    }
  }, []);

  return (
    <div 
      ref={bannerRef}
      role="alert" 
      aria-live="assertive"
      tabIndex={-1}
      className="bg-red-50 border-l-4 border-red-600 p-4 mb-6 outline-none focus:ring-2 focus:ring-focus"
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <span aria-hidden="true" className="text-red-600 font-bold text-xl">⚠</span>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-bold text-red-800">
            Time-sensitive: {deadline ? `this document mentions a deadline on ${deadline}` : 'immediate attention required'}
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{reason}</p>
          </div>
          {resources && resources.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-red-800 uppercase tracking-wider">Resources</h4>
              <ul className="mt-2 space-y-1">
                {resources.map((resource, i) => (
                  <li key={i}>
                    <a 
                      href={resource.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-red-600 hover:text-red-500 underline text-sm"
                    >
                      {resource.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
