"""Supabase client for database operations."""

from typing import Dict, Optional
from supabase import create_client, Client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """Singleton Supabase client."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("supabase_client_initialized", url=settings.supabase_url)
        return cls._instance


def get_job_posting(job_posting_id: str) -> Dict:
    """
    Fetch job posting from Supabase.
    
    Args:
        job_posting_id: UUID of job posting
        
    Returns:
        Job posting data
        
    Raises:
        Exception: If job not found or query fails
    """
    client = SupabaseClient.get_client()
    
    try:
        response = client.table("job_postings")\
            .select("*")\
            .eq("id", job_posting_id)\
            .single()\
            .execute()
        
        logger.info(
            "job_posting_fetched",
            job_id=job_posting_id,
            title=response.data.get("title")
        )
        
        return response.data
    
    except Exception as e:
        logger.error(
            "job_posting_fetch_failed",
            job_id=job_posting_id,
            error=str(e)
        )
        raise


def get_candidate(candidate_id: str) -> Dict:
    """
    Fetch candidate from Supabase.
    
    Args:
        candidate_id: UUID of candidate
        
    Returns:
        Candidate data
        
    Raises:
        Exception: If candidate not found or query fails
    """
    client = SupabaseClient.get_client()
    
    try:
        response = client.table("candidates")\
            .select("*")\
            .eq("id", candidate_id)\
            .single()\
            .execute()
        
        logger.info(
            "candidate_fetched",
            candidate_id=candidate_id,
            name=response.data.get("full_name")
        )
        
        return response.data
    
    except Exception as e:
        logger.error(
            "candidate_fetch_failed",
            candidate_id=candidate_id,
            error=str(e)
        )
        raise


def save_interview_message(
    application_id: str,
    sender: str,
    message_text: str,
    message_type: str,
    question_category: Optional[str] = None,
    order_index: Optional[int] = None,
    agent_score: Optional[float] = None,
    agent_scoring_explanation: Optional[str] = None
) -> Dict:
    """
    Save interview message to Supabase.
    
    Args:
        application_id: UUID of application
        sender: 'agent' or 'candidate'
        message_text: Content of message
        message_type: Type of message
        question_category: Category (knockout, technical, soft_skills)
        order_index: Order in conversation
        agent_score: Score if agent message
        agent_scoring_explanation: Score explanation
        
    Returns:
        Inserted message data
    """
    client = SupabaseClient.get_client()
    
    message_data = {
        "application_id": application_id,
        "sender": sender,
        "message_text": message_text,
        "message_type": message_type,
        "question_category": question_category,
        "order_index": order_index,
        "agent_score": agent_score,
        "agent_scoring_explanation": agent_scoring_explanation
    }
    
    # Remove None values
    message_data = {k: v for k, v in message_data.items() if v is not None}
    
    try:
        response = client.table("interview_messages")\
            .insert(message_data)\
            .execute()
        
        logger.info(
            "message_saved",
            application_id=application_id,
            sender=sender,
            category=question_category
        )
        
        return response.data[0] if response.data else {}
    
    except Exception as e:
        logger.error(
            "message_save_failed",
            application_id=application_id,
            error=str(e)
        )
        raise
