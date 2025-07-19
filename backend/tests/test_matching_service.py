import pytest
from datetime import datetime
from app.services.matching_service import MatchingService, MatchResult, MatchScore
from app.services.resume_parser import ParsedResume, ContactInfo, WorkExperience, Education
from app.services.job_scraper import JobDescription


class TestMatchingService:
    """Test suite for the MatchingService class"""
    
    @pytest.fixture(scope='class')
    def matching_service(self):
        """Create matching service instance for testing"""
        return MatchingService()
    
    @pytest.fixture
    def sample_resume(self):
        """Create sample resume for testing"""
        contact_info = ContactInfo(
            full_name="John Doe",
            email="john.doe@email.com",
            phone="123-456-7890"
        )
        
        work_experience = [
            WorkExperience(
                title="Senior Software Engineer",
                company="Tech Corp",
                start_date="2020",
                end_date="2023",
                description="Developed web applications using Python and React"
            )
        ]
        
        education = [
            Education(
                degree="Bachelor of Science in Computer Science",
                institution="University of Technology",
                graduation_date="2019"
            )
        ]
        
        skills = {
            'skills': [
                {'skill': 'python', 'confidence': 0.9, 'category': 'technical'},
                {'skill': 'react', 'confidence': 0.8, 'category': 'technical'},
                {'skill': 'javascript', 'confidence': 0.8, 'category': 'technical'},
                {'skill': 'leadership', 'confidence': 0.7, 'category': 'soft'}
            ]
        }
        
        return ParsedResume(
            contact_info=contact_info,
            work_experience=work_experience,
            education=education,
            skills=skills,
            summary="Experienced software engineer with 3+ years in web development",
            processing_metadata={'total_years_experience': 3}
        )
    
    @pytest.fixture
    def sample_job(self):
        """Create sample job description for testing"""
        return JobDescription(
            title="Software Engineer",
            company="Startup Inc",
            description="We are looking for a skilled software engineer to join our team. "
                       "The ideal candidate should have experience with Python and React.",
            requirements="Bachelor's degree in Computer Science or related field. "
                        "2+ years of experience in software development. "
                        "Strong skills in Python, React, and JavaScript.",
            skills=['python', 'react', 'javascript', 'sql'],
            location="San Francisco, CA",
            remote_ok=True,
            job_id="job123"
        )
    
    def test_skills_score_calculation(self, matching_service, sample_resume, sample_job):
        """Test skills score calculation"""
        skills_score, details = matching_service.calculate_skills_score(sample_resume, sample_job)
        
        assert 0.0 <= skills_score <= 1.0, "Skills score should be between 0 and 1"
        assert isinstance(details, dict), "Details should be a dictionary"
        assert 'matched_skills' in details, "Details should include matched skills"
        assert 'missing_skills' in details, "Details should include missing skills"
        
        # Should have high skills score due to matching Python, React, JavaScript
        assert skills_score > 0.7, "Should have high skills score for matching skills"
        
        # Check specific skill matches
        matched_skills = details['matched_skills']
        assert 'python' in matched_skills, "Python should be matched"
        assert 'react' in matched_skills, "React should be matched"
        assert 'javascript' in matched_skills, "JavaScript should be matched"
        
        # Check missing skills
        missing_skills = details['missing_skills']
        assert 'sql' in missing_skills, "SQL should be missing"
    
    def test_experience_score_calculation(self, matching_service, sample_resume, sample_job):
        """Test experience score calculation"""
        experience_score, details = matching_service.calculate_experience_score(sample_resume, sample_job)
        
        assert 0.0 <= experience_score <= 1.0, "Experience score should be between 0 and 1"
        assert isinstance(details, dict), "Details should be a dictionary"
        assert 'resume_years' in details, "Details should include resume years"
        assert 'job_years_required' in details, "Details should include job years required"
        
        # Should have good experience score (3 years vs 2+ required)
        assert experience_score > 0.8, "Should have high experience score"
        
        # Check specific values
        assert details['resume_years'] == 3, "Resume should have 3 years experience"
        assert details['job_years_required'] == 2, "Job should require 2 years experience"
    
    def test_education_score_calculation(self, matching_service, sample_resume, sample_job):
        """Test education score calculation"""
        education_score, details = matching_service.calculate_education_score(sample_resume, sample_job)
        
        assert 0.0 <= education_score <= 1.0, "Education score should be between 0 and 1"
        assert isinstance(details, dict), "Details should be a dictionary"
        
        # Should have good education score (Bachelor's in CS)
        assert education_score > 0.8, "Should have high education score for CS degree"
    
    def test_additional_score_calculation(self, matching_service, sample_resume, sample_job):
        """Test additional factors score calculation"""
        additional_score, details = matching_service.calculate_additional_score(sample_resume, sample_job)
        
        assert 0.0 <= additional_score <= 1.0, "Additional score should be between 0 and 1"
        assert isinstance(details, dict), "Details should be a dictionary"
        
        # Should have various factors
        assert 'certifications' in details, "Should include certifications factor"
        assert 'keywords' in details, "Should include keywords factor"
        assert 'location' in details, "Should include location factor"
        assert 'company' in details, "Should include company factor"
    
    def test_overall_match_calculation(self, matching_service, sample_resume, sample_job):
        """Test overall match score calculation"""
        match_result = matching_service.calculate_match_score(sample_resume, sample_job)
        
        assert isinstance(match_result, MatchResult), "Should return MatchResult object"
        assert isinstance(match_result.match_score, MatchScore), "Should contain MatchScore object"
        
        # Check overall score
        overall_score = match_result.match_score.overall_score
        assert 0.0 <= overall_score <= 1.0, "Overall score should be between 0 and 1"
        assert overall_score > 0.7, "Should have high overall score for good match"
        
        # Check individual scores
        assert 0.0 <= match_result.match_score.skills_score <= 1.0, "Skills score should be valid"
        assert 0.0 <= match_result.match_score.experience_score <= 1.0, "Experience score should be valid"
        assert 0.0 <= match_result.match_score.education_score <= 1.0, "Education score should be valid"
        assert 0.0 <= match_result.match_score.additional_score <= 1.0, "Additional score should be valid"
        
        # Check confidence
        assert 0.0 <= match_result.match_score.confidence <= 1.0, "Confidence should be between 0 and 1"
        
        # Check explanation
        assert isinstance(match_result.match_score.explanation, str), "Explanation should be string"
        assert len(match_result.match_score.explanation) > 0, "Explanation should not be empty"
    
    def test_match_result_to_dict(self, matching_service, sample_resume, sample_job):
        """Test match result to dictionary conversion"""
        match_result = matching_service.calculate_match_score(sample_resume, sample_job)
        result_dict = match_result.to_dict()
        
        assert isinstance(result_dict, dict), "Should return dictionary"
        
        # Check required fields
        required_fields = [
            'resume_id', 'job_id', 'overall_score', 'skills_score',
            'experience_score', 'education_score', 'additional_score',
            'confidence', 'explanation', 'matched_skills', 'missing_skills'
        ]
        
        for field in required_fields:
            assert field in result_dict, f"Field {field} should be in result dictionary"
    
    def test_no_skills_match(self, matching_service, sample_resume):
        """Test matching when job has no skills specified"""
        job_no_skills = JobDescription(
            title="Generic Position",
            company="Generic Corp",
            description="A generic position with no specific skills mentioned",
            requirements="No specific requirements",
            skills=[],
            job_id="job_no_skills"
        )
        
        match_result = matching_service.calculate_match_score(sample_resume, job_no_skills)
        
        assert match_result.match_score.overall_score > 0.0, "Should have some score even without skills"
        assert match_result.match_score.skills_score > 0.0, "Should use text similarity for skills"
    
    def test_no_experience_requirements(self, matching_service, sample_resume):
        """Test matching when job has no experience requirements"""
        job_no_exp = JobDescription(
            title="Entry Level Position",
            company="Startup Corp",
            description="Entry level position suitable for new graduates",
            requirements="Bachelor's degree required",
            skills=['python'],
            job_id="job_no_exp"
        )
        
        match_result = matching_service.calculate_match_score(sample_resume, job_no_exp)
        
        assert match_result.match_score.experience_score >= 0.8, "Should have high experience score when no requirement"
    
    def test_overqualified_candidate(self, matching_service, sample_job):
        """Test matching when candidate is overqualified"""
        # Create overqualified resume
        overqualified_resume = ParsedResume(
            contact_info=ContactInfo(full_name="Senior Developer"),
            work_experience=[
                WorkExperience(
                    title="Senior Software Engineer",
                    company="Big Tech",
                    start_date="2010",
                    end_date="2023",
                    description="10+ years of experience in Python and React"
                )
            ],
            education=[
                Education(
                    degree="Master of Science in Computer Science",
                    institution="Top University"
                )
            ],
            skills={
                'skills': [
                    {'skill': 'python', 'confidence': 0.95, 'category': 'technical'},
                    {'skill': 'react', 'confidence': 0.9, 'category': 'technical'},
                    {'skill': 'javascript', 'confidence': 0.9, 'category': 'technical'},
                    {'skill': 'sql', 'confidence': 0.8, 'category': 'technical'}
                ]
            },
            processing_metadata={'total_years_experience': 13}
        )
        
        match_result = matching_service.calculate_match_score(overqualified_resume, sample_job)
        
        assert match_result.match_score.overall_score > 0.8, "Overqualified candidate should have high score"
        assert match_result.match_score.experience_score >= 0.9, "Should have excellent experience score"
    
    def test_underqualified_candidate(self, matching_service, sample_job):
        """Test matching when candidate is underqualified"""
        underqualified_resume = ParsedResume(
            contact_info=ContactInfo(full_name="Junior Developer"),
            work_experience=[
                WorkExperience(
                    title="Junior Developer",
                    company="Small Company",
                    start_date="2023",
                    end_date="2023",
                    description="6 months of experience in Python"
                )
            ],
            education=[
                Education(
                    degree="Associate Degree in IT",
                    institution="Community College"
                )
            ],
            skills={
                'skills': [
                    {'skill': 'python', 'confidence': 0.6, 'category': 'technical'}
                ]
            },
            processing_metadata={'total_years_experience': 0.5}
        )
        
        match_result = matching_service.calculate_match_score(underqualified_resume, sample_job)
        
        assert match_result.match_score.overall_score < 0.7, "Underqualified candidate should have lower score"
        assert match_result.match_score.experience_score < 0.6, "Should have low experience score"
    
    async def test_bulk_matching(self, matching_service, sample_resume, sample_job):
        """Test bulk matching functionality"""
        # Create multiple resumes and jobs
        resumes = [sample_resume] * 2
        jobs = [sample_job] * 2
        
        results = await matching_service.bulk_match(resumes, jobs, min_score_threshold=0.5)
        
        assert len(results) == 4, "Should have 4 match results (2 resumes x 2 jobs)"
        assert all(isinstance(result, MatchResult) for result in results), "All results should be MatchResult objects"
        assert all(result.match_score.overall_score >= 0.5 for result in results), "All results should meet threshold"
        
        # Results should be sorted by score (descending)
        scores = [result.match_score.overall_score for result in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score"
    
    def test_rank_candidates(self, matching_service, sample_resume, sample_job):
        """Test candidate ranking functionality"""
        # Create match results
        match_results = [
            MatchResult(
                resume_id="resume1",
                job_id="job123",
                match_score=MatchScore(
                    overall_score=0.9,
                    skills_score=0.8,
                    experience_score=0.9,
                    education_score=0.8,
                    additional_score=0.7,
                    confidence=0.8,
                    explanation="Excellent match"
                )
            ),
            MatchResult(
                resume_id="resume2",
                job_id="job123",
                match_score=MatchScore(
                    overall_score=0.7,
                    skills_score=0.6,
                    experience_score=0.7,
                    education_score=0.8,
                    additional_score=0.6,
                    confidence=0.7,
                    explanation="Good match"
                )
            )
        ]
        
        ranked_candidates = matching_service.rank_candidates(match_results, "job123")
        
        assert len(ranked_candidates) == 2, "Should return 2 ranked candidates"
        assert ranked_candidates[0].rank == 1, "First candidate should have rank 1"
        assert ranked_candidates[1].rank == 2, "Second candidate should have rank 2"
        assert ranked_candidates[0].percentile > ranked_candidates[1].percentile, "First candidate should have higher percentile"
    
    def test_explain_match(self, matching_service, sample_resume, sample_job):
        """Test match explanation functionality"""
        match_result = matching_service.calculate_match_score(sample_resume, sample_job)
        explanation = matching_service.explain_match(match_result)
        
        assert isinstance(explanation, dict), "Explanation should be dictionary"
        
        # Check required fields
        required_fields = [
            'overall_assessment', 'score_breakdown', 'skills_analysis',
            'experience_analysis', 'education_analysis', 'confidence', 'recommendations'
        ]
        
        for field in required_fields:
            assert field in explanation, f"Field {field} should be in explanation"
        
        # Check score breakdown
        score_breakdown = explanation['score_breakdown']
        assert 'overall' in score_breakdown, "Should include overall score"
        assert 'skills' in score_breakdown, "Should include skills score"
        assert 'experience' in score_breakdown, "Should include experience score"
        assert 'education' in score_breakdown, "Should include education score"
        assert 'additional' in score_breakdown, "Should include additional score"
        
        # Check skills analysis
        skills_analysis = explanation['skills_analysis']
        assert 'matched_skills' in skills_analysis, "Should include matched skills"
        assert 'missing_skills' in skills_analysis, "Should include missing skills"
        
        # Check recommendations
        recommendations = explanation['recommendations']
        assert isinstance(recommendations, list), "Recommendations should be list"
    
    def test_experience_extraction(self, matching_service):
        """Test experience extraction from job text"""
        test_cases = [
            ("Minimum 3 years of experience required", 3),
            ("At least 5 years experience in software development", 5),
            ("2+ years of experience", 2),
            ("10 years minimum experience", 10),
            ("Entry level position", 0),
            ("No specific experience requirements", 0)
        ]
        
        for text, expected_years in test_cases:
            extracted_years = matching_service._extract_required_experience(text)
            assert extracted_years == expected_years, f"Expected {expected_years} years from '{text}', got {extracted_years}"
    
    def test_education_level_extraction(self, matching_service):
        """Test education level extraction"""
        test_cases = [
            ("Bachelor's degree in Computer Science", 3),
            ("Master's degree required", 4),
            ("PhD in relevant field", 5),
            ("MBA preferred", 4.5),
            ("High school diploma", 1),
            ("Associate degree", 2),
            ("No specific education requirements", 0)
        ]
        
        for text, expected_level in test_cases:
            extracted_level = matching_service._extract_required_education(text)
            assert extracted_level == expected_level, f"Expected {expected_level} level from '{text}', got {extracted_level}"
    
    def test_scoring_weights_sum(self, matching_service):
        """Test that scoring weights sum to 1.0"""
        weights = matching_service.scoring_weights
        total_weight = sum(weights.values())
        
        assert abs(total_weight - 1.0) < 0.001, "Scoring weights should sum to 1.0"
    
    def test_error_handling(self, matching_service):
        """Test error handling in match calculation"""
        # Create invalid resume and job
        invalid_resume = ParsedResume(contact_info=ContactInfo())
        invalid_job = JobDescription(title="", company="", description="")
        
        # Should not crash, should return valid result with low scores
        match_result = matching_service.calculate_match_score(invalid_resume, invalid_job)
        
        assert isinstance(match_result, MatchResult), "Should return MatchResult even with invalid data"
        assert 0.0 <= match_result.match_score.overall_score <= 1.0, "Should return valid score range"
