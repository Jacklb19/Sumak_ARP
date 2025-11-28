import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def validate_api_keys():
    """Validate that required API keys are configured"""
    
    required_keys = {
        "OPENAI_API_KEY": "OpenAI API",
        "SUPABASE_URL": "Supabase URL",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase Service Role Key"
    }
    
    optional_keys = {
        "NOTION_API_KEY": "Notion API",
        "TELEGRAM_BOT_TOKEN": "Telegram Bot",
        "APIFY_API_TOKEN": "Apify Token",
        "SERPER_API_KEY": "Serper API"
    }
    
    logger.info("🔑 Validating API Keys...")
    
    # Check required keys
    missing_required = []
    for key, name in required_keys.items():
        if not os.getenv(key):
            missing_required.append(f"  ❌ {name} ({key})")
        else:
            logger.info(f"  ✅ {name}")
    
    # Check optional keys
    for key, name in optional_keys.items():
        if os.getenv(key):
            logger.info(f"  ✅ {name} (optional)")
        else:
            logger.warning(f"  ⚠️ {name} not configured (optional)")
    
    if missing_required:
        error_msg = "Missing required API keys:\n" + "\n".join(missing_required)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("✅ All required API keys validated")

def clean_json_response(content: str) -> str:
    """
    Clean JSON response from LLM
    Handles markdown code blocks and formatting
    """
    
    # Remove markdown code blocks
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:].strip()
        content = content.rstrip("```").strip()
    
    return content

def parse_llm_json(response: Any) -> Dict[str, Any]:
    """
    Parse LLM response as JSON
    Handles common LLM formatting issues
    """
    
    try:
        import json
        
        content = response.content if hasattr(response, 'content') else str(response)
        content = clean_json_response(content)
        
        return json.loads(content)
    
    except Exception as e:
        logger.error(f"Error parsing LLM JSON: {e}")
        return {}
