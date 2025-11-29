-- ============================================================
-- ESQUEMA COMPLETO - SUPABASE (Rol 1)
-- ============================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- TABLA: companies
-- ============================================================
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  sector VARCHAR(100),
  size VARCHAR(50), -- startup, pyme, grande
  country VARCHAR(50),
  description TEXT,
  logo_url VARCHAR(500),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  whatsapp_number VARCHAR(20),
  whatsapp_token VARCHAR(500),
  
  CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Índices
CREATE INDEX idx_companies_email ON companies(email);

-- RLS (Row Level Security)
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Companies are publicly readable" ON companies
  FOR SELECT USING (true);

CREATE POLICY "Companies can update themselves" ON companies
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Companies can delete themselves" ON companies
  FOR DELETE USING (auth.uid() = id);

-- ============================================================
-- TABLA: job_postings
-- ============================================================
CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  area VARCHAR(100),
  contract_type VARCHAR(50),
  salary_min INTEGER,
  salary_max INTEGER,
  modality VARCHAR(50),
  location VARCHAR(255),
  required_skills JSONB,
  nice_to_have_skills JSONB,
  custom_questions JSONB,
  knockout_criteria JSONB,
  job_template_context TEXT,
  status VARCHAR(50) DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  
  CONSTRAINT status_check CHECK (status IN ('draft', 'published', 'closed'))
);

-- Índices
CREATE INDEX idx_job_postings_company_id ON job_postings(company_id);
CREATE INDEX idx_job_postings_status ON job_postings(status);
CREATE INDEX idx_job_postings_published_at ON job_postings(published_at DESC);

-- RLS
ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Published jobs are publicly readable" ON job_postings
  FOR SELECT USING (status = 'published' OR auth.uid() = company_id);

CREATE POLICY "Companies can manage their jobs" ON job_postings
  FOR ALL USING (auth.uid() = company_id);

-- ============================================================
-- TABLA: candidates
-- ============================================================
CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  phone_number VARCHAR(20) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  country VARCHAR(50),
  city VARCHAR(100),
  seniority_level VARCHAR(50),
  expected_salary INTEGER,
  linkedin_url VARCHAR(500),
  github_url VARCHAR(500),
  portfolio_url VARCHAR(500),
  cv_text_extracted TEXT,
  cv_embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Índices
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_phone ON candidates(phone_number);
CREATE INDEX idx_candidates_cv_embedding ON candidates USING ivfflat(cv_embedding vector_cosine_ops);

-- RLS
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates are publicly readable (limited)" ON candidates
  FOR SELECT USING (true);

CREATE POLICY "Candidates can update themselves" ON candidates
  FOR UPDATE USING (auth.uid() = id);

-- ============================================================
-- TABLA: applications
-- ============================================================
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  
  cv_file_url VARCHAR(500),
  
  status VARCHAR(50) DEFAULT 'pending',
  cv_score NUMERIC(3,1),
  cv_score_explanation TEXT,
  technical_score NUMERIC(3,1),
  technical_score_explanation TEXT,
  soft_skills_score NUMERIC(3,1),
  soft_skills_score_explanation TEXT,
  global_score NUMERIC(3,1) DEFAULT 0,
  global_score_explanation TEXT,
  
  interview_started_at TIMESTAMPTZ,
  interview_completed_at TIMESTAMPTZ,
  interview_duration_minutes INTEGER,
  
  hiring_decision VARCHAR(50),
  rejection_reason VARCHAR(255),
  hire_date DATE,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT status_check CHECK (status IN ('pending', 'interview_in_progress', 'evaluation_completed', 'ranked', 'hired', 'rejected')),
  CONSTRAINT hiring_decision_check CHECK (hiring_decision IN ('pending', 'shortlisted', 'hired', 'rejected')),
  CONSTRAINT unique_application UNIQUE(candidate_id, job_posting_id)
);

-- Índices
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_posting_id ON applications(job_posting_id);
CREATE INDEX idx_applications_company_id ON applications(company_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_global_score ON applications(global_score DESC);

-- RLS
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates see their applications" ON applications
  FOR SELECT USING (auth.uid() = candidate_id);

CREATE POLICY "Companies see their applications" ON applications
  FOR SELECT USING (auth.uid() = company_id);

CREATE POLICY "Backend can manage applications" ON applications
  FOR ALL USING (true);

-- ============================================================
-- TABLA: interview_messages
-- ============================================================
CREATE TABLE interview_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  
  sender VARCHAR(50) NOT NULL,
  message_text TEXT NOT NULL,
  message_type VARCHAR(50),
  question_category VARCHAR(50),
  
  order_index INTEGER,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  
  agent_score NUMERIC(2,1),
  agent_scoring_explanation TEXT
);

-- Índices
CREATE INDEX idx_interview_messages_application_id ON interview_messages(application_id);
CREATE INDEX idx_interview_messages_order ON interview_messages(application_id, order_index);

-- RLS
ALTER TABLE interview_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates see their interview messages" ON interview_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM applications 
      WHERE applications.id = interview_messages.application_id 
      AND applications.candidate_id = auth.uid()
    )
  );

CREATE POLICY "Companies see their application messages" ON interview_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM applications 
      WHERE applications.id = interview_messages.application_id 
      AND applications.company_id = auth.uid()
    )
  );

-- ============================================================
-- TABLA: agent_conversations
-- ============================================================
CREATE TABLE agent_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  
  recruiter_question TEXT NOT NULL,
  agent_response TEXT NOT NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  context_snapshot JSONB
);

-- Índices
CREATE INDEX idx_agent_conversations_job_id ON agent_conversations(job_posting_id);
CREATE INDEX idx_agent_conversations_company_id ON agent_conversations(company_id);

-- RLS
ALTER TABLE agent_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Companies see their agent conversations" ON agent_conversations
  FOR SELECT USING (auth.uid() = company_id);

-- ============================================================
-- TABLA: onboarding_templates
-- ============================================================
CREATE TABLE onboarding_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  
  recipient_email VARCHAR(255) NOT NULL,
  recipient_name VARCHAR(255) NOT NULL,
  
  subject VARCHAR(255),
  body TEXT,
  
  generated_at TIMESTAMPTZ DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  status VARCHAR(50) DEFAULT 'generated',
  
  company_name VARCHAR(255),
  job_title VARCHAR(255),
  start_date DATE,
  first_day_checklist JSONB
);

-- RLS
ALTER TABLE onboarding_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Companies see their onboarding templates" ON onboarding_templates
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM applications 
      WHERE applications.id = onboarding_templates.application_id 
      AND applications.company_id = auth.uid()
    )
  );

-- ============================================================
-- VISTA: v_candidates_ranked_by_job
-- ============================================================
CREATE VIEW v_candidates_ranked_by_job AS
SELECT 
  app.id as application_id,
  app.job_posting_id,
  c.full_name,
  c.email,
  jp.title as job_title,
  app.global_score,
  app.cv_score,
  app.technical_score,
  app.soft_skills_score,
  app.status,
  app.created_at,
  ROW_NUMBER() OVER (PARTITION BY app.job_posting_id ORDER BY app.global_score DESC) as rank
FROM applications app
JOIN candidates c ON app.candidate_id = c.id
JOIN job_postings jp ON app.job_posting_id = jp.id
WHERE app.status IN ('evaluation_completed', 'ranked', 'hired')
ORDER BY app.job_posting_id, rank;