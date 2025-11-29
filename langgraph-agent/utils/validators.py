"""Input validation utilities."""

import re
from typing import Optional
from uuid import UUID


def validate_uuid(value: str) -> bool:
    """
    Validate UUID format.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID
    """
    try:
        UUID(value, version=4)
        return True
    except (ValueError, AttributeError):
        return False


def validate_phase(phase: str) -> bool:
    """
    Validate interview phase value.
    
    Args:
        phase: Phase string to validate
        
    Returns:
        True if valid phase
    """
    valid_phases = {"knockout", "technical", "soft_skills", "closing"}
    return phase in valid_phases


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input text.
    
    - Remove HTML tags
    - Remove control characters
    - Trim whitespace
    - Optionally limit length
    
    Args:
        text: Text to sanitize
        max_length: Optional max length
        
    Returns:
        Sanitized text
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "..."
    
    return text.strip()


def validate_score(score: float) -> bool:
    """
    Validate score is within range.
    
    Args:
        score: Score value
        
    Returns:
        True if valid (0-5 range)
    """
    return isinstance(score, (int, float)) and 0 <= score <= 5
