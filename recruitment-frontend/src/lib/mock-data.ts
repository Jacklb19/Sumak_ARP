export type Seniority = "Junior" | "Mid" | "Senior"
export type CandidateStatus = "Pending" | "Interviewing" | "Hired" | "Rejected"

export interface Candidate {
  id: string
  name: string
  email: string
  appliedRole: string
  seniority: Seniority
  technicalScore: number
  behavioralScore: number
  culturalFitScore: number
  overallScore: number
  status: CandidateStatus
  cvUrl: string
  linkedinUrl: string
  appliedDate: string
  aiSummary: {
    recommendation: string
    pros: string[]
    cons: string[]
  }
  transcript: {
    role: "ai" | "candidate"
    message: string
    timestamp: string
  }[]
}

export interface Job {
  id: string
  title: string
  department: string
  location: string
  status: "Open" | "Closed"
  applicants: number
}

export const mockCandidates: Candidate[] = [
  {
    id: "1",
    name: "Sarah Chen",
    email: "sarah.chen@email.com",
    appliedRole: "Senior Frontend Engineer",
    seniority: "Senior",
    technicalScore: 92,
    behavioralScore: 88,
    culturalFitScore: 95,
    overallScore: 91,
    status: "Interviewing",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/sarahchen",
    appliedDate: "2024-01-15",
    aiSummary: {
      recommendation:
        "Strongly Recommended. Sarah demonstrates exceptional technical proficiency with 8 years of React experience and strong leadership qualities. Her communication style aligns well with our collaborative culture.",
      pros: [
        "Deep expertise in React, TypeScript, and modern frontend architecture",
        "Proven track record leading teams of 5+ engineers",
        "Excellent problem-solving approach during technical discussions",
        "Strong alignment with company values around innovation",
      ],
      cons: [
        "Limited experience with our specific tech stack (Next.js)",
        "May require adjustment period for async-first communication",
        "Salary expectations slightly above budget",
      ],
    },
    transcript: [
      {
        role: "ai",
        message:
          "Hello Sarah! Welcome to your AI interview for the Senior Frontend Engineer position. I'm here to assess your technical skills and learn more about your experience. Are you ready to begin?",
        timestamp: "10:00 AM",
      },
      {
        role: "candidate",
        message:
          "Hi! Yes, I'm excited to be here. I've prepared for this and looking forward to discussing my experience.",
        timestamp: "10:01 AM",
      },
      {
        role: "ai",
        message:
          "Great! Let's start with your experience. Can you tell me about a complex frontend challenge you've solved recently?",
        timestamp: "10:01 AM",
      },
      {
        role: "candidate",
        message:
          "Absolutely. At my current role, I led the migration of our legacy jQuery application to React. The main challenge was maintaining business continuity while incrementally adopting the new framework. We implemented a micro-frontend architecture that allowed both systems to coexist.",
        timestamp: "10:03 AM",
      },
      {
        role: "ai",
        message: "Impressive approach! How did you handle state management across the micro-frontends?",
        timestamp: "10:04 AM",
      },
      {
        role: "candidate",
        message:
          "We used a custom event bus for cross-app communication and implemented a shared Redux store for common state. For isolated features, we used React Query for server state management.",
        timestamp: "10:06 AM",
      },
    ],
  },
  {
    id: "2",
    name: "Marcus Rodriguez",
    email: "marcus.r@email.com",
    appliedRole: "Backend Engineer",
    seniority: "Mid",
    technicalScore: 78,
    behavioralScore: 85,
    culturalFitScore: 82,
    overallScore: 81,
    status: "Pending",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/marcusrodriguez",
    appliedDate: "2024-01-18",
    aiSummary: {
      recommendation:
        "Recommended with reservations. Marcus shows solid foundational skills and excellent soft skills. Would benefit from mentorship in distributed systems.",
      pros: [
        "Strong Python and Node.js fundamentals",
        "Excellent communication and teamwork abilities",
        "Quick learner with growth mindset",
        "Previous startup experience shows adaptability",
      ],
      cons: [
        "Limited experience with microservices at scale",
        "No exposure to Kubernetes or container orchestration",
        "May need ramp-up time on complex architectures",
      ],
    },
    transcript: [
      {
        role: "ai",
        message: "Welcome Marcus! Let's discuss your backend development experience.",
        timestamp: "2:00 PM",
      },
      {
        role: "candidate",
        message: "Thanks! I have 4 years of experience primarily with Python and Node.js.",
        timestamp: "2:01 PM",
      },
    ],
  },
  {
    id: "3",
    name: "Emily Watson",
    email: "emily.watson@email.com",
    appliedRole: "Product Designer",
    seniority: "Senior",
    technicalScore: 88,
    behavioralScore: 94,
    culturalFitScore: 91,
    overallScore: 91,
    status: "Hired",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/emilywatson",
    appliedDate: "2024-01-10",
    aiSummary: {
      recommendation:
        "Highly Recommended. Emily is an exceptional designer with a rare combination of strategic thinking and hands-on execution skills.",
      pros: [
        "Award-winning portfolio with measurable business impact",
        "Strong user research and data-driven design approach",
        "Experience with design systems at scale",
        "Excellent stakeholder management skills",
      ],
      cons: ["Prefers hybrid work, may need accommodation", "High demand candidate, competitive offer needed"],
    },
    transcript: [],
  },
  {
    id: "4",
    name: "James Kim",
    email: "james.kim@email.com",
    appliedRole: "DevOps Engineer",
    seniority: "Junior",
    technicalScore: 65,
    behavioralScore: 72,
    culturalFitScore: 78,
    overallScore: 71,
    status: "Pending",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/jameskim",
    appliedDate: "2024-01-20",
    aiSummary: {
      recommendation: "Consider for junior role. James shows promise but needs significant mentorship and training.",
      pros: [
        "Strong foundational knowledge of Linux systems",
        "Eager to learn and shows initiative",
        "Good cultural fit with team dynamics",
      ],
      cons: [
        "Limited hands-on production experience",
        "No cloud platform certifications",
        "May struggle with on-call responsibilities initially",
      ],
    },
    transcript: [],
  },
  {
    id: "5",
    name: "Aisha Patel",
    email: "aisha.patel@email.com",
    appliedRole: "Data Scientist",
    seniority: "Mid",
    technicalScore: 85,
    behavioralScore: 79,
    culturalFitScore: 83,
    overallScore: 82,
    status: "Interviewing",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/aishapatel",
    appliedDate: "2024-01-17",
    aiSummary: {
      recommendation:
        "Recommended. Aisha has solid ML fundamentals and good business acumen. Strong candidate for data science roles requiring cross-functional collaboration.",
      pros: [
        "Strong ML/AI background with published research",
        "Experience translating business problems to technical solutions",
        "Proficient in Python, TensorFlow, and PyTorch",
      ],
      cons: [
        "Less experience with production ML systems",
        "Communication style may need adjustment for non-technical stakeholders",
      ],
    },
    transcript: [],
  },
  {
    id: "6",
    name: "David Thompson",
    email: "david.t@email.com",
    appliedRole: "Engineering Manager",
    seniority: "Senior",
    technicalScore: 76,
    behavioralScore: 92,
    culturalFitScore: 89,
    overallScore: 86,
    status: "Interviewing",
    cvUrl: "#",
    linkedinUrl: "https://linkedin.com/in/davidthompson",
    appliedDate: "2024-01-12",
    aiSummary: {
      recommendation:
        "Strongly Recommended for management track. David excels in leadership and team building, with sufficient technical depth for oversight roles.",
      pros: [
        "Exceptional people management skills",
        "Track record of building high-performing teams",
        "Strong technical foundation adequate for EM role",
        "Experience scaling teams from 3 to 20+ engineers",
      ],
      cons: ["Technical skills may be dated for hands-on contributions", "Previous companies were in different domain"],
    },
    transcript: [],
  },
]

export const mockJobs: Job[] = [
  {
    id: "1",
    title: "Senior Frontend Engineer",
    department: "Engineering",
    location: "Remote",
    status: "Open",
    applicants: 24,
  },
  {
    id: "2",
    title: "Backend Engineer",
    department: "Engineering",
    location: "San Francisco",
    status: "Open",
    applicants: 18,
  },
  { id: "3", title: "Product Designer", department: "Design", location: "New York", status: "Closed", applicants: 12 },
  {
    id: "4",
    title: "DevOps Engineer",
    department: "Infrastructure",
    location: "Remote",
    status: "Open",
    applicants: 8,
  },
  { id: "5", title: "Data Scientist", department: "Data", location: "Remote", status: "Open", applicants: 15 },
]
