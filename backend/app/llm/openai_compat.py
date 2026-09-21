import json
import time
from typing import Any, Dict, Literal, Optional, Type, TypeVar
import httpx
from pydantic import ValidationError
from pydantic.json_schema import models_json_schema

from app.core.errors import LLMInvalidOutputError
from app.core.logging import get_logger
from app.core.settings import settings
from app.llm.base import LLMClient, LLMResult, TaskName

logger = get_logger(__name__)
T = TypeVar("T")


class OpenAICompatClient:
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str],
        model_fast: str,
        model_analysis: str,
        provider_name: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_fast = model_fast
        self.model_analysis = model_analysis
        self.provider_name = provider_name
        self._client = httpx.AsyncClient(timeout=45.0)

    async def _call_api(
        self,
        model: str,
        system: str,
        user: str,
        json_schema: Dict[str, Any],
        max_output_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_output_tokens,
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "response_schema",
                    "schema": json_schema,
                    "strict": True,
                },
            },
        }

        start_time = time.monotonic()
        try:
            response = await self._client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error("LLM API HTTP error", extra={"status": e.response.status_code, "response": e.response.text})
            raise
        except Exception as e:
            logger.error("LLM API connection error", exc_info=True)
            raise

        latency_ms = int((time.monotonic() - start_time) * 1000)
        return {
            "data": data,
            "latency_ms": latency_ms,
        }

    async def generate_json(
        self,
        *,
        task: TaskName,
        system: str,
        user: str,
        schema: Type[T],
        tier: Literal["fast", "analysis"],
        max_output_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResult[T]:
        model = self.model_analysis if tier == "analysis" else self.model_fast
        
        # Extract json schema from pydantic model
        _, schema_dict = models_json_schema([(schema, "validation")])
        if schema.__name__ in schema_dict.get("$defs", {}):
            actual_schema = schema_dict["$defs"][schema.__name__]
        else:
            actual_schema = schema.model_json_schema()

        # One repair retry loop
        for attempt in range(2):
            result = await self._call_api(
                model=model,
                system=system,
                user=user,
                json_schema=actual_schema,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
            )
            
            raw_data = result["data"]
            try:
                message = raw_data["choices"][0]["message"]["content"]
                parsed_json = json.loads(message)
                validated_data = schema.model_validate(parsed_json)
                
                usage = raw_data.get("usage", {})
                return LLMResult(
                    data=validated_data,
                    provider=self.provider_name,
                    model=model,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    latency_ms=result["latency_ms"],
                    cache_hit=False,
                    prompt_version="1.0", # TODO: dynamic prompt version
                )
            except (KeyError, json.JSONDecodeError, ValidationError) as e:
                logger.warning(
                    "Failed to parse or validate LLM output",
                    extra={"attempt": attempt + 1, "error": str(e)},
                )
                if attempt == 1:
                    raise LLMInvalidOutputError(detail="LLM returned invalid output format after repair retry.") from e
                
                # Append repair instructions for the next attempt
                user += f"\n\nPrevious attempt failed with error: {str(e)}. Please correct the JSON output."
        
        raise LLMInvalidOutputError(detail="Unreachable.")
