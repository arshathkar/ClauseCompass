import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { CitationChip, ReadAloudButton } from '../../components';
import { useSSE } from '../../lib/sse';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  isAbstention?: boolean;
}

export function AskPage() {
  const { t: _t } = useTranslation();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'I can answer questions based strictly on the contents of your document. What would you like to know?'
    }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { events, isStreaming } = useSSE();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, events]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    
    // Create placeholder for assistant response
    const asstMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: asstMsgId, role: 'assistant', content: '' }]);

    // Trigger SSE (simulated endpoint or actual if backend is running)
    // await startStream('/v1/chat', { question: input }, { 'X-Session-Id': sessionId || '' });
    
    // For demo/UI completeness, simulate streaming
    simulateStreaming(asstMsgId, input);
  };

  const simulateStreaming = (msgId: string, q: string) => {
    const isAbstention = q.toLowerCase().includes('who is the president');
    let content = isAbstention 
      ? 'The document does not provide information about that.' 
      : 'Based on the document, this is the answer to your question. ';
      
    let i = 0;
    const interval = setInterval(() => {
      if (i < content.length) {
        setMessages(prev => prev.map(m => 
          m.id === msgId ? { ...m, content: m.content + content[i] } : m
        ));
        i++;
      } else {
        clearInterval(interval);
        setMessages(prev => prev.map(m => 
          m.id === msgId ? { 
            ...m, 
            isAbstention, 
            citations: isAbstention ? [] : ['4.1', '5.2']
          } : m
        ));
      }
    }, 20);
  };

  const suggestions = [
    "What is the notice period?",
    "Can the landlord keep my deposit?",
    "Are there any penalties for late payment?"
  ];

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
              msg.role === 'user' 
                ? 'bg-brand text-white rounded-br-none' 
                : 'bg-gray-100 text-gray-800 rounded-bl-none'
            }`}>
              {msg.role === 'assistant' && (
                <div className="flex justify-between items-start mb-1">
                  <span className="text-xs font-bold text-gray-500 uppercase">ClauseCompass</span>
                  {msg.content && !isStreaming && <ReadAloudButton text={msg.content} />}
                </div>
              )}
              
              <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
                {msg.content}
                {msg.role === 'assistant' && isStreaming && msg.id === messages[messages.length-1].id && (
                  <span className="inline-block w-2 h-4 ml-1 bg-brand animate-pulse"></span>
                )}
              </div>
              
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200/50 flex flex-wrap gap-2">
                  <span className="text-xs text-gray-500 font-medium pt-1">Sources:</span>
                  {msg.citations.map(c => (
                    <CitationChip key={c} clauseId={c} onClick={(id) => console.log('scroll to', id)} />
                  ))}
                </div>
              )}

              {msg.isAbstention && (
                <div className="mt-4 bg-white border border-gray-200 p-4 rounded text-sm text-gray-700">
                  <p className="font-semibold text-gray-900 mb-2">I can only answer from the document.</p>
                  <p>Consider asking a professional or checking these resources:</p>
                  <ul className="list-disc ml-5 mt-2 text-brand underline cursor-pointer">
                    <li>Free legal aid center</li>
                    <li>Consumer forum guidelines</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
          {suggestions.map((s, i) => (
            <button 
              key={i}
              onClick={() => setInput(s)}
              className="whitespace-nowrap bg-white border border-gray-300 text-sm text-brand px-3 py-1.5 rounded-full hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-focus"
            >
              {s}
            </button>
          ))}
        </div>
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your document..."
            className="flex-1 rounded-full border-gray-300 border p-3 pl-6 focus:border-brand focus:ring-brand shadow-sm"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="bg-brand text-white w-12 h-12 rounded-full flex items-center justify-center hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-focus focus:ring-offset-2 disabled:opacity-50"
            aria-label="Send message"
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  );
}
