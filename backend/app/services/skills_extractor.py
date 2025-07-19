import re
import json
from typing import List, Dict, Set, Tuple
from collections import Counter
import spacy
from spacy.matcher import Matcher
from .text_preprocessor import TextPreprocessor


class SkillsExtractor:
    """Advanced skills extraction and recognition system"""
    
    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.matcher = Matcher(self.nlp.vocab)
        except OSError:
            self.nlp = None
            self.matcher = None
            print("Warning: spaCy model not found. Skills extraction will be limited.")
        
        # Initialize skills database
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
        self.certifications = self._load_certifications()
        
        # Create skill patterns for matching
        self._create_skill_patterns()
    
    def _load_technical_skills(self) -> Dict[str, List[str]]:
        """Load technical skills taxonomy with aliases"""
        return {
            # Programming Languages
            "python": ["python", "py", "python3", "python 3"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "node js"],
            "java": ["java", "java se", "java ee"],
            "c++": ["c++", "cpp", "c plus plus"],
            "c#": ["c#", "csharp", "c sharp"],
            "php": ["php", "php7", "php 7"],
            "ruby": ["ruby", "ruby on rails", "ror"],
            "go": ["go", "golang"],
            "rust": ["rust", "rust lang"],
            "typescript": ["typescript", "ts"],
            "kotlin": ["kotlin"],
            "swift": ["swift"],
            "scala": ["scala"],
            "r": ["r", "r programming"],
            
            # Web Technologies
            "html": ["html", "html5", "html 5"],
            "css": ["css", "css3", "css 3"],
            "react": ["react", "react.js", "reactjs"],
            "angular": ["angular", "angularjs", "angular js"],
            "vue": ["vue", "vue.js", "vuejs"],
            "jquery": ["jquery", "jquery"],
            "bootstrap": ["bootstrap", "bootstrap 4", "bootstrap 5"],
            "sass": ["sass", "scss"],
            "less": ["less"],
            
            # Frameworks
            "django": ["django", "django framework"],
            "flask": ["flask", "flask framework"],
            "spring": ["spring", "spring boot", "spring framework"],
            "express": ["express", "express.js", "expressjs"],
            "laravel": ["laravel", "laravel framework"],
            "rails": ["rails", "ruby on rails"],
            "asp.net": ["asp.net", "asp net", "dot net"],
            
            # Databases
            "mysql": ["mysql", "my sql"],
            "postgresql": ["postgresql", "postgres", "psql"],
            "mongodb": ["mongodb", "mongo", "mongo db"],
            "redis": ["redis"],
            "sqlite": ["sqlite", "sqlite3"],
            "oracle": ["oracle", "oracle db"],
            "sql server": ["sql server", "mssql", "microsoft sql server"],
            
            # Cloud & DevOps
            "aws": ["aws", "amazon web services"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud platform", "google cloud"],
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s"],
            "jenkins": ["jenkins", "jenkins ci"],
            "git": ["git", "version control"],
            "github": ["github"],
            "gitlab": ["gitlab"],
            
            # Data Science & ML
            "machine learning": ["machine learning", "ml", "artificial intelligence", "ai"],
            "deep learning": ["deep learning", "neural networks"],
            "tensorflow": ["tensorflow", "tf"],
            "pytorch": ["pytorch", "torch"],
            "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
            "pandas": ["pandas", "data analysis"],
            "numpy": ["numpy", "numerical computing"],
            "matplotlib": ["matplotlib", "data visualization"],
            "seaborn": ["seaborn"],
            "jupyter": ["jupyter", "jupyter notebook"],
            
            # Testing
            "unit testing": ["unit testing", "unit tests"],
            "pytest": ["pytest", "py.test"],
            "jest": ["jest", "javascript testing"],
            "selenium": ["selenium", "web automation"],
            "postman": ["postman", "api testing"],
            
            # Mobile
            "android": ["android", "android development"],
            "ios": ["ios", "ios development"],
            "react native": ["react native", "react-native"],
            "flutter": ["flutter", "dart"],
            
            # Other Technologies
            "elasticsearch": ["elasticsearch", "elastic search"],
            "kafka": ["kafka", "apache kafka"],
            "spark": ["spark", "apache spark"],
            "hadoop": ["hadoop", "big data"],
            "tableau": ["tableau", "data visualization"],
            "power bi": ["power bi", "powerbi"],
        }
    
    def _load_soft_skills(self) -> Dict[str, List[str]]:
        """Load soft skills with aliases"""
        return {
            "communication": ["communication", "verbal communication", "written communication"],
            "leadership": ["leadership", "team leadership", "leading teams"],
            "teamwork": ["teamwork", "team collaboration", "collaborative"],
            "problem solving": ["problem solving", "analytical thinking", "critical thinking"],
            "project management": ["project management", "agile", "scrum", "kanban"],
            "time management": ["time management", "organizational skills"],
            "adaptability": ["adaptability", "flexibility", "adaptable"],
            "creativity": ["creativity", "innovative", "creative thinking"],
            "attention to detail": ["attention to detail", "detail-oriented", "meticulous"],
            "customer service": ["customer service", "client relations", "customer support"],
            "presentation": ["presentation", "public speaking", "presenting"],
            "negotiation": ["negotiation", "negotiating", "conflict resolution"],
            "mentoring": ["mentoring", "coaching", "training"],
            "strategic thinking": ["strategic thinking", "strategic planning", "strategy"],
        }
    
    def _load_certifications(self) -> Dict[str, List[str]]:
        """Load certifications with aliases"""
        return {
            # Cloud Certifications
            "aws certified": ["aws certified", "amazon web services certified"],
            "azure certified": ["azure certified", "microsoft azure certified"],
            "google cloud certified": ["google cloud certified", "gcp certified"],
            
            # IT Certifications
            "cissp": ["cissp", "certified information systems security professional"],
            "cisa": ["cisa", "certified information systems auditor"],
            "pmp": ["pmp", "project management professional"],
            "cissp": ["cissp", "certified information systems security professional"],
            
            # Programming Certifications
            "oracle certified": ["oracle certified", "oca", "ocp"],
            "microsoft certified": ["microsoft certified", "mcsa", "mcse"],
            "cisco certified": ["cisco certified", "ccna", "ccnp"],
            
            # Agile Certifications
            "scrum master": ["scrum master", "certified scrum master", "csm"],
            "product owner": ["product owner", "certified product owner", "cspo"],
            "safe": ["safe", "scaled agile framework"],
        }
    
    def _create_skill_patterns(self):
        """Create spaCy patterns for skill matching"""
        if not self.matcher:
            return
            
        # Create patterns for technical skills
        for skill, aliases in self.technical_skills.items():
            patterns = []
            for alias in aliases:
                # Create pattern for exact match
                pattern = [{"LOWER": {"IN": alias.lower().split()}}]
                patterns.append(pattern)
            
            if patterns:
                self.matcher.add(f"TECH_{skill.upper()}", patterns)
    
    def extract_skills_with_ner(self, text: str) -> List[Dict]:
        """Extract skills using Named Entity Recognition"""
        if not self.nlp:
            return []
            
        doc = self.nlp(text)
        skills = []
        
        # Extract organizations (often technology companies/tools)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                skill_text = ent.text.lower()
                if self._is_technical_skill(skill_text):
                    skills.append({
                        "skill": skill_text,
                        "category": "technical",
                        "confidence": 0.8,
                        "method": "ner",
                        "start": ent.start_char,
                        "end": ent.end_char
                    })
        
        return skills
    
    def extract_skills_with_regex(self, text: str) -> List[Dict]:
        """Extract skills using regex patterns"""
        skills = []
        text_lower = text.lower()
        
        # Technical skills
        for skill, aliases in self.technical_skills.items():
            for alias in aliases:
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    skills.append({
                        "skill": skill,
                        "category": "technical",
                        "confidence": 0.9,
                        "method": "regex",
                        "start": match.start(),
                        "end": match.end(),
                        "matched_text": match.group()
                    })
        
        # Soft skills
        for skill, aliases in self.soft_skills.items():
            for alias in aliases:
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    skills.append({
                        "skill": skill,
                        "category": "soft",
                        "confidence": 0.8,
                        "method": "regex",
                        "start": match.start(),
                        "end": match.end(),
                        "matched_text": match.group()
                    })
        
        # Certifications
        for cert, aliases in self.certifications.items():
            for alias in aliases:
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    skills.append({
                        "skill": cert,
                        "category": "certification",
                        "confidence": 0.95,
                        "method": "regex",
                        "start": match.start(),
                        "end": match.end(),
                        "matched_text": match.group()
                    })
        
        return skills
    
    def extract_skills_with_spacy_matcher(self, text: str) -> List[Dict]:
        """Extract skills using spaCy matcher patterns"""
        if not self.nlp or not self.matcher:
            return []
            
        doc = self.nlp(text)
        matches = self.matcher(doc)
        skills = []
        
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            skill_name = label.replace("TECH_", "").lower()
            span = doc[start:end]
            
            skills.append({
                "skill": skill_name,
                "category": "technical",
                "confidence": 0.85,
                "method": "spacy_matcher",
                "start": span.start_char,
                "end": span.end_char,
                "matched_text": span.text
            })
        
        return skills
    
    def _is_technical_skill(self, text: str) -> bool:
        """Check if text represents a technical skill"""
        text_lower = text.lower()
        for skill, aliases in self.technical_skills.items():
            if any(alias.lower() in text_lower for alias in aliases):
                return True
        return False
    
    def _normalize_skill(self, skill_text: str) -> str:
        """Normalize skill text to standard form"""
        skill_lower = skill_text.lower()
        
        # Check technical skills
        for skill, aliases in self.technical_skills.items():
            if any(alias.lower() == skill_lower for alias in aliases):
                return skill
        
        # Check soft skills
        for skill, aliases in self.soft_skills.items():
            if any(alias.lower() == skill_lower for alias in aliases):
                return skill
        
        # Check certifications
        for skill, aliases in self.certifications.items():
            if any(alias.lower() == skill_lower for alias in aliases):
                return skill
        
        return skill_text
    
    def _calculate_confidence_score(self, skill: Dict, context: str) -> float:
        """Calculate confidence score for extracted skill"""
        base_confidence = skill.get("confidence", 0.5)
        
        # Boost confidence based on context
        context_lower = context.lower()
        skill_text = skill["skill"].lower()
        
        # Higher confidence if skill appears multiple times
        occurrences = context_lower.count(skill_text)
        if occurrences > 1:
            base_confidence += 0.1 * min(occurrences - 1, 3)
        
        # Higher confidence if skill appears in specific sections
        if any(section in context_lower for section in ["skills", "technologies", "expertise"]):
            base_confidence += 0.1
        
        # Higher confidence for certifications
        if skill["category"] == "certification":
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _remove_duplicates(self, skills: List[Dict]) -> List[Dict]:
        """Remove duplicate skills and merge information"""
        skill_map = {}
        
        for skill in skills:
            skill_key = skill["skill"].lower()
            
            if skill_key not in skill_map:
                skill_map[skill_key] = skill
            else:
                # Keep the one with higher confidence
                if skill["confidence"] > skill_map[skill_key]["confidence"]:
                    skill_map[skill_key] = skill
        
        return list(skill_map.values())
    
    def extract_skills(self, text: str, min_confidence: float = 0.6) -> Dict:
        """Main method to extract skills from text"""
        if not text:
            return {"skills": [], "summary": {"total": 0, "technical": 0, "soft": 0, "certifications": 0}}
        
        # Extract skills using different methods
        all_skills = []
        
        # Method 1: Regex patterns
        regex_skills = self.extract_skills_with_regex(text)
        all_skills.extend(regex_skills)
        
        # Method 2: NER
        ner_skills = self.extract_skills_with_ner(text)
        all_skills.extend(ner_skills)
        
        # Method 3: spaCy matcher
        spacy_skills = self.extract_skills_with_spacy_matcher(text)
        all_skills.extend(spacy_skills)
        
        # Normalize skills
        for skill in all_skills:
            skill["skill"] = self._normalize_skill(skill["skill"])
            skill["confidence"] = self._calculate_confidence_score(skill, text)
        
        # Remove duplicates
        unique_skills = self._remove_duplicates(all_skills)
        
        # Filter by confidence threshold
        filtered_skills = [skill for skill in unique_skills if skill["confidence"] >= min_confidence]
        
        # Sort by confidence
        filtered_skills.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Create summary
        summary = {
            "total": len(filtered_skills),
            "technical": len([s for s in filtered_skills if s["category"] == "technical"]),
            "soft": len([s for s in filtered_skills if s["category"] == "soft"]),
            "certifications": len([s for s in filtered_skills if s["category"] == "certification"])
        }
        
        return {
            "skills": filtered_skills,
            "summary": summary
        }
    
    def get_skill_categories(self) -> Dict:
        """Get all available skill categories"""
        return {
            "technical_skills": list(self.technical_skills.keys()),
            "soft_skills": list(self.soft_skills.keys()),
            "certifications": list(self.certifications.keys())
        }
    
    def fuzzy_match_skills(self, query: str, threshold: float = 0.8) -> List[str]:
        """Find skills similar to query using fuzzy matching"""
        from difflib import get_close_matches
        
        all_skills = list(self.technical_skills.keys()) + list(self.soft_skills.keys()) + list(self.certifications.keys())
        
        # Also include aliases
        all_aliases = []
        for skill_dict in [self.technical_skills, self.soft_skills, self.certifications]:
            for skill, aliases in skill_dict.items():
                all_aliases.extend(aliases)
        
        all_skills.extend(all_aliases)
        
        matches = get_close_matches(query.lower(), [skill.lower() for skill in all_skills], 
                                  n=10, cutoff=threshold)
        
        return matches
