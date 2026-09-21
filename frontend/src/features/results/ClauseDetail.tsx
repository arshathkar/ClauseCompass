import * as Dialog from '@radix-ui/react-dialog';
import { useTranslation } from 'react-i18next';
import { SeverityBadge } from '../../components';

interface ClauseDetailProps {
  isOpen: boolean;
  onClose: () => void;
  finding: {
    id: string;
    clauseId: string;
    severity: 'High' | 'Medium' | 'Low' | 'Info';
    category: string;
    whatItSays: string;
    whatItMeans: string;
    whyItMatters: string;
    questionToAsk?: string;
    needsReview?: boolean;
    sourceText?: string;
  } | null;
}

export function ClauseDetail({ isOpen, onClose, finding }: ClauseDetailProps) {
  const { t } = useTranslation();

  if (!finding) return null;

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40 transition-opacity" />
        <Dialog.Content 
          className="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%] w-full max-w-2xl max-h-[90vh] bg-white rounded-lg shadow-xl z-50 overflow-hidden flex flex-col focus:outline-none"
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-3">
              <Dialog.Title className="text-lg font-bold text-gray-900 m-0">
                Clause {finding.clauseId}
              </Dialog.Title>
              <SeverityBadge severity={finding.severity} />
              {finding.needsReview && (
                <span className="text-xs font-semibold bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded border border-yellow-200">
                  Needs review
                </span>
              )}
            </div>
            <Dialog.Close asChild>
              <button 
                className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-focus rounded p-1"
                aria-label={t('common.close')}
              >
                ✕
              </button>
            </Dialog.Close>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {finding.sourceText && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r">
                <h3 className="text-xs font-bold text-yellow-800 uppercase tracking-wider mb-2">Source Text</h3>
                <p className="text-sm font-serif text-gray-800 line-clamp-4 hover:line-clamp-none transition-all">
                  "{finding.sourceText}"
                </p>
              </div>
            )}

            <div className="space-y-6">
              <div>
                <h3 className="font-bold text-gray-900 mb-1">{t('clause.whatItSays')}</h3>
                <p className="text-gray-700">{finding.whatItSays}</p>
              </div>
              
              <div>
                <h3 className="font-bold text-gray-900 mb-1">{t('clause.whatItMeans')}</h3>
                <p className="text-gray-700">{finding.whatItMeans}</p>
              </div>
              
              <div>
                <h3 className="font-bold text-gray-900 mb-1">{t('clause.whyItMatters')}</h3>
                <p className="text-gray-700">{finding.whyItMatters}</p>
              </div>
              
              {finding.questionToAsk && (
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                  <h3 className="font-bold text-blue-900 mb-1">{t('clause.question')}</h3>
                  <p className="text-blue-800 font-medium mb-3">"{finding.questionToAsk}"</p>
                  <button className="text-sm bg-white text-blue-700 border border-blue-300 font-semibold py-1.5 px-4 rounded hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-focus">
                    Copy question
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex justify-between items-center">
            <button className="text-sm text-gray-500 hover:text-red-600 underline underline-offset-2 focus:outline-none focus:ring-2 focus:ring-red-500 rounded px-1">
              {t('clause.wrong')}
            </button>
            <Dialog.Close asChild>
              <button className="bg-gray-200 text-gray-800 font-semibold py-2 px-6 rounded hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-focus">
                {t('common.close')}
              </button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
