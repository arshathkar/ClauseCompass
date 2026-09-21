import { useState, useEffect, useCallback, useRef } from 'react';

interface Announcement {
  message: string;
  timestamp: number;
}

let announceFn: (msg: string) => void = () => {};

export function announce(message: string) {
  announceFn(message);
}

export function StatusRegion() {
  const [announcement, setAnnouncement] = useState<Announcement | null>(null);
  const lastAnnouncementTime = useRef<number>(0);
  const timeoutId = useRef<any>(null);

  const handleAnnounce = useCallback((message: string) => {
    const now = Date.now();
    // Throttle announcements to at least 5s apart unless it's a critical error
    if (now - lastAnnouncementTime.current < 5000) {
      if (timeoutId.current) clearTimeout(timeoutId.current);
      timeoutId.current = setTimeout(() => {
        handleAnnounce(message);
      }, 5000 - (now - lastAnnouncementTime.current));
      return;
    }

    lastAnnouncementTime.current = now;
    setAnnouncement({ message, timestamp: now });
  }, []);

  useEffect(() => {
    announceFn = handleAnnounce;
    return () => {
      if (timeoutId.current) clearTimeout(timeoutId.current);
      announceFn = () => {};
    };
  }, [handleAnnounce]);

  return (
    <div 
      role="status" 
      aria-live="polite" 
      aria-atomic="true" 
      className="sr-only"
    >
      {announcement ? announcement.message : ''}
    </div>
  );
}
