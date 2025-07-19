import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from typing import Dict, Any, List
import json

from app.main import app
from app.core.database import Base, get_db
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.candidate import Candidate
from app.models.match import Match
from app.services.resume_parser import ResumeParser
from app.services.job_scraper import JobScraper
from app.services.nlp_processor import NLPProcessor
from app.services.matching_engine import MatchingEngine
from app.core.security import SecurityValidator, SecurityMiddleware
from app.core.performance import PerformanceMonitor


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Test client fixture"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Database session fixture"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestResumeParser:
    """Test suite for resume parsing functionality"""
    
    def setup_method(self):
        self.parser = ResumeParser()
    
    def test_pdf_parsing(self):
        """Test PDF resume parsing"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name
        
        try:
            with patch('app.services.resume_parser.pdfplumber.open') as mock_pdf:
                mock_page = Mock()
                mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\nPython, JavaScript"
                mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
                
                result = self.parser.parse_pdf(tmp_path)
                
                assert result['success'] == True
                assert 'John Doe' in result['text']
                assert 'Software Engineer' in result['text']
        finally:
            os.unlink(tmp_path)
    
    def test_docx_parsing(self):
        """Test DOCX resume parsing"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"Mock DOCX content")
            tmp_path = tmp.name
        
        try:
            with patch('app.services.resume_parser.Document') as mock_doc:
                mock_para = Mock()
                mock_para.text = "Jane Smith\nData Scientist\nPython, R, SQL"
                mock_doc.return_value.paragraphs = [mock_para]
                
                result = self.parser.parse_docx(tmp_path)
                
                assert result['success'] == True
                assert 'Jane Smith' in result['text']
                assert 'Data Scientist' in result['text']
        finally:
            os.unlink(tmp_path)
    
    def test_section_identification(self):
        """Test resume section identification"""
        text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        
        EXPERIENCE
        Software Engineer at Tech Corp
        2020-2023
        
        EDUCATION
        BS Computer Science
        University of Tech
        2016-2020
        
        SKILLS
        Python, JavaScript, SQL
        """
        
        sections = self.parser.identify_sections(text)
        
        assert 'contact' in sections
        assert 'experience' in sections
        assert 'education' in sections
        assert 'skills' in sections
        assert 'john.doe@email.com' in sections['contact']
        assert 'Software Engineer' in sections['experience']
        assert 'BS Computer Science' in sections['education']
        assert 'Python' in sections['skills']
    
    def test_contact_extraction(self):
        """Test contact information extraction"""
        text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        linkedin.com/in/johndoe
        """
        
        contact = self.parser.extract_contact_info(text)
        
        assert contact['name'] == 'John Doe'
        assert contact['email'] == 'john.doe@email.com'
        assert contact['phone'] == '(555) 123-4567'
        assert 'linkedin.com/in/johndoe' in contact['linkedin']
    
    def test_skills_extraction(self):
        """Test skills extraction"""
        text = """
        SKILLS
        Programming Languages: Python, JavaScript, Java, C++
        Databases: MySQL, PostgreSQL, MongoDB
        Frameworks: React, Django, Flask
        Tools: Git, Docker, Jenkins
        """
        
        skills = self.parser.extract_skills(text)
        
        assert 'python' in [s.lower() for s in skills]
        assert 'javascript' in [s.lower() for s in skills]
        assert 'mysql' in [s.lower() for s in skills]
        assert 'react' in [s.lower() for s in skills]
        assert 'docker' in [s.lower() for s in skills]


class TestJobScraper:
    """Test suite for job scraping functionality"""
    
    def setup_method(self):
        self.scraper = JobScraper()
    
    def test_job_board_scraping(self):
        """Test job board scraping"""
        with patch('app.services.job_scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <div class="job-title">Software Engineer</div>
                <div class="company">Tech Corp</div>
                <div class="job-description">
                    Looking for a software engineer with Python experience
                </div>
            </html>
            """
            mock_get.return_value = mock_response
            
            jobs = self.scraper.scrape_jobs("https://example.com/jobs")
            
            assert len(jobs) > 0
            assert any('Software Engineer' in job.get('title', '') for job in jobs)
    
    def test_job_deduplication(self):
        """Test job deduplication"""
        jobs = [
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'description': 'Python developer position'
            },
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'description': 'Python developer position'
            },
            {
                'title': 'Data Scientist',
                'company': 'Data Corp',
                'description': 'ML engineer position'
            }
        ]
        
        deduplicated = self.scraper.deduplicate_jobs(jobs)
        
        assert len(deduplicated) == 2
    
    def test_job_parsing(self):
        """Test job description parsing"""
        html = """
        <div class="job-posting">
            <h1>Senior Software Engineer</h1>
            <div class="company-name">Tech Innovations Inc</div>
            <div class="job-location">San Francisco, CA</div>
            <div class="job-description">
                We are looking for a senior software engineer with:
                - 5+ years of experience
                - Python programming skills
                - Database knowledge
                - API development experience
            </div>
        </div>
        """
        
        job_data = self.scraper.parse_job_posting(html)
        
        assert job_data['title'] == 'Senior Software Engineer'
        assert job_data['company'] == 'Tech Innovations Inc'
        assert job_data['location'] == 'San Francisco, CA'
        assert 'Python' in job_data['description']


class TestNLPProcessor:
    """Test suite for NLP processing functionality"""
    
    def setup_method(self):
        self.processor = NLPProcessor()
    
    def test_text_preprocessing(self):
        """Test text preprocessing"""
        text = "This is a SAMPLE text with SPECIAL characters!!! And numbers123."
        
        processed = self.processor.preprocess_text(text)
        
        assert processed.islower()
        assert 'sample' in processed
        assert 'special' in processed
        assert '!!!' not in processed
    
    def test_skill_extraction(self):
        """Test skill extraction using NLP"""
        text = """
        I have experience with Python programming, machine learning,
        and database management. I've worked with React, Node.js,
        and AWS cloud services.
        """
        
        skills = self.processor.extract_skills_nlp(text)
        
        assert 'python' in [s.lower() for s in skills]
        assert 'machine learning' in [s.lower() for s in skills]
        assert 'react' in [s.lower() for s in skills]
        assert 'aws' in [s.lower() for s in skills]
    
    def test_text_similarity(self):
        """Test text similarity calculation"""
        text1 = "Python software engineer with machine learning experience"
        text2 = "ML engineer with Python programming skills"
        text3 = "Marketing manager with communication skills"
        
        similarity_high = self.processor.calculate_similarity(text1, text2)
        similarity_low = self.processor.calculate_similarity(text1, text3)
        
        assert similarity_high > similarity_low
        assert similarity_high > 0.5
        assert similarity_low < 0.3
    
    def test_entity_recognition(self):
        """Test named entity recognition"""
        text = """
        John Doe worked at Google for 3 years as a Software Engineer.
        He graduated from Stanford University with a Computer Science degree.
        """
        
        entities = self.processor.extract_entities(text)
        
        person_entities = [e for e in entities if e['label'] == 'PERSON']
        org_entities = [e for e in entities if e['label'] == 'ORG']
        
        assert len(person_entities) > 0
        assert len(org_entities) > 0
        assert any('John Doe' in e['text'] for e in person_entities)
        assert any('Google' in e['text'] for e in org_entities)


class TestMatchingEngine:
    """Test suite for matching engine functionality"""
    
    def setup_method(self):
        self.engine = MatchingEngine()
    
    def test_skill_matching(self):
        """Test skill-based matching"""
        resume_skills = ['Python', 'JavaScript', 'React', 'SQL']
        job_skills = ['Python', 'React', 'Node.js', 'MongoDB']
        
        score = self.engine.calculate_skill_match(resume_skills, job_skills)
        
        assert score > 0.0
        assert score <= 1.0
    
    def test_experience_matching(self):
        """Test experience-based matching"""
        resume_exp = {
            'years': 5,
            'roles': ['Software Engineer', 'Full Stack Developer'],
            'companies': ['Tech Corp', 'Startup Inc']
        }
        
        job_req = {
            'min_years': 3,
            'preferred_roles': ['Software Engineer', 'Backend Developer'],
            'industry': 'Technology'
        }
        
        score = self.engine.calculate_experience_match(resume_exp, job_req)
        
        assert score > 0.0
        assert score <= 1.0
    
    def test_education_matching(self):
        """Test education-based matching"""
        resume_edu = {
            'degree': 'Bachelor of Science',
            'field': 'Computer Science',
            'university': 'Tech University'
        }
        
        job_req = {
            'required_degree': 'Bachelor',
            'preferred_fields': ['Computer Science', 'Software Engineering']
        }
        
        score = self.engine.calculate_education_match(resume_edu, job_req)
        
        assert score > 0.0
        assert score <= 1.0
    
    def test_comprehensive_matching(self):
        """Test comprehensive resume-job matching"""
        resume_data = {
            'skills': ['Python', 'JavaScript', 'React', 'SQL'],
            'experience': {
                'years': 5,
                'roles': ['Software Engineer'],
                'companies': ['Tech Corp']
            },
            'education': {
                'degree': 'Bachelor of Science',
                'field': 'Computer Science'
            }
        }
        
        job_data = {
            'skills': ['Python', 'React', 'Node.js'],
            'requirements': {
                'min_years': 3,
                'preferred_roles': ['Software Engineer'],
                'required_degree': 'Bachelor'
            }
        }
        
        match_result = self.engine.match_resume_to_job(resume_data, job_data)
        
        assert 'overall_score' in match_result
        assert 'skill_score' in match_result
        assert 'experience_score' in match_result
        assert 'education_score' in match_result
        assert match_result['overall_score'] > 0.0
        assert match_result['overall_score'] <= 1.0


class TestSecurityValidator:
    """Test suite for security validation"""
    
    def setup_method(self):
        self.validator = SecurityValidator()
    
    def test_password_validation(self):
        """Test password strength validation"""
        weak_password = "123456"
        medium_password = "Password123"
        strong_password = "StrongP@ssw0rd123"
        
        weak_result = self.validator.validate_password(weak_password)
        medium_result = self.validator.validate_password(medium_password)
        strong_result = self.validator.validate_password(strong_password)
        
        assert weak_result['valid'] == False
        assert medium_result['valid'] == True
        assert strong_result['valid'] == True
        assert strong_result['strength'] == 'strong'
    
    def test_email_validation(self):
        """Test email format validation"""
        valid_emails = [
            'user@example.com',
            'test.email+tag@domain.co.uk',
            'user123@test-domain.com'
        ]
        
        invalid_emails = [
            'invalid-email',
            'user@',
            '@domain.com',
            'user@domain',
            'user space@domain.com'
        ]
        
        for email in valid_emails:
            assert self.validator.validate_email(email) == True
        
        for email in invalid_emails:
            assert self.validator.validate_email(email) == False
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        safe_inputs = [
            "John Doe",
            "Software Engineer",
            "user@example.com"
        ]
        
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT * FROM passwords"
        ]
        
        for input_text in safe_inputs:
            assert self.validator.detect_sql_injection(input_text) == False
        
        for input_text in malicious_inputs:
            assert self.validator.detect_sql_injection(input_text) == True
    
    def test_xss_detection(self):
        """Test XSS detection"""
        safe_inputs = [
            "Normal text content",
            "Email: user@example.com",
            "Skills: Python, JavaScript"
        ]
        
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for input_text in safe_inputs:
            assert self.validator.detect_xss(input_text) == False
        
        for input_text in malicious_inputs:
            assert self.validator.detect_xss(input_text) == True
    
    def test_file_upload_validation(self):
        """Test file upload validation"""
        # Mock PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj"
        
        result = self.validator.validate_file_upload(pdf_content, "resume.pdf")
        
        assert result['valid'] == True
        assert result['mime_type'] == 'application/pdf'
        
        # Mock malicious file
        malicious_content = b"MZ\x90\x00\x03\x00\x00\x00"  # PE executable signature
        
        result = self.validator.validate_file_upload(malicious_content, "malware.exe")
        
        assert result['valid'] == False
        assert "not allowed" in " ".join(result['issues'])


class TestPerformanceMonitor:
    """Test suite for performance monitoring"""
    
    def setup_method(self):
        self.monitor = PerformanceMonitor()
    
    def test_system_metrics_collection(self):
        """Test system metrics collection"""
        self.monitor.collect_system_metrics()
        
        assert 'cpu_percent' in self.monitor.system_metrics
        assert 'memory_percent' in self.monitor.system_metrics
        assert 'uptime' in self.monitor.system_metrics
        assert isinstance(self.monitor.system_metrics['cpu_percent'], (int, float))
        assert isinstance(self.monitor.system_metrics['memory_percent'], (int, float))
    
    def test_performance_report(self):
        """Test performance report generation"""
        self.monitor.collect_system_metrics()
        report = self.monitor.get_performance_report()
        
        assert 'timestamp' in report
        assert 'system_metrics' in report
        assert 'uptime' in report
        assert isinstance(report['uptime'], (int, float))


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_resume_upload(self, client):
        """Test resume upload endpoint"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, "rb") as file:
                response = client.post(
                    "/api/v1/resumes/upload",
                    files={"file": ("resume.pdf", file, "application/pdf")}
                )
                
            assert response.status_code in [200, 201]
        finally:
            os.unlink(tmp_path)
    
    def test_job_creation(self, client):
        """Test job creation endpoint"""
        job_data = {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "description": "Looking for a Python developer",
            "requirements": {
                "skills": ["Python", "JavaScript"],
                "experience": "3+ years"
            }
        }
        
        response = client.post("/api/v1/jobs/", json=job_data)
        assert response.status_code in [200, 201]
    
    def test_matching_endpoint(self, client):
        """Test matching endpoint"""
        # First create a resume and job
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, "rb") as file:
                resume_response = client.post(
                    "/api/v1/resumes/upload",
                    files={"file": ("resume.pdf", file, "application/pdf")}
                )
            
            job_data = {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Python developer position"
            }
            
            job_response = client.post("/api/v1/jobs/", json=job_data)
            
            if resume_response.status_code in [200, 201] and job_response.status_code in [200, 201]:
                resume_id = resume_response.json().get("id")
                job_id = job_response.json().get("id")
                
                if resume_id and job_id:
                    match_response = client.post(
                        f"/api/v1/matching/match/{resume_id}/{job_id}"
                    )
                    
                    assert match_response.status_code in [200, 201]
        finally:
            os.unlink(tmp_path)


class TestIntegrationWorkflows:
    """Test suite for integration workflows"""
    
    def test_end_to_end_workflow(self, client, db_session):
        """Test complete end-to-end workflow"""
        # 1. Upload resume
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"Mock PDF content")
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, "rb") as file:
                resume_response = client.post(
                    "/api/v1/resumes/upload",
                    files={"file": ("resume.pdf", file, "application/pdf")}
                )
            
            # 2. Create job
            job_data = {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Python developer position"
            }
            
            job_response = client.post("/api/v1/jobs/", json=job_data)
            
            # 3. Perform matching
            if resume_response.status_code in [200, 201] and job_response.status_code in [200, 201]:
                resume_id = resume_response.json().get("id")
                job_id = job_response.json().get("id")
                
                if resume_id and job_id:
                    match_response = client.post(
                        f"/api/v1/matching/match/{resume_id}/{job_id}"
                    )
                    
                    assert match_response.status_code in [200, 201]
                    
                    # 4. Get match results
                    results_response = client.get(f"/api/v1/matching/results/{resume_id}")
                    assert results_response.status_code == 200
        finally:
            os.unlink(tmp_path)
    
    def test_bulk_processing_workflow(self, client):
        """Test bulk processing workflow"""
        # Create multiple resumes and jobs
        resume_ids = []
        job_ids = []
        
        # Upload multiple resumes
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(f"Mock PDF content {i}".encode())
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, "rb") as file:
                    response = client.post(
                        "/api/v1/resumes/upload",
                        files={"file": (f"resume_{i}.pdf", file, "application/pdf")}
                    )
                    
                if response.status_code in [200, 201]:
                    resume_ids.append(response.json().get("id"))
            finally:
                os.unlink(tmp_path)
        
        # Create multiple jobs
        for i in range(2):
            job_data = {
                "title": f"Position {i}",
                "company": f"Company {i}",
                "description": f"Job description {i}"
            }
            
            response = client.post("/api/v1/jobs/", json=job_data)
            if response.status_code in [200, 201]:
                job_ids.append(response.json().get("id"))
        
        # Perform bulk matching
        if resume_ids and job_ids:
            bulk_data = {
                "resume_ids": resume_ids,
                "job_ids": job_ids
            }
            
            response = client.post("/api/v1/matching/bulk", json=bulk_data)
            assert response.status_code in [200, 201, 202]  # 202 for async processing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
