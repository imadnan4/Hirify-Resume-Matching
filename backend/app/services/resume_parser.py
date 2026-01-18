import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import spacy
from .nlp_service import nlp_service
from .semantic_skills import semantic_skills_extractor


@dataclass
class ContactInfo:
    """Contact information data structure"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
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
        self.nlp_service = nlp_service
        self.skills_extractor = semantic_skills_extractor
        self.nlp = None  # Don't load spaCy model during init - use lazy loading
        self.__post_init__()
        
    def _load_spacy_model(self):
        """Load spaCy model on demand"""
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("Successfully loaded spaCy model 'en_core_web_sm'")
            except OSError:
                print("Warning: spaCy model not found. Some features may be limited.")
                print("Please run: python -m spacy download en_core_web_sm")
                self.nlp = False
    
    def __post_init__(self):
        """Initialize section patterns"""
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
        
        # Define exact section headers and their mappings
        section_headers = {
            'PROFESSIONAL SUMMARY': 'summary',
            'TECHNICAL SKILLS': 'skills', 
            'PROFESSIONAL EXPERIENCE': 'experience',
            'KEY PROJECTS': 'projects',
            'EDUCATION CERTIFICATIONS': 'education',  # Treat as single education section
            'LANGUAGES': 'languages'
        }
        
        section_indices = {}
        
        # Find exact section header matches
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean in section_headers:
                header_mapping = section_headers[line_clean]
                if isinstance(header_mapping, list):
                    # Combined section - assign same index to both
                    for section_name in header_mapping:
                        section_indices[section_name] = i
                else:
                    section_indices[header_mapping] = i
        
        # Sort sections by their appearance
        sorted_sections = sorted(section_indices.items(), key=lambda item: item[1])
        
        # Extract content for each section
        for i in range(len(sorted_sections)):
            section_name, start_index = sorted_sections[i]
            end_index = sorted_sections[i+1][1] if i + 1 < len(sorted_sections) else len(lines)
            
            # Get all content between this section and the next
            content_lines = [lines[j].strip() for j in range(start_index + 1, end_index) if lines[j].strip()]
            
            # Assign all content lines to the section
            sections[section_name] = content_lines
            
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
        self._load_spacy_model()
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
        
        # Extract location using NER and patterns
        self._extract_location(text, contact)
        
        return contact
    
    def _extract_location(self, text: str, contact: ContactInfo) -> None:
        """Extract location information from resume text"""
        # Use spaCy NER to find locations
        self._load_spacy_model()
        if self.nlp:
            doc = self.nlp(text[:1000])  # Check first 1000 chars for location
            locations = []
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:  # GPE = Geopolitical entity, LOC = Location
                    locations.append(ent.text)
            
            if locations:
                # Take the first location found
                contact.location = locations[0]
                return
        
        # Fallback: pattern-based location extraction
        # Look for common location patterns in first few lines
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            
            # Pattern: City, State ZIP
            location_pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})?'
            location_match = re.search(location_pattern, line)
            if location_match:
                city = location_match.group(1).strip()
                state = location_match.group(2)
                if len(city.split()) <= 3:  # Reasonable city name length
                    contact.location = f"{city}, {state}"
                    return
            
            # Pattern: City, State (without ZIP)
            location_pattern2 = r'([A-Za-z\s]+),\s*([A-Za-z\s]+)$'
            location_match2 = re.search(location_pattern2, line)
            if location_match2:
                city = location_match2.group(1).strip()
                state = location_match2.group(2).strip()
                # Check if it looks like a reasonable location
                if (len(city.split()) <= 3 and len(state.split()) <= 2 and 
                    not any(char.isdigit() for char in line) and '@' not in line):
                    contact.location = f"{city}, {state}"
                    return
    
    def extract_work_experience(self, text_lines: List[str]) -> List[WorkExperience]:
        """Extract work experience from text lines"""
        experiences = []
        current_experience = None
        
        i = 0
        while i < len(text_lines):
            line = text_lines[i].strip()
            if not line:
                i += 1
                continue

            # Look for job title (first non-bullet line)
            if not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                # If we have a previous experience, save it
                if current_experience:
                    experiences.append(current_experience)
                
                # Start new experience
                current_experience = WorkExperience(title=line)
                
                # Check if next line has company/location/date info
                if i + 1 < len(text_lines):
                    next_line = text_lines[i + 1].strip()
                    if '|' in next_line:
                        # Parse company | location | date format
                        parts = [p.strip() for p in next_line.split('|')]
                        if len(parts) >= 1:
                            current_experience.company = parts[0]
                        if len(parts) >= 2:
                            current_experience.location = parts[1]
                        if len(parts) >= 3:
                            # Parse date range
                            date_part = parts[2]
                            date_pattern = re.compile(r'(\w+\s*-?\s*\w*\s+\d{4})', re.IGNORECASE)
                            dates = date_pattern.findall(date_part)
                            if len(dates) >= 1:
                                current_experience.start_date = dates[0]
                            if len(dates) >= 2:
                                current_experience.end_date = dates[1]
                            elif len(dates) == 1 and '-' in date_part:
                                # Handle "August - September 2024" format
                                date_range_pattern = re.compile(r'(\w+)\s*-\s*(\w+\s+\d{4})', re.IGNORECASE)
                                date_match = date_range_pattern.search(date_part)
                                if date_match:
                                    month_start = date_match.group(1)
                                    month_end_year = date_match.group(2)
                                    year = re.search(r'\d{4}', month_end_year).group()
                                    current_experience.start_date = f"{month_start} {year}"
                                    current_experience.end_date = month_end_year
                        i += 1  # Skip the company/location/date line
                
            # Add bullet points to description
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if current_experience:
                    if not current_experience.description:
                        current_experience.description = ''
                    current_experience.description += line + '\n'
            
            i += 1
        
        # Save the last experience
        if current_experience:
            experiences.append(current_experience)
        
        return experiences
    
    def extract_education(self, text_lines: List[str]) -> List[Education]:
        """Extract education information from text lines"""
        educations = []
        current_education = None
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue

            # Create a new education entry for each line
            current_education = Education()
            
            # Split line by | to separate degree/major from institution/date
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) > 0:
                current_education.degree = parts[0]
            
            if len(parts) > 1:
                # Check for graduation year
                grad_year_match = re.search(r'\b(\d{4})\b', parts[1])
                if grad_year_match:
                    current_education.graduation_date = grad_year_match.group(1)
                    # The rest is the institution
                    current_education.institution = re.sub(r'\b(\d{4})\b', '', parts[1]).strip()
                else:
                    current_education.institution = parts[1]
            
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
