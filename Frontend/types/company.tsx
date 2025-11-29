// <CHANGE> Adding TypeScript types for company entities
export interface Company {
  id: string
  name: string
  email: string
  sector?: string
  size?: string
  country?: string
  city?: string
  description?: string
  logo_url?: string
  whatsapp_number?: string
  created_at: string
}

export interface JobPosting {
  id: string
  company_id: string
  title: string
  description: string
  area: string
  contract_type: string
  salary_min?: number
  salary_max?: number
  modality: string
  location: string
  required_skills: string[]
  nice_to_have_skills?: string[]
  custom_questions?: string[]
  knockout_criteria?: string[]
  status: 'draft' | 'published' | 'closed'
  created_at: string
  updated_at: string
}

export interface RegisterCompanyRequest {
  company_name: string
  email: string
  password: string
  country?: string
  city?: string
  sector?: string
  size?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface CreateJobPostingRequest {
  title: string
  description: string
  area: string
  contract_type: string
  salary_min?: number
  salary_max?: number
  modality: string
  location: string
  required_skills: string[]
  nice_to_have_skills?: string[]
  custom_questions?: string[]
  knockout_criteria?: string[]
}

export interface UpdateCompanyRequest {
  sector?: string
  size?: string
  country?: string
  city?: string
  description?: string
  logo_url?: string
  whatsapp_number?: string
}
