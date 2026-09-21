import { useRef, useState } from 'react';

interface FileDropProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  isProcessing?: boolean;
  progress?: number; // 0-100
}

export function FileDrop({ onFileSelect, accept = ".pdf,.docx,.txt,.md", isProcessing, progress }: FileDropProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        isDragActive ? 'border-brand bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleChange} 
        accept={accept} 
        className="hidden" 
        aria-label="Upload document"
      />
      
      {isProcessing ? (
        <div className="space-y-4">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent text-brand rounded-full" role="status">
            <span className="sr-only">Loading...</span>
          </div>
          <p className="text-sm font-medium">Extracting text...</p>
          {progress !== undefined && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-brand h-2.5 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-gray-500">
            <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <p className="text-base text-gray-700">Drop your file here, or click to choose</p>
          <p className="text-sm text-gray-500">PDF, DOCX, TXT up to 10MB</p>
          <button 
            type="button" 
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand"
          >
            Choose file
          </button>
        </div>
      )}
    </div>
  );
}
