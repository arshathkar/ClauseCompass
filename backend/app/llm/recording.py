import hashlib
import json
import os
from typing import Literal, Type, TypeVar
from app.core.errors import AppError
from app.llm.base import LLMClient, LLMResult, TaskName

T = TypeVar("T")

class RecordingClient:
    def __init__(self, inner_client: LLMClient, fixtures_dir: str | None = None, allow_recording: bool = False):
        if fixtures_dir is None:
            from app.core.settings import settings
            fixtures_dir = str(settings.data_dir / "fixtures" / "llm")
        self.inner_client = inner_client
        self.fixtures_dir = fixtures_dir
        self.allow_recording = allow_recording

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
        
        if not self.allow_recording:
            # We refuse to record unless explicitly allowed (e.g., flag in context indicating synthetic document)
            raise AppError(detail="Recording is only allowed for synthetic documents")
            
        result = await self.inner_client.generate_json(
            task=task,
            system=system,
            user=user,
            schema=schema,
            tier=tier,
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
        
        prompt_version = "1.0"
        hash_input = f"{task.value}{prompt_version}{user}".encode("utf-8")
        hash16 = hashlib.sha256(hash_input).hexdigest()[:16]
        
        dir_path = os.path.join(self.fixtures_dir, task.value)
        os.makedirs(dir_path, exist_ok=True)
        
        fixture_path = os.path.join(dir_path, f"{hash16}.json")
        
        # Write only if it doesn't exist
        if not os.path.exists(fixture_path):
            with open(fixture_path, "w", encoding="utf-8") as f:
                json.dump(result.data.model_dump(), f, indent=2, ensure_ascii=False)
                
        return result
