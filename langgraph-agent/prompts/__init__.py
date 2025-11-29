"""Prompts module initialization."""

from prompts.knockout_prompts import (
    get_knockout_question_prompt,
    get_knockout_evaluation_prompt
)
from prompts.technical_prompts import (
    get_technical_question_prompt,
    get_technical_evaluation_prompt
)
from prompts.soft_skills_prompts import (
    get_soft_skills_question_prompt,
    get_soft_skills_evaluation_prompt
)

__all__ = [
    "get_knockout_question_prompt",
    "get_knockout_evaluation_prompt",
    "get_technical_question_prompt",
    "get_technical_evaluation_prompt",
    "get_soft_skills_question_prompt",
    "get_soft_skills_evaluation_prompt"
]
