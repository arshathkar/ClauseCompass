import hashlib
import json
import os
from typing import Literal, Type, TypeVar
from app.core.errors import AppError
from app.llm.base import LLMClient, LLMResult, TaskName

T = TypeVar("T")

class ReplayClient:
    def __init__(self, fixtures_dir: str | None = None):
        if fixtures_dir is None:
            from app.core.settings import settings
            fixtures_dir = str(settings.data_dir / "fixtures" / "llm")
        self.fixtures_dir = fixtures_dir

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
        
        prompt_version = "1.0" # TODO: extract from system prompt
        
        hash_input = f"{task.value}{prompt_version}{user}".encode("utf-8")
        hash16 = hashlib.sha256(hash_input).hexdigest()[:16]
        
        fixture_path = os.path.join(self.fixtures_dir, task.value, f"{hash16}.json")
        
        if not os.path.exists(fixture_path):
            raise AppError(detail=f"Replay fixture missing for {task.value} - {hash16}")
            
        with open(fixture_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        validated_data = schema.model_validate(raw_data)
        
        return LLMResult(
            data=validated_data,
            provider="replay",
            model="replay-model",
            input_tokens=0,
            output_tokens=0,
            latency_ms=10,
            cache_hit=True,
            prompt_version=prompt_version
        )
