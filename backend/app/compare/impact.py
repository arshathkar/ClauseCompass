from typing import Dict, List
from app.llm.base import LLMClient
from app.llm.schemas import ComparePair

# Note: this module would usually batch calls to the LLM to analyze the impact.
# Due to hackathon scoping and simplicity, this can be implemented in orchestrator or directly here.
