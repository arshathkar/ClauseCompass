import time
import uuid
from typing import Dict, Any, Optional
from app.core.settings import settings
from app.core.errors import SessionExpiredError

class SessionData:
    def __init__(self, id: str):
        self.id = id
        self.created_at = time.monotonic()
        self.last_accessed = self.created_at
        self.data: Dict[str, Any] = {}

class SessionStore:
    def __init__(self, ttl_min: int = settings.session_ttl_min):
        self.ttl_sec = ttl_min * 60
        self._store: Dict[str, SessionData] = {}
        
    def _cleanup(self):
        now = time.monotonic()
        expired = [k for k, v in self._store.items() if (now - v.last_accessed) > self.ttl_sec]
        for k in expired:
            del self._store[k]
            
    def create(self) -> str:
        self._cleanup()
        session_id = str(uuid.uuid4())
        self._store[session_id] = SessionData(session_id)
        return session_id
        
    def get(self, session_id: str) -> SessionData:
        self._cleanup()
        if session_id not in self._store:
            raise SessionExpiredError()
        session = self._store[session_id]
        session.last_accessed = time.monotonic()
        return session
        
    def delete(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

# Global instance
session_store = SessionStore()
