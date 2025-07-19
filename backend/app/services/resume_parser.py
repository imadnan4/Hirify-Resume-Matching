import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import spacy
from .text_preprocessor import TextPreprocessor
from .skills_extractor import SkillsExtractor


@dataclass
class ContactInfo:
    """Contact information data structure"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


@dataclass
class WorkExperience:
    """Work experience data structure"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False


@dataclass
class Education:
    """Education data structure"""
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: Optional[str] = None


@dataclass
class ParsedResume:
    """Complete parsed resume data structure"""
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = None
    education: List[Education] = None
    skills: Dict = None
    certifications: List[str] = None
    languages: List[str] = None
    projects: List[str] = None
    achievements: List[str] = None
    raw_text: str = ""
    processing_metadata: Dict = None

    def __post_init__(self):
        if self.work_experience is None:
            self.work_experience = []
        if self.education is None:
            self.education = []
        if self.skills is None:
            self.skills = {}
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []
        if self.projects is None:
            self.projects = []
        if self.achievements is None:
            self.achievements = []
        if self.processing_metadata is None:
            self.processing_metadata = {}


class ResumeParser:
    """Advanced resume parsing service with section identification"""
    
    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        self.skills_extractor = SkillsExtractor()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            print("Warning: spaCy model not found. Some features may be limited.")
        
        # Section patterns for identification
        self.section_patterns = {
            'contact': [
                r'contact\s+information',
                r'personal\s+information',
                r'contact\s+details',
            ],
            'summary': [
                r'professional\s+summary',
                r'career\s+summary',
                r'summary\s+of\s+qualifications',
                r'profile',
                r'objective',
                r'about\s+me',
                r'career\s+objective',
                r'professional\s+profile',
            ],
            'experience': [
                r'work\s+experience',
                r'professional\s+experience',
                r'employment\s+history',
                r'career\s+history',
                r'experience',
                r'employment',
                r'work\s+history',
            ],
            'education': [
                r'education',
                r'educational\s+background',
                r'academic\s+background',
                r'qualifications',
                r'academic\s+qualifications',
            ],
            'skills': [
                r'skills',
                r'technical\s+skills',
                r'core\s+competencies',
                r'competencies',
                r'expertise',
                r'technologies',
                r'proficiencies',
                r'capabilities',
            ],
            'certifications': [
                r'certifications',
                r'certificates',
                r'professional\s+certifications',
                r'licenses',
                r'credentials',
            ],
            'projects': [
                r'projects',
                r'key\s+projects',
                r'notable\s+projects',
                r'selected\s+projects',
                r'project\s+experience',
            ],
            'achievements': [
                r'achievements',
                r'accomplishments',
                r'awards',
                r'honors',
                r'recognition',
            ],
            'languages': [
                r'languages',
                r'language\s+skills',
                r'foreign\s+languages',
            ]
        }
    
    def identify_sections(self, text: str) -> Dict[str, List[str]]:
        """Identify different sections in resume text"""
        lines = text.split('\n')
        sections = {}
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            section_found = None
            for section_type, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        section_found = section_type
                        break
                if section_found:
                    break
            
            if section_found:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = current_content
                
                # Start new section
                current_section = section_found
                current_content = []
            else:
                # Add to current section
                if current_section:
                    current_content.append(line)
        
        # Save the last section
        if current_section and current_content:
            sections[current_section] = current_content
        
        return sections
    
    def extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from resume text"""
        contact = ContactInfo()
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact.email = email_match.group()
        
        # Phone pattern
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact.phone = phone_match.group()
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()
        
        # GitHub pattern
        github_pattern = r'github\.com/[A-Za-z0-9-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact.github = github_match.group()
        
        # Website pattern
        website_pattern = r'https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        website_matches = re.findall(website_pattern, text)
        if website_matches:
            # Filter out LinkedIn and GitHub URLs
            websites = [url for url in website_matches 
                       if 'linkedin.com' not in url and 'github.com' not in url]
            if websites:
                contact.website = websites[0]
        
        # Extract name using NER
        if self.nlp:
            doc = self.nlp(text[:500])  # Check first 500 chars for name
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    contact.full_name = ent.text
                    break
        
        # Fallback name extraction from first line
        if not contact.full_name:
            lines = text.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and not any(char.isdigit() for char in line) and '@' not in line:
                    # Simple heuristic: if it's a short line without numbers or @ symbol
                    if len(line.split()) >= 2 and len(line.split()) <= 4:
                        contact.full_name = line
                        break
        
        return contact
    
    def extract_work_experience(self, text_lines: List[str]) -> List[WorkExperience]:
        """Extract work experience from text lines"""
        experiences = []
        current_experience = None
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for job title patterns
            job_title_indicators = ['developer', 'engineer', 'manager', 'analyst', 'specialist', 
                                  'coordinator', 'consultant', 'director', 'lead', 'senior', 
                                  'junior', 'intern', 'associate']
            
            if any(indicator in line.lower() for indicator in job_title_indicators):
                # Save previous experience
                if current_experience:
                    experiences.append(current_experience)
                
                # Start new experience
                current_experience = WorkExperience()
                current_experience.title = line
                
                # Try to extract company name from the same line or next line
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        current_experience.title = parts[0].strip()
                        current_experience.company = parts[1].strip()
            
            # Check for date patterns
            date_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|\w+\s+\d{4})'
            if re.search(date_pattern, line):
                if current_experience:
                    # Extract date range
                    date_range_pattern = r'(\w+\s+\d{4}|\d{4})\s*[-–—]\s*(\w+\s+\d{4}|\d{4}|present|current)'
                    date_match = re.search(date_range_pattern, line, re.IGNORECASE)
                    if date_match:
                        current_experience.start_date = date_match.group(1)
                        current_experience.end_date = date_match.group(2)
                        current_experience.is_current = 'present' in date_match.group(2).lower() or 'current' in date_match.group(2).lower()
            
            # Check for company names (if not already extracted)
            if current_experience and not current_experience.company:
                # Look for company indicators
                company_indicators = ['inc', 'corp', 'llc', 'ltd', 'company', 'technologies', 'solutions']
                if any(indicator in line.lower() for indicator in company_indicators):
                    current_experience.company = line
            
            # Add to description if it's a bullet point or detailed description
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if current_experience:
                    if current_experience.description:
                        current_experience.description += '\n' + line
                    else:
                        current_experience.description = line
        
        # Save the last experience
        if current_experience:
            experiences.append(current_experience)
        
        return experiences
    
    def extract_education(self, text_lines: List[str]) -> List[Education]:
        """Extract education information from text lines"""
        educations = []
        current_education = None
        
        # Degree patterns
        degree_patterns = [
            r'bachelor',
            r'master',
            r'phd',
            r'doctorate',
            r'b\.?s\.?',
            r'b\.?a\.?',
            r'm\.?s\.?',
            r'm\.?a\.?',
            r'mba',
            r'associate',
            r'diploma',
            r'certificate',
        ]
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for degree patterns
            for pattern in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Save previous education
                    if current_education:
                        educations.append(current_education)
                    
                    # Start new education
                    current_education = Education()
                    current_education.degree = line
                    break
            
            # Check for graduation date
            date_pattern = r'(\d{4}|\w+\s+\d{4})'
            if re.search(date_pattern, line):
                if current_education:
                    current_education.graduation_date = re.search(date_pattern, line).group()
            
            # Check for GPA
            gpa_pattern = r'gpa[:\s]*(\d\.\d+|\d+\.\d+/\d+\.\d+)'
            gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
            if gpa_match and current_education:
                current_education.gpa = gpa_match.group(1)
            
            # Check for institution names
            institution_indicators = ['university', 'college', 'institute', 'school', 'academy']
            if any(indicator in line.lower() for indicator in institution_indicators):
                if current_education and not current_education.institution:
                    current_education.institution = line
        
        # Save the last education
        if current_education:
            educations.append(current_education)
        
        return educations
    
    def extract_summary(self, text_lines: List[str]) -> str:
        """Extract professional summary from text lines"""
        return ' '.join(text_lines).strip()
    
    def extract_projects(self, text_lines: List[str]) -> List[str]:
        """Extract project information from text lines"""
        projects = []
        current_project = ""
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # If line starts with bullet point, it's a new project
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if current_project:
                    projects.append(current_project)
                current_project = line
            else:
                # Continue current project description
                if current_project:
                    current_project += ' ' + line
                else:
                    current_project = line
        
        # Add the last project
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def extract_achievements(self, text_lines: List[str]) -> List[str]:
        """Extract achievements from text lines"""
        achievements = []
        
        for line in text_lines:
            line = line.strip()
            if line:
                achievements.append(line)
        
        return achievements
    
    def extract_languages(self, text_lines: List[str]) -> List[str]:
        """Extract languages from text lines"""
        languages = []
        
        # Common language patterns
        language_patterns = [
            r'english',
            r'spanish',
            r'french',
            r'german',
            r'italian',
            r'portuguese',
            r'russian',
            r'chinese',
            r'japanese',
            r'korean',
            r'arabic',
            r'hindi',
            r'native',
            r'fluent',
            r'conversational',
            r'beginner',
            r'intermediate',
            r'advanced',
        ]
        
        text = ' '.join(text_lines).lower()
        
        for pattern in language_patterns:
            if re.search(pattern, text):
                languages.append(pattern.capitalize())
        
        return list(set(languages))  # Remove duplicates
    
    def calculate_years_of_experience(self, work_experiences: List[WorkExperience]) -> int:
        """Calculate total years of experience from work history"""
        total_months = 0
        
        for exp in work_experiences:
            if exp.start_date and exp.end_date:
                # Simple calculation - could be improved with proper date parsing
                try:
                    start_year = int(re.search(r'\d{4}', exp.start_date).group())
                    if exp.is_current:
                        end_year = datetime.now().year
                    else:
                        end_year = int(re.search(r'\d{4}', exp.end_date).group())
                    
                    years = end_year - start_year
                    total_months += years * 12
                except (AttributeError, ValueError):
                    # If date parsing fails, assume 1 year
                    total_months += 12
        
        return total_months // 12
    
    def parse_resume(self, text: str) -> ParsedResume:
        """Main method to parse resume text into structured data"""
        # Initialize parsed resume
        parsed_resume = ParsedResume(
            contact_info=ContactInfo(),
            raw_text=text
        )
        
        # Extract contact information from full text
        parsed_resume.contact_info = self.extract_contact_info(text)
        
        # Identify sections
        sections = self.identify_sections(text)
        
        # Extract information from each section
        if 'summary' in sections:
            parsed_resume.summary = self.extract_summary(sections['summary'])
        
        if 'experience' in sections:
            parsed_resume.work_experience = self.extract_work_experience(sections['experience'])
        
        if 'education' in sections:
            parsed_resume.education = self.extract_education(sections['education'])
        
        if 'projects' in sections:
            parsed_resume.projects = self.extract_projects(sections['projects'])
        
        if 'achievements' in sections:
            parsed_resume.achievements = self.extract_achievements(sections['achievements'])
        
        if 'languages' in sections:
            parsed_resume.languages = self.extract_languages(sections['languages'])
        
        # Extract skills from the entire text
        skills_result = self.skills_extractor.extract_skills(text)
        parsed_resume.skills = skills_result
        
        # Extract certifications (from skills or dedicated section)
        if 'certifications' in sections:
            cert_text = ' '.join(sections['certifications'])
            cert_skills = self.skills_extractor.extract_skills(cert_text)
            parsed_resume.certifications = [
                skill['skill'] for skill in cert_skills['skills'] 
                if skill['category'] == 'certification'
            ]
        else:
            # Get certifications from general skills extraction
            parsed_resume.certifications = [
                skill['skill'] for skill in skills_result['skills'] 
                if skill['category'] == 'certification'
            ]
        
        # Calculate processing metadata
        parsed_resume.processing_metadata = {
            'total_years_experience': self.calculate_years_of_experience(parsed_resume.work_experience),
            'total_skills': len(parsed_resume.skills.get('skills', [])),
            'sections_found': list(sections.keys()),
            'processing_timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'confidence_score': self._calculate_overall_confidence(parsed_resume)
        }
        
        return parsed_resume
    
    def _calculate_overall_confidence(self, parsed_resume: ParsedResume) -> float:
        """Calculate overall confidence score for the parsed resume"""
        confidence_factors = []
        
        # Contact information completeness
        contact_fields = [
            parsed_resume.contact_info.full_name,
            parsed_resume.contact_info.email,
            parsed_resume.contact_info.phone
        ]
        contact_completeness = sum(1 for field in contact_fields if field) / len(contact_fields)
        confidence_factors.append(contact_completeness * 0.3)
        
        # Work experience presence
        if parsed_resume.work_experience:
            confidence_factors.append(0.25)
        
        # Education presence
        if parsed_resume.education:
            confidence_factors.append(0.15)
        
        # Skills extraction confidence
        if parsed_resume.skills and parsed_resume.skills.get('skills'):
            avg_skill_confidence = sum(
                skill['confidence'] for skill in parsed_resume.skills['skills']
            ) / len(parsed_resume.skills['skills'])
            confidence_factors.append(avg_skill_confidence * 0.2)
        
        # Summary presence
        if parsed_resume.summary:
            confidence_factors.append(0.1)
        
        return sum(confidence_factors) if confidence_factors else 0.0
