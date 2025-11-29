export interface Candidate {
  id: string
  full_name: string
  email: string
  phone_number: string
  country: string
  city: string
  seniority_level?: "junior" | "mid" | "senior"
  linkedin_url?: string
  github_url?: string
  portfolio_url?: string
  created_at: string
}

export interface JobPosting {
  id: string
  company_id: string
  company_name: string
  company_logo?: string
  title: string
  description: string
  area: string
  contract_type: string
  salary_min?: number
  salary_max?: number
  modality: "remote" | "hybrid" | "onsite"
  location: string
  required_skills: {
    languages?: string[]
    years_experience?: number
  }
  published_at: string
}

export interface Application {
  id: string
  job_posting_id: string
  job_title: string
  company_name: string
  status: "pending" | "interview_in_progress" | "evaluation_completed" | "hired" | "rejected"
  global_score?: number
  cv_score?: number
  technical_score?: number
  soft_skills_score?: number
  global_score_explanation?: string
  created_at: string
  interview_started_at?: string
  interview_completed_at?: string
}

export interface ChatMessage {
  id: string
  sender: "agent" | "candidate"
  message_text: string
  timestamp: string
  question_category?: "knockout" | "technical" | "soft_skills"
  score?: number
  explanation?: string
}
