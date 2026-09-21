import asyncio
import hashlib
import time
from typing import Any, Callable, Dict, Literal, Optional, Type, TypeVar
import httpx
from cachetools import TTLCache

from app.core.errors import CapacityExhaustedError, RateLimitedError
from app.core.logging import get_logger
from app.core.settings import settings
from app.llm.base import LLMClient, LLMResult, TaskName
from app.llm.budget import get_budget_tracker

logger = get_logger(__name__)
T = TypeVar("T")

# In-memory session cache for LLM results. Key format: {session_id}:{hash}
_llm_cache = TTLCache(maxsize=1000, ttl=settings.session_ttl_min * 60)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.monotonic()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("Circuit breaker OPENED")

    def record_success(self):
        self.failures = 0
        if self.state != "CLOSED":
            self.state = "CLOSED"
            logger.info("Circuit breaker CLOSED")

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker HALF_OPEN")
                return True
            return False
        # HALF_OPEN allows 1 execution
        return True


class ResilientClient:
    def __init__(self, primary_client: LLMClient, fallback_client: Optional[LLMClient] = None, replay_client: Optional[LLMClient] = None):
        self.primary_client = primary_client
        self.fallback_client = fallback_client
        self.replay_client = replay_client
        
        self.semaphore = asyncio.Semaphore(settings.llm_concurrency)
        self.breaker = CircuitBreaker()
        self.tokens_per_second = (settings.llm_rpm_limit * 0.8) / 60.0
        self.token_bucket = settings.llm_rpm_limit * 0.8
        self.last_refill = time.monotonic()

    async def _wait_rate_limit(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.token_bucket = min(
            settings.llm_rpm_limit * 0.8,
            self.token_bucket + elapsed * self.tokens_per_second
        )
        self.last_refill = now

        if self.token_bucket < 1.0:
            wait_time = (1.0 - self.token_bucket) / self.tokens_per_second
            await asyncio.sleep(wait_time)
            self.token_bucket = 0.0
            self.last_refill = time.monotonic()
        else:
            self.token_bucket -= 1.0

    async def _execute_with_retry(
        self,
        client: LLMClient,
        task: TaskName,
        system: str,
        user: str,
        schema: Type[T],
        tier: Literal["fast", "analysis"],
    ) -> LLMResult[T]:
        
        max_retries = settings.llm_max_retries
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                result = await client.generate_json(
                    task=task, system=system, user=user, schema=schema, tier=tier
                )
                self.breaker.record_success()
                return result
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429:
                    retry_after = e.response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after else base_delay * (2 ** attempt)
                    logger.warning("Rate limited (429)", extra={"attempt": attempt+1, "delay": delay})
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        continue
                elif status >= 500:
                    delay = base_delay * (2 ** attempt)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        continue
                
                self.breaker.record_failure()
                raise
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                self.breaker.record_failure()
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
                raise
        
        raise CapacityExhaustedError()

    async def generate_json(
        self,
        *,
        task: TaskName,
        system: str,
        user: str,
        schema: Type[T],
        tier: Literal["fast", "analysis"],
        session_id: str = "default",
        max_output_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResult[T]:
        
        # Check cache
        cache_key = hashlib.sha256(f"{task}:{system}:{user}:{tier}".encode()).hexdigest()
        full_cache_key = f"{session_id}:{cache_key}"
        if full_cache_key in _llm_cache:
            res = _llm_cache[full_cache_key]
            res.cache_hit = True
            return res

        # Check budget
        budget = get_budget_tracker(session_id)
        if task != TaskName.QUERY_REWRITE:
            budget.add_call(0, 0) # Token count is updated after call

        async with self.semaphore:
            await self._wait_rate_limit()
            
            clients_to_try = []
            if self.breaker.can_execute():
                clients_to_try.append(self.primary_client)
            if self.fallback_client:
                clients_to_try.append(self.fallback_client)
            if self.replay_client:
                clients_to_try.append(self.replay_client)
                
            last_err = None
            for client in clients_to_try:
                try:
                    result = await self._execute_with_retry(
                        client, task, system, user, schema, tier
                    )
                    budget.total_session_tokens += (result.input_tokens + result.output_tokens)
                    _llm_cache[full_cache_key] = result
                    return result
                except Exception as e:
                    logger.warning("LLM client failed, trying next", extra={"client_type": type(client).__name__})
                    last_err = e
            
            raise CapacityExhaustedError(detail="All LLM fallback options exhausted") from last_err
