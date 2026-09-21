from typing import Any, Dict, Literal, Type, TypeVar
from app.llm.base import LLMClient, LLMResult, TaskName

T = TypeVar("T")

class FakeClient:
    def __init__(self, responses: Dict[TaskName, Any] = None):
        self.responses = responses or {}

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
        
        # Default mock responses
        data: Any = None
        if task in self.responses:
            data = self.responses[task]
        elif task == TaskName.DOC_TYPE:
            data = {"doc_type": "rental", "confidence": 0.9}
        elif task == TaskName.KEY_FACTS:
            data = {
                "facts": [{"label": "Rent", "value": "25000", "citation": None}],
                "obligations": [],
                "summary_simple": "Simple summary",
                "summary_standard": "Standard summary",
                "summary_detailed": "Detailed summary",
                "summary_citations": []
            }
        elif task == TaskName.CLAUSE_ANALYSIS:
            data = {"findings": []}
        elif task == TaskName.MISSING_CLAUSES:
            data = {"missing": []} # Or appropriate schema
        elif task == TaskName.QUERY_REWRITE:
            data = {"english_query": "test query", "keywords": ["test"], "language": "en"}
        elif task == TaskName.QA_ANSWER:
            data = {"answerable": True, "segments": [{"text": "Answer", "citations": []}], "follow_ups": [], "confidence": 0.9}
        elif task == TaskName.COMPARE_ADJUDICATE:
            data = {"pairs": []}
        elif task == TaskName.COMPARE_IMPACT:
            data = {"status": "changed", "citations": []}
        elif task == TaskName.EMAIL_DRAFT:
            data = {"subject": "Test", "body": "Test"}
            
        validated_data = schema.model_validate(data)
        
        return LLMResult(
            data=validated_data,
            provider="fake",
            model="fake-model",
            input_tokens=10,
            output_tokens=10,
            latency_ms=50,
            cache_hit=False,
            prompt_version="1.0"
        )
