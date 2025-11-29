from enum import Enum


class ApplicationStatus(str, Enum):
    """Estados de una aplicación/postulación"""
    PENDING = "pending"
    INTERVIEW_IN_PROGRESS = "interview_in_progress"
    EVALUATION_COMPLETED = "evaluation_completed"
    RANKED = "ranked"
    HIRED = "hired"
    REJECTED = "rejected"


class JobPostingStatus(str, Enum):
    """Estados de una vacante"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class HiringDecision(str, Enum):
    """Decisión de contratación"""
    PENDING = "pending"
    SHORTLISTED = "shortlisted"
    HIRED = "hired"
    REJECTED = "rejected"


class SeniorityLevel(str, Enum):
    """Nivel de experiencia del candidato"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class ContractType(str, Enum):
    """Tipo de contrato"""
    FTC = "FTC"  # Full Time Contract
    PTC = "PTC"  # Part Time Contract
    INTERNSHIP = "Internship"


class Modality(str, Enum):
    """Modalidad de trabajo"""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class QuestionCategory(str, Enum):
    """Categoría de pregunta en la entrevista"""
    KNOCKOUT = "knockout"
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    CLOSING = "closing"


class InterviewPhase(str, Enum):
    """Fases de la entrevista"""
    GREETING = "greeting"
    KNOCKOUT = "knockout"
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    CLOSING = "closing"


class MessageSender(str, Enum):
    """Quién envía un mensaje en la entrevista"""
    AGENT = "agent"
    CANDIDATE = "candidate"