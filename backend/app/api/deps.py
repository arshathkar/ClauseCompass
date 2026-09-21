from typing import Annotated
from fastapi import Depends, Header, HTTPException
from app.core.settings import settings
from app.llm.base import LLMClient
from app.llm.openai_compat import OpenAICompatClient
from app.llm.resilient import ResilientClient
from app.llm.fake import FakeClient
from app.llm.replay import ReplayClient
from app.session.store import SessionData, session_store


def get_llm_client() -> LLMClient:
    if settings.llm_mode == "fake":
        return FakeClient()
    elif settings.llm_mode == "replay":
        return ReplayClient()
    else:
        primary = OpenAICompatClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model_fast=settings.llm_model_fast,
            model_analysis=settings.llm_model_analysis,
            provider_name="primary"
        )
        fallback = None
        if settings.llm_fallback_base_url:
            fallback = OpenAICompatClient(
                base_url=settings.llm_fallback_base_url,
                api_key=settings.llm_fallback_api_key,
                model_fast=settings.llm_fallback_model,
                model_analysis=settings.llm_fallback_model,
                provider_name="fallback"
            )
        replay = ReplayClient() # for synthetic docs
        return ResilientClient(primary_client=primary, fallback_client=fallback, replay_client=replay)


def get_session(x_session_id: Annotated[str, Header()]) -> SessionData:
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Missing X-Session-Id header")
    return session_store.get(x_session_id)
