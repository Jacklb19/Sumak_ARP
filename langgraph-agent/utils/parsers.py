"""Text parsing utilities for LLM responses."""

import re
from typing import Dict, Optional


def extract_question_from_llm(response: str) -> str:
    """
    Extract question from LLM response.
    
    Looks for patterns like:
    - QUESTION: [text]
    - Q: [text]
    - Falls back to entire response if no pattern found
    
    Args:
        response: Raw LLM response
        
    Returns:
        Extracted question text
    """
    patterns = [
        r"QUESTION:\s*(.+?)(?:\n|$)",
        r"Q:\s*(.+?)(?:\n|$)",
        r"PREGUNTA:\s*(.+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Fallback: return first non-empty line
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    return lines[0] if lines else response.strip()


def parse_evaluation_response(response: str) -> Dict[str, any]:
    """
    Parse evaluation response from LLM.
    
    Expected format:
    SCORE: 4.5
    EXPLANATION: Good answer because...
    AUTO_REJECT: false
    
    Args:
        response: Raw LLM evaluation response
        
    Returns:
        Dict with parsed values
    """
    result = {
        "score": 3.0,  # Default
        "explanation": "",
        "auto_reject": False
    }
    
    # Extract score
    score_match = re.search(r"SCORE:\s*([0-5](?:\.\d)?)", response, re.IGNORECASE)
    if score_match:
        try:
            result["score"] = float(score_match.group(1))
        except ValueError:
            pass
    
    # Extract explanation
    explanation_match = re.search(
        r"EXPLANATION:\s*(.+?)(?:\n[A-Z_]+:|$)",
        response,
        re.IGNORECASE | re.DOTALL
    )
    if explanation_match:
        result["explanation"] = explanation_match.group(1).strip()
    
    # Extract auto_reject
    if re.search(r"AUTO_REJECT:\s*true", response, re.IGNORECASE):
        result["auto_reject"] = True
    
    # Extract difficulty (for technical)
    difficulty_match = re.search(
        r"DIFFICULTY:\s*(easy|medium|hard)",
        response,
        re.IGNORECASE
    )
    if difficulty_match:
        result["difficulty"] = difficulty_match.group(1).lower()
    
    # Extract competency (for soft skills)
    competency_match = re.search(
        r"COMPETENCY:\s*(.+?)(?:\n|$)",
        response,
        re.IGNORECASE
    )
    if competency_match:
        result["competency"] = competency_match.group(1).strip()
    
    return result


def parse_score_from_text(text: str) -> Optional[float]:
    """
    Extract numeric score from text.
    
    Args:
        text: Text containing score
        
    Returns:
        Float score between 0-5, or None if not found
    """
    # Look for patterns like "4.5/5", "3.0", "score: 4"
    patterns = [
        r"(\d+\.?\d*)/5",
        r"score:\s*(\d+\.?\d*)",
        r"puntuación:\s*(\d+\.?\d*)",
        r"\b(\d+\.?\d*)\s*puntos?\b"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                score = float(match.group(1))
                if 0 <= score <= 5:
                    return score
            except ValueError:
                continue
    
    return None


def sanitize_llm_output(text: str) -> str:
    """
    Clean and sanitize LLM output.
    
    - Remove excessive whitespace
    - Remove markdown artifacts
    - Trim to reasonable length
    
    Args:
        text: Raw LLM output
        
    Returns:
        Cleaned text
    """
    # Remove markdown code blocks
    text = re.sub(r"``````", "", text)
    
    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length (safety)
    max_length = 2000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text
