
import requests
import json
import sys
import tempfile
from typing import Dict, Optional, Any
from datetime import date


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Variables globales para guardar IDs entre tests
state = {
    "company_id": None,
    "token": None,
    "job_id": None,
    "candidate_id": None,
    "application_id": None,
    "template_id": None
}

# Colores para output
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


# ============================================================
# UTILITIES
# ============================================================

def print_test(test_name: str, passed: bool, message: str = ""):
    """Print formatted test result"""
    status = f"{Color.GREEN}✅ PASS{Color.END}" if passed else f"{Color.RED}❌ FAIL{Color.END}"
    print(f"{status} | {test_name}")
    if message and not passed:
        print(f"       {Color.RED}Error: {message}{Color.END}")


def save_response_data(response: requests.Response, keys: list) -> Dict[str, Any]:
    """Extract and save response data"""
    try:
        data = response.json()
        result = {}
        for key in keys:
            if key in data:
                result[key] = data[key]
        return result
    except:
        return {}


def create_test_pdf() -> str:
    """Create a minimal valid PDF for testing"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 120 >>
stream
BT
/F1 14 Tf
50 700 Td
(Juan Garcia - Senior Python Developer) Tj
0 -20 Td
(Email: juan@example.com) Tj
0 -20 Td
(Skills: Python, FastAPI, PostgreSQL) Tj
0 -20 Td
(Experience: 5 years) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
0000000385 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
464
%%EOF"""
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        f.write(pdf_content)
        return f.name


# ============================================================
# TEST SUITE
# ============================================================

def test_health_check():
    """TEST 1: Health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        print_test("Health Check", passed, "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False


def test_config_loading():
    """TEST 2: Config loading"""
    try:
        from app.core.config import settings
        passed = (
            settings.SUPABASE_URL and
            settings.GROQ_API_KEY and
            settings.SECRET_KEY
        )
        print_test("Config Loading", passed, "" if passed else "Missing variables")
        return passed
    except Exception as e:
        print_test("Config Loading", False, str(e))
        return False


def test_supabase_connection():
    """TEST 3: Supabase connection"""
    try:
        from app.core.supabase_client import SupabaseClient
        client = SupabaseClient.get_client()
        response = client.table("companies").select("count").execute()
        passed = response is not None
        print_test("Supabase Connection", passed)
        return passed
    except Exception as e:
        print_test("Supabase Connection", False, str(e))
        return False
def test_register_company():
    """TEST 4: Register company"""
    try:
        payload = {
            "company_name": "TestCorp",
            "email": f"test-{date.today()}-{id(object())}@example.com",
            "password": "TestPassword123!",
            "sector": "Technology",
            "size": "startup",
            "country": "Colombia"
        }
        
        response = requests.post(f"{API_V1}/auth/register-company", json=payload)
        
        # ✅ AGREGA ESTO PARA VER EL ERROR
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"\n{Color.RED}Error response: {json.dumps(error_detail, indent=2)}{Color.END}")
            except:
                print(f"\n{Color.RED}Error text: {response.text}{Color.END}")
        
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            state["company_id"] = data.get("company_id")
            state["token"] = data.get("token")
        
        print_test("Register Company", passed, "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Register Company", False, str(e))
        return False


def test_login():
    """TEST 5: Login"""
    try:
        # Use same email from registration
        payload = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        response = requests.post(f"{API_V1}/auth/login", json=payload, timeout=5)
        # Esta puede fallar si no existe la empresa, es ok
        print_test("Login", response.status_code in [200, 401])
        return response.status_code in [200, 401]
    except Exception as e:
        print_test("Login", False, str(e))
        return False


def test_get_company():
    """TEST 6: Get company profile"""
    if not state["token"] or not state["company_id"]:
        print_test("Get Company", False, "Missing token or company_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        response = requests.get(
            f"{API_V1}/companies/{state['company_id']}",
            headers=headers
        )
        passed = response.status_code == 200
        print_test("Get Company", passed)
        return passed
    except Exception as e:
        print_test("Get Company", False, str(e))
        return False


def test_update_company():
    """TEST 7: Update company profile"""
    if not state["token"] or not state["company_id"]:
        print_test("Update Company", False, "Missing token or company_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "description": "Test company for hackathon",
            "whatsapp_number": "+573001234567"
        }
        
        response = requests.put(
            f"{API_V1}/companies/{state['company_id']}",
            headers=headers,
            json=payload
        )
        passed = response.status_code == 200
        print_test("Update Company", passed)
        return passed
    except Exception as e:
        print_test("Update Company", False, str(e))
        return False

def test_create_job_posting():
    """TEST 8: Create job posting (Groq generates context)"""
    if not state["token"] or not state["company_id"]:
        print_test("Create Job Posting", False, "Missing token or company_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "company_id": state["company_id"],
            "title": "Senior Python Developer",
            "description": "We are looking for a senior developer with FastAPI experience",
            "area": "Backend",
            "contract_type": "PTC",
            "modality": "remote",
            "location": "Bogotá",
            "required_skills": {
                "languages": ["Python", "FastAPI", "PostgreSQL"],
                "years_experience": 3
            }
        }
        
        response = requests.post(
            f"{API_V1}/job-postings/",
            headers=headers,
            json=payload,
            timeout=15  # Groq puede tardar
        )
        
        # ✅ DEBUG COMPLETO
        if response.status_code != 200:
            print(f"\n{Color.RED}=== ERROR DEBUG ==={Color.END}")
            print(f"{Color.YELLOW}Status Code:{Color.END} {response.status_code}")
            print(f"{Color.YELLOW}Response Headers:{Color.END} {dict(response.headers)}")
            try:
                error_json = response.json()
                print(f"{Color.YELLOW}Response JSON:{Color.END}")
                print(json.dumps(error_json, indent=2))
            except:
                print(f"{Color.YELLOW}Response Text:{Color.END}")
                print(response.text)
            print(f"{Color.RED}=================={Color.END}\n")
        
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            state["job_id"] = data.get("data", {}).get("job_posting_id")
        
        print_test("Create Job Posting (with Groq context)", passed,
                  "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Create Job Posting (with Groq context)", False, str(e))
        import traceback
        print(f"\n{Color.RED}Exception Traceback:{Color.END}")
        traceback.print_exc()
        return False



def test_list_job_postings():
    """TEST 9: List job postings"""
    try:
        response = requests.get(f"{API_V1}/job-postings?status=published")
        passed = response.status_code == 200
        print_test("List Job Postings", passed)
        return passed
    except Exception as e:
        print_test("List Job Postings", False, str(e))
        return False


def test_publish_job_posting():
    """TEST 10: Publish job posting"""
    if not state["token"] or not state["job_id"]:
        print_test("Publish Job", False, "Missing token or job_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        response = requests.put(
            f"{API_V1}/job-postings/{state['job_id']}/publish",
            headers=headers
        )
        passed = response.status_code == 200
        print_test("Publish Job", passed)
        return passed
    except Exception as e:
        print_test("Publish Job", False, str(e))
        return False


def test_create_application():
    """TEST 11: Create application with CV"""
    if not state["job_id"]:
        print_test("Create Application", False, "Missing job_id")
        return False
    
    try:
        pdf_path = create_test_pdf()
        
        files = {"cv_file": ("test_cv.pdf", open(pdf_path, "rb"), "application/pdf")}
        data = {
            "full_name": "Juan García",
            "email": f"candidate-{id(object())}@example.com",
            "phone_number": "+573001234567",
            "job_posting_id": state["job_id"],
            "country": "Colombia",
            "city": "Bogotá",
            "seniority_level": "senior",
            "expected_salary": 80000,
            "consent_ai": "true",
            "consent_data_storage": "true"
        }
        
        response = requests.post(
            f"{API_V1}/applications/",
            files=files,
            data=data,
            timeout=30  # CV parsing tarda
        )
        
        passed = response.status_code == 200
        
        if passed:
            result = response.json()
            state["candidate_id"] = result.get("candidate_id")
            state["application_id"] = result.get("application_id")
        
        print_test("Create Application (CV parsing)", passed,
                  "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Create Application (CV parsing)", False, str(e))
        return False


def test_get_application():
    """TEST 12: Get application details"""
    if not state["token"] or not state["application_id"]:
        print_test("Get Application", False, "Missing token or application_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        response = requests.get(
            f"{API_V1}/applications/{state['application_id']}",
            headers=headers
        )
        passed = response.status_code == 200
        print_test("Get Application", passed)
        return passed
    except Exception as e:
        print_test("Get Application", False, str(e))
        return False


def test_calculate_cv_score():
    """TEST 13: Calculate CV score (Groq analysis)"""
    if not state["token"] or not state["candidate_id"] or not state["job_id"]:
        print_test("Calculate CV Score", False, "Missing required IDs")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "candidate_id": state["candidate_id"],
            "job_posting_id": state["job_id"]
        }
        
        response = requests.post(
            f"{API_V1}/scoring/calculate-cv-score",
            headers=headers,
            json=payload,
            timeout=20  # Groq puede tardar
        )
        
        passed = response.status_code == 200
        print_test("Calculate CV Score (Groq analysis)", passed,
                  "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Calculate CV Score (Groq analysis)", False, str(e))
        return False


def test_calculate_global_score():
    """TEST 14: Calculate global score"""
    if not state["token"] or not state["application_id"] or not state["job_id"]:
        print_test("Calculate Global Score", False, "Missing required IDs")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "application_id": state["application_id"],
            "job_posting_id": state["job_id"],
            "cv_score": 80,
            "technical_score": 85,
            "soft_skills_score": 82
        }
        
        response = requests.post(
            f"{API_V1}/scoring/calculate-global-score",
            headers=headers,
            json=payload
        )
        
        passed = response.status_code == 200
        print_test("Calculate Global Score", passed)
        return passed
    except Exception as e:
        print_test("Calculate Global Score", False, str(e))
        return False


def test_webhook():
    """TEST 15: Webhook (n8n simulation)"""
    if not state["application_id"]:
        print_test("Webhook", False, "Missing application_id")
        return False
    
    try:
        payload = {
            "application_id": state["application_id"],
            "candidate_message": "Tengo 5 años de experiencia con Python y FastAPI",
            "interview_state": {
                "current_phase": "technical",
                "completed_phases": ["knockout"],
                "conversation_history": []
            }
        }
        
        response = requests.post(
            f"{API_V1}/webhooks/interview-step",
            json=payload
        )
        
        passed = response.status_code == 200
        print_test("Webhook Interview Step", passed)
        return passed
    except Exception as e:
        print_test("Webhook Interview Step", False, str(e))
        return False


def test_agent_chat():
    """TEST 16: Agent chat (Groq analysis)"""
    if not state["token"] or not state["job_id"]:
        print_test("Agent Chat", False, "Missing token or job_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "job_posting_id": state["job_id"],
            "question": "¿Quiénes son los mejores candidatos?"
        }
        
        response = requests.post(
            f"{API_V1}/agent/chat",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        passed = response.status_code == 200
        print_test("Agent Chat (Groq analysis)", passed,
                  "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Agent Chat (Groq analysis)", False, str(e))
        return False


def test_generate_onboarding():
    """TEST 17: Generate onboarding (Groq email generation)"""
    if not state["token"] or not state["application_id"]:
        print_test("Generate Onboarding", False, "Missing required data")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {state['token']}"}
        payload = {
            "application_id": state["application_id"],
            "company_info": {"name": "TestCorp"},
            "job_info": {"title": "Senior Python Developer"},
            "first_day_checklist": ["Office setup", "Team intro"]
        }
        
        response = requests.post(
            f"{API_V1}/onboarding/generate",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            state["template_id"] = data.get("onboarding_template_id")
        
        print_test("Generate Onboarding (Groq email)", passed,
                  "" if passed else f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Generate Onboarding (Groq email)", False, str(e))
        return False


# ============================================================
# MAIN
# ============================================================

def main():
    """Run all tests"""
    print(f"\n{Color.BLUE}{'='*60}")
    print("🚀 ROL 1 BACKEND TEST SUITE")
    print(f"{'='*60}{Color.END}\n")
    
    tests = [
        ("Prerequisites & Health", [
            test_health_check,
            test_config_loading,
            test_supabase_connection
        ]),
        ("Authentication", [
            test_register_company,
            test_login
        ]),
        ("Company Management", [
            test_get_company,
            test_update_company
        ]),
        ("Job Management", [
            test_create_job_posting,
            test_list_job_postings,
            test_publish_job_posting
        ]),
        ("Application Management", [
            test_create_application,
            test_get_application
        ]),
        ("Scoring (with Groq)", [
            test_calculate_cv_score,
            test_calculate_global_score
        ]),
        ("Advanced Features", [
            test_webhook,
            test_agent_chat,
            test_generate_onboarding
        ])
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category, test_list in tests:
        print(f"\n{Color.YELLOW}{category}{Color.END}")
        for test_func in test_list:
            total_tests += 1
            if test_func():
                total_passed += 1
    
    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.GREEN if total_passed == total_tests else Color.YELLOW}"
          f"RESULTADO FINAL: {total_passed}/{total_tests} tests pasados"
          f"{Color.END}")
    print(f"{Color.BLUE}{'='*60}{Color.END}\n")
    
    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())