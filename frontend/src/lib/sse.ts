import { useState, useCallback, useRef } from 'react';

export function useSSE<T = any>() {
  const [events, setEvents] = useState<T[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const abortController = useRef<AbortController | null>(null);

  const startStream = useCallback(async (url: string, body: any, headers?: Record<string, string>) => {
    try {
      setIsStreaming(true);
      setError(null);
      setEvents([]);
      
      abortController.current = new AbortController();
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          ...headers
        },
        body: JSON.stringify(body),
        signal: abortController.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop() || ''; // Keep the incomplete line in the buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') {
              setIsStreaming(false);
              return;
            }
            try {
              const data = JSON.parse(dataStr);
              setEvents(prev => [...prev, data]);
            } catch (e) {
              console.error('Failed to parse SSE data', e);
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        setError(e);
      }
    } finally {
      setIsStreaming(false);
    }
  }, []);

  const cancel = useCallback(() => {
    if (abortController.current) {
      abortController.current.abort();
    }
  }, []);

  return { events, error, isStreaming, startStream, cancel };
}
