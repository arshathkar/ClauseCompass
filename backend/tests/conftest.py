import pytest
from app.core.settings import Settings

@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def fake_llm():
    class FakeLLM:
        async def generate(self, prompt):
            return "Fake response"
    return FakeLLM()
