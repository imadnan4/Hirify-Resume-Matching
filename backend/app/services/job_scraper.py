import asyncio
import aiohttp
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import hashlib
from .text_preprocessor import TextPreprocessor
from .skills_extractor import SkillsExtractor


@dataclass
class JobDescription:
    """Job description data structure"""
    title: str
    company: str
    location: Optional[str] = None
    description: str = ""
    requirements: str = ""
    salary_range: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experience_level: Optional[str] = None  # Entry, Mid, Senior, etc.
    source: str = ""
    source_url: str = ""
    scraped_date: datetime = field(default_factory=datetime.now)
    skills: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    remote_ok: bool = False
    job_id: Optional[str] = None
    
    def __post_init__(self):
        # Generate unique job ID based on title, company, and description
        if not self.job_id:
            content = f"{self.title}{self.company}{self.description[:100]}"
            self.job_id = hashlib.md5(content.encode()).hexdigest()[:10]


class JobScraper:
    """Advanced job scraping service with multiple source support"""
    
    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        self.skills_extractor = SkillsExtractor()
        self.scraped_jobs: Set[str] = set()  # Track scraped job IDs for deduplication
        self.session = None
        
        # Rate limiting settings
        self.request_delay = 2.0  # seconds between requests
        self.max_concurrent_requests = 5
        
        # Common job selectors for different sites
        self.site_selectors = {
            'indeed.com': {
                'job_cards': '.job_seen_beacon',
                'title': '[data-jk] h2 a span',
                'company': '.companyName',
                'location': '.companyLocation',
                'description': '.jobsearch-jobDescriptionText',
                'salary': '.salary-snippet',
            },
            'linkedin.com': {
                'job_cards': '.jobs-search__results-list li',
                'title': '.job-card-list__title',
                'company': '.job-card-container__company-name',
                'location': '.job-card-container__metadata-item',
                'description': '.jobs-description__content',
            },
            'glassdoor.com': {
                'job_cards': '.react-job-listing',
                'title': '.jobTitle',
                'company': '.employerName',
                'location': '.location',
                'description': '.jobDescriptionContent',
                'salary': '.salaryText',
            },
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_indeed(self, search_query: str, location: str = "", max_pages: int = 3) -> List[JobDescription]:
        """Scrape job listings from Indeed"""
        jobs = []
        
        for page in range(max_pages):
            url = f"https://www.indeed.com/jobs?q={search_query}&l={location}&start={page * 10}"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        job_cards = soup.select(self.site_selectors['indeed.com']['job_cards'])
                        
                        for card in job_cards:
                            try:
                                title_elem = card.select_one(self.site_selectors['indeed.com']['title'])
                                company_elem = card.select_one(self.site_selectors['indeed.com']['company'])
                                location_elem = card.select_one(self.site_selectors['indeed.com']['location'])
                                
                                if title_elem and company_elem:
                                    title = title_elem.get_text(strip=True)
                                    company = company_elem.get_text(strip=True)
                                    location_text = location_elem.get_text(strip=True) if location_elem else ""
                                    
                                    # Get job details URL
                                    job_link = card.select_one('a[data-jk]')
                                    job_url = ""
                                    if job_link:
                                        job_url = urljoin("https://www.indeed.com", job_link.get('href', ''))
                                    
                                    # Create job description
                                    job = JobDescription(
                                        title=title,
                                        company=company,
                                        location=location_text,
                                        source="indeed.com",
                                        source_url=job_url,
                                        scraped_date=datetime.now()
                                    )
                                    
                                    # Get detailed description if URL available
                                    if job_url:
                                        job.description = await self._get_job_details(job_url, 'indeed.com')
                                    
                                    jobs.append(job)
                                    
                            except Exception as e:
                                print(f"Error parsing job card: {e}")
                                continue
                        
                        # Rate limiting
                        await asyncio.sleep(self.request_delay)
                        
            except Exception as e:
                print(f"Error scraping Indeed page {page}: {e}")
                continue
        
        return jobs
    
    async def scrape_linkedin(self, search_query: str, location: str = "", max_pages: int = 3) -> List[JobDescription]:
        """Scrape job listings from LinkedIn"""
        jobs = []
        
        # Note: LinkedIn requires authentication for most job listings
        # This is a simplified implementation that would need proper authentication
        
        for page in range(max_pages):
            url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location}&start={page * 25}"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        job_cards = soup.select(self.site_selectors['linkedin.com']['job_cards'])
                        
                        for card in job_cards:
                            try:
                                title_elem = card.select_one(self.site_selectors['linkedin.com']['title'])
                                company_elem = card.select_one(self.site_selectors['linkedin.com']['company'])
                                location_elem = card.select_one(self.site_selectors['linkedin.com']['location'])
                                
                                if title_elem and company_elem:
                                    title = title_elem.get_text(strip=True)
                                    company = company_elem.get_text(strip=True)
                                    location_text = location_elem.get_text(strip=True) if location_elem else ""
                                    
                                    job = JobDescription(
                                        title=title,
                                        company=company,
                                        location=location_text,
                                        source="linkedin.com",
                                        source_url=url,
                                        scraped_date=datetime.now()
                                    )
                                    
                                    jobs.append(job)
                                    
                            except Exception as e:
                                print(f"Error parsing LinkedIn job card: {e}")
                                continue
                        
                        await asyncio.sleep(self.request_delay)
                        
            except Exception as e:
                print(f"Error scraping LinkedIn page {page}: {e}")
                continue
        
        return jobs
    
    async def scrape_glassdoor(self, search_query: str, location: str = "", max_pages: int = 3) -> List[JobDescription]:
        """Scrape job listings from Glassdoor"""
        jobs = []
        
        for page in range(max_pages):
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_query}&locT=C&locId={location}&p={page + 1}"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        job_cards = soup.select(self.site_selectors['glassdoor.com']['job_cards'])
                        
                        for card in job_cards:
                            try:
                                title_elem = card.select_one(self.site_selectors['glassdoor.com']['title'])
                                company_elem = card.select_one(self.site_selectors['glassdoor.com']['company'])
                                location_elem = card.select_one(self.site_selectors['glassdoor.com']['location'])
                                
                                if title_elem and company_elem:
                                    title = title_elem.get_text(strip=True)
                                    company = company_elem.get_text(strip=True)
                                    location_text = location_elem.get_text(strip=True) if location_elem else ""
                                    
                                    job = JobDescription(
                                        title=title,
                                        company=company,
                                        location=location_text,
                                        source="glassdoor.com",
                                        source_url=url,
                                        scraped_date=datetime.now()
                                    )
                                    
                                    jobs.append(job)
                                    
                            except Exception as e:
                                print(f"Error parsing Glassdoor job card: {e}")
                                continue
                        
                        await asyncio.sleep(self.request_delay)
                        
            except Exception as e:
                print(f"Error scraping Glassdoor page {page}: {e}")
                continue
        
        return jobs
    
    async def _get_job_details(self, job_url: str, source: str) -> str:
        """Get detailed job description from job URL"""
        try:
            async with self.session.get(job_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract description based on source
                    if source == 'indeed.com':
                        desc_elem = soup.select_one(self.site_selectors['indeed.com']['description'])
                        if desc_elem:
                            return desc_elem.get_text(strip=True)
                    
                    elif source == 'linkedin.com':
                        desc_elem = soup.select_one(self.site_selectors['linkedin.com']['description'])
                        if desc_elem:
                            return desc_elem.get_text(strip=True)
                    
                    elif source == 'glassdoor.com':
                        desc_elem = soup.select_one(self.site_selectors['glassdoor.com']['description'])
                        if desc_elem:
                            return desc_elem.get_text(strip=True)
                    
        except Exception as e:
            print(f"Error getting job details from {job_url}: {e}")
        
        return ""
    
    def extract_job_requirements(self, description: str) -> str:
        """Extract requirements section from job description"""
        requirements_patterns = [
            r'requirements?[:\s]*(.*?)(?=responsibilities|qualifications|benefits|$)',
            r'qualifications?[:\s]*(.*?)(?=responsibilities|requirements|benefits|$)',
            r'must have[:\s]*(.*?)(?=responsibilities|qualifications|benefits|$)',
            r'you[\'|\s]?(?:will|should|must)[:\s]*(.*?)(?=responsibilities|qualifications|benefits|$)',
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_salary_range(self, description: str) -> Optional[str]:
        """Extract salary range from job description"""
        salary_patterns = [
            r'\$[\d,]+(?:\.\d{2})?\s*-\s*\$[\d,]+(?:\.\d{2})?',
            r'\$[\d,]+(?:\.\d{2})?\s*(?:per|/)\s*(?:year|month|hour)',
            r'[\d,]+k?\s*-\s*[\d,]+k?\s*(?:per|/)\s*(?:year|month|hour)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def extract_job_type(self, description: str) -> Optional[str]:
        """Extract job type from description"""
        job_type_patterns = [
            r'full[-\s]?time',
            r'part[-\s]?time',
            r'contract',
            r'temporary',
            r'internship',
            r'remote',
            r'freelance',
        ]
        
        for pattern in job_type_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return pattern.replace('[-\\s]?', '-')
        
        return None
    
    def extract_experience_level(self, description: str) -> Optional[str]:
        """Extract experience level from description"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'entry[-\s]?level',
            r'junior',
            r'mid[-\s]?level',
            r'senior',
            r'lead',
            r'principal',
            r'staff',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def extract_benefits(self, description: str) -> List[str]:
        """Extract benefits from job description"""
        benefits_patterns = [
            r'health\s*insurance',
            r'dental\s*insurance',
            r'vision\s*insurance',
            r'401k',
            r'retirement\s*plan',
            r'paid\s*time\s*off',
            r'vacation\s*days',
            r'sick\s*leave',
            r'maternity\s*leave',
            r'paternity\s*leave',
            r'flexible\s*hours',
            r'work\s*from\s*home',
            r'remote\s*work',
            r'stock\s*options',
            r'equity',
            r'bonus',
            r'gym\s*membership',
            r'free\s*lunch',
            r'snacks',
            r'coffee',
        ]
        
        benefits = []
        for pattern in benefits_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                benefits.append(pattern.replace('\\s*', ' '))
        
        return benefits
    
    def process_job_description(self, job: JobDescription) -> JobDescription:
        """Process and enhance job description with extracted information"""
        # Extract requirements
        job.requirements = self.extract_job_requirements(job.description)
        
        # Extract salary range
        job.salary_range = self.extract_salary_range(job.description)
        
        # Extract job type
        job.job_type = self.extract_job_type(job.description)
        
        # Extract experience level
        job.experience_level = self.extract_experience_level(job.description)
        
        # Extract benefits
        job.benefits = self.extract_benefits(job.description)
        
        # Extract skills
        full_text = f"{job.title} {job.description} {job.requirements}"
        skills_result = self.skills_extractor.extract_skills(full_text)
        job.skills = [skill['skill'] for skill in skills_result['skills']]
        
        # Check if remote work is mentioned
        job.remote_ok = bool(re.search(r'remote|work\s*from\s*home', job.description, re.IGNORECASE))
        
        return job
    
    def deduplicate_jobs(self, jobs: List[JobDescription]) -> List[JobDescription]:
        """Remove duplicate job descriptions"""
        unique_jobs = []
        seen_ids = set()
        
        for job in jobs:
            if job.job_id not in seen_ids:
                seen_ids.add(job.job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def scrape_all_sources(self, search_query: str, location: str = "", max_pages: int = 3) -> List[JobDescription]:
        """Scrape jobs from all supported sources"""
        all_jobs = []
        
        try:
            # Scrape Indeed
            print(f"Scraping Indeed for '{search_query}' in '{location}'...")
            indeed_jobs = await self.scrape_indeed(search_query, location, max_pages)
            all_jobs.extend(indeed_jobs)
            
            # Scrape LinkedIn
            print(f"Scraping LinkedIn for '{search_query}' in '{location}'...")
            linkedin_jobs = await self.scrape_linkedin(search_query, location, max_pages)
            all_jobs.extend(linkedin_jobs)
            
            # Scrape Glassdoor
            print(f"Scraping Glassdoor for '{search_query}' in '{location}'...")
            glassdoor_jobs = await self.scrape_glassdoor(search_query, location, max_pages)
            all_jobs.extend(glassdoor_jobs)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        # Process and deduplicate jobs
        processed_jobs = [self.process_job_description(job) for job in all_jobs]
        unique_jobs = self.deduplicate_jobs(processed_jobs)
        
        print(f"Found {len(all_jobs)} total jobs, {len(unique_jobs)} unique jobs")
        
        return unique_jobs
    
    async def scrape_company_careers(self, company_url: str, company_name: str) -> List[JobDescription]:
        """Scrape jobs from company career pages"""
        jobs = []
        
        try:
            async with self.session.get(company_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Generic selectors for job listings
                    job_selectors = [
                        '.job-listing',
                        '.career-listing',
                        '.position',
                        '.job-post',
                        '.opening',
                        '[class*="job"]',
                        '[class*="career"]',
                        '[class*="position"]',
                    ]
                    
                    for selector in job_selectors:
                        job_elements = soup.select(selector)
                        
                        for elem in job_elements:
                            try:
                                # Extract title (usually in h2, h3, or link)
                                title_elem = elem.select_one('h2, h3, a, .title')
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    
                                    # Extract description if available
                                    desc_elem = elem.select_one('.description, .summary, p')
                                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                                    
                                    # Extract location if available
                                    location_elem = elem.select_one('.location, .city, .office')
                                    location = location_elem.get_text(strip=True) if location_elem else ""
                                    
                                    job = JobDescription(
                                        title=title,
                                        company=company_name,
                                        location=location,
                                        description=description,
                                        source=f"careers.{company_name.lower()}",
                                        source_url=company_url,
                                        scraped_date=datetime.now()
                                    )
                                    
                                    jobs.append(job)
                                    
                            except Exception as e:
                                print(f"Error parsing company job: {e}")
                                continue
                        
                        if jobs:  # If we found jobs with this selector, stop trying others
                            break
                    
        except Exception as e:
            print(f"Error scraping company careers from {company_url}: {e}")
        
        return jobs


# Usage example function
async def main():
    """Example usage of the job scraper"""
    async with JobScraper() as scraper:
        # Scrape jobs for software engineer positions
        jobs = await scraper.scrape_all_sources(
            search_query="software engineer",
            location="San Francisco, CA",
            max_pages=2
        )
        
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:5]:  # Print first 5 jobs
            print(f"- {job.title} at {job.company} ({job.source})")
            print(f"  Skills: {', '.join(job.skills[:5])}...")
            print(f"  Remote: {'Yes' if job.remote_ok else 'No'}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
