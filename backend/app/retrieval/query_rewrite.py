import os
from typing import Any, Dict
from pydantic import BaseModel
from app.llm.base import LLMClient, TaskName

class QueryRewriteResult(BaseModel):
    english_query: str
    keywords: list[str]
    language: str

async def rewrite_query(llm_client: LLMClient, question: str, language: str, session_id: str) -> str:
    path = os.path.join("backend", "app", "llm", "prompts", "query-rewrite@1.0.md")
    if not os.path.exists(path):
        path = os.path.join("app", "llm", "prompts", "query-rewrite@1.0.md")
        
    with open(path, "r", encoding="utf-8") as f:
        user_prompt = f.read().format(question=question, language=language)
        
    system_prompt = "You are a query rewriting assistant. Output JSON."
    
    res = await llm_client.generate_json(
        task=TaskName.QUERY_REWRITE,
        system=system_prompt,
        user=user_prompt,
        schema=QueryRewriteResult,
        tier="fast",
        session_id=session_id
    )
    return res.data.english_query
