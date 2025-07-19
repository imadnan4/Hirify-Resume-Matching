import pytest
from app.services.resume_parser import ResumeParser, ParsedResume


class TestResumeParser:
    """Test suite for the ResumeParser service"""

    @pytest.fixture(scope='class')
    def parser(self):
        return ResumeParser()

    def test_parse_contact_info(self, parser):
        text = "John Doe\njohndoe@example.com\n+1-202-555-0173"
        contact_info = parser.extract_contact_info(text)

        assert contact_info.full_name == "John Doe"
        assert contact_info.email == "johndoe@example.com"
        assert contact_info.phone == "+1-202-555-0173"

    def test_identify_sections(self, parser):
        text = "\n" \
               "Professional Summary\n" \
               "Experienced software engineer...\n" \
               "Work Experience\n" \
               "Google, Software Developer...\n" \
               "Education\n" \
               "Bachelor of Science in Computer Science"

        sections = parser.identify_sections(text)

        assert 'summary' in sections
        assert 'experience' in sections
        assert 'education' in sections

    def test_parse_work_experience(self, parser):
        text_lines = ["Software Developer at Google | Mountain View, CA", "June 2018 - Present", "Developing...", "• Worked on..."]
        experiences = parser.extract_work_experience(text_lines)

        assert len(experiences) > 0
        assert experiences[0].title == "Software Developer at Google"
        assert experiences[0].start_date == "June 2018"
        assert experiences[0].is_current is True

    def test_parse_education(self, parser):
        text_lines = ["Bachelor of Science in Computer Science", "Harvard University", "Graduated May 2015"]
        education = parser.extract_education(text_lines)

        assert len(education) > 0
        assert education[0].degree == "Bachelor of Science in Computer Science"
        assert education[0].institution == "Harvard University"

    def test_parse_summary(self, parser):
        text_lines = ["Experienced software engineer with a demonstrated history of working..."]
        summary = parser.extract_summary(text_lines)

        assert "Experienced software engineer" in summary

    def test_full_resume_parsing(self, parser):
        text = "John Doe\nProfessional Summary\n " \
               "Innovative software engineer with 5 years..."

        parsed_resume: ParsedResume = parser.parse_resume(text)

        assert parsed_resume.contact_info.full_name == "John Doe"
        assert parsed_resume.summary.startswith("Innovative software engineer")

