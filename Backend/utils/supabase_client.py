from supabase import create_client
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client for Supabase database operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        
        self.client = create_client(self.url, self.key)
    
    # ============== CANDIDATES ==============
    
    def create_candidate(self, data: Dict[str, Any]):
        """Create a candidate"""
        try:
            return self.client.table('candidates').insert(data).execute()
        except Exception as e:
            logger.error(f"Error creating candidate: {e}")
            return None
    
    def get_candidate(self, candidate_id: str):
        """Get candidate by ID"""
        try:
            return self.client.table('candidates').select('*').eq(
                'id', candidate_id
            ).single().execute()
        except Exception as e:
            logger.error(f"Error getting candidate: {e}")
            return None
    
    def update_candidate(self, candidate_id: str, data: Dict[str, Any]):
        """Update candidate"""
        try:
            return self.client.table('candidates').update(data).eq(
                'id', candidate_id
            ).execute()
        except Exception as e:
            logger.error(f"Error updating candidate: {e}")
            return None
    
    # ============== EVALUATIONS ==============
    
    def create_evaluation(self, evaluation_data: Dict[str, Any]):
        """Create evaluation"""
        try:
            return self.client.table('evaluations').insert(evaluation_data).execute()
        except Exception as e:
            logger.error(f"Error creating evaluation: {e}")
            return None
    
    def get_evaluation(self, evaluation_id: str):
        """Get evaluation by ID"""
        try:
            return self.client.table('evaluations').select('*').eq(
                'id', evaluation_id
            ).single().execute()
        except Exception as e:
            logger.error(f"Error getting evaluation: {e}")
            return None
    
    def get_evaluations_by_company(self, company_id: str, limit: int = 100):
        """Get all evaluations for a company"""
        try:
            response = self.client.table('evaluations').select('*').eq(
                'company_id', company_id
            ).order('evaluated_at', desc=True).limit(limit).execute()
            return response.data if response else []
        except Exception as e:
            logger.error(f"Error getting evaluations: {e}")
            return []
    
    # ============== JOBS ==============
    
    def get_job(self, job_id: str):
        """Get job by ID"""
        try:
            return self.client.table('jobs').select('*').eq(
                'id', job_id
            ).single().execute()
        except Exception as e:
            logger.error(f"Error getting job: {e}")
            return None
    
    # ============== STATS ==============
    
    def get_stats(self, company_id: str):
        """Get company statistics"""
        try:
            # Count evaluations
            evals = self.client.table('evaluations').select('*').eq(
                'company_id', company_id
            ).execute()
            
            if not evals.data:
                return {"total_evaluations": 0}
            
            # Calculate averages
            total = len(evals.data)
            avg_score = sum(e.get('overall_score', 0) for e in evals.data) / total if total > 0 else 0
            
            return {
                "total_evaluations": total,
                "average_score": round(avg_score, 2),
                "recommended": sum(1 for e in evals.data if e.get('recommendation') == 'hire'),
                "maybe": sum(1 for e in evals.data if e.get('recommendation') == 'maybe'),
                "rejected": sum(1 for e in evals.data if e.get('recommendation') == 'reject')
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
