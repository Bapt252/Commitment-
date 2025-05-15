"""
Smart Match Engine

This module provides the core matching engine for the SmartMatch system, 
enabling bidirectional matching between CVs and job posts.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Configure logging
logger = logging.getLogger(__name__)

class SmartMatcher:
    """
    Main engine for matching CVs and job descriptions using various 
    sophisticated techniques.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SmartMatcher with optional configuration parameters.
        
        Args:
            config (dict, optional): Configuration parameters for the matcher.
        """
        self.config = config or {}
        
        # Initialize NLP tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english') + stopwords.words('french'))
        
        # Set default weights for match scoring
        self.weights = self.config.get('weights', {
            'skills': 0.40,
            'experience': 0.25,
            'education': 0.15,
            'title_relevance': 0.10,
            'location': 0.10,
        })
        
        logger.info("SmartMatcher initialized with weights: %s", self.weights)

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for NLP analysis.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        filtered_tokens = [
            self.lemmatizer.lemmatize(word) 
            for word in tokens 
            if word not in self.stop_words and len(word) > 2
        ]
        
        return " ".join(filtered_tokens)

    def calculate_match_score(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the match score between a CV and a job posting.
        
        Args:
            cv_data (dict): Structured CV data
            job_data (dict): Structured job posting data
            
        Returns:
            dict: Match score and detailed breakdown
        """
        # Initialize score components
        scores = {
            'skills': 0.0,
            'experience': 0.0,
            'education': 0.0,
            'title_relevance': 0.0,
            'location': 0.0,
            'total': 0.0
        }
        
        details = {
            'matched_skills': [],
            'missing_skills': [],
            'experience_match': False,
            'education_match': False,
            'location_match': False,
            'title_relevance': 0.0
        }
        
        # Calculate skills match
        scores['skills'], details['matched_skills'], details['missing_skills'] = self._calculate_skills_match(
            cv_data.get('skills', []),
            job_data.get('skills', [])
        )
        
        # Calculate experience match
        scores['experience'], details['experience_match'] = self._calculate_experience_match(
            cv_data.get('total_experience', 0),
            job_data.get('experience_required', 0)
        )
        
        # Calculate education match
        scores['education'], details['education_match'] = self._calculate_education_match(
            cv_data.get('education', []),
            job_data.get('education_required', '')
        )
        
        # Calculate title relevance
        scores['title_relevance'], details['title_relevance'] = self._calculate_title_relevance(
            cv_data.get('experience_details', []),
            job_data.get('title', '')
        )
        
        # Calculate location match
        scores['location'], details['location_match'] = self._calculate_location_match(
            cv_data.get('location', ''),
            job_data.get('location', ''),
            job_data.get('remote', False)
        )
        
        # Calculate total weighted score
        scores['total'] = sum(scores[key] * self.weights[key] for key in self.weights)
        
        # Format to percentage with two decimal places
        for key in scores:
            scores[key] = round(scores[key] * 100, 2)
        
        return {
            'scores': scores,
            'details': details
        }

    def _calculate_skills_match(
        self, 
        cv_skills: List[str], 
        job_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate match score based on skills.
        
        Args:
            cv_skills (list): Skills from CV
            job_skills (list): Skills required in job
            
        Returns:
            tuple: (match_score, matched_skills, missing_skills)
        """
        if not job_skills:
            return 1.0, cv_skills, []
            
        # Normalize all skills by lowercasing
        cv_skills_norm = [skill.lower() for skill in cv_skills]
        job_skills_norm = [skill.lower() for skill in job_skills]
        
        # Find matched and missing skills
        matched_skills = [skill for skill in job_skills if skill.lower() in cv_skills_norm]
        missing_skills = [skill for skill in job_skills if skill.lower() not in cv_skills_norm]
        
        # Calculate score
        if len(job_skills) == 0:
            return 1.0, matched_skills, missing_skills
            
        score = len(matched_skills) / len(job_skills)
        return score, matched_skills, missing_skills

    def _calculate_experience_match(
        self, 
        cv_experience: float, 
        job_experience_required: float
    ) -> Tuple[float, bool]:
        """
        Calculate match score based on experience.
        
        Args:
            cv_experience (float): Years of experience in CV
            job_experience_required (float): Years of experience required in job
            
        Returns:
            tuple: (score, is_match)
        """
        if job_experience_required <= 0:
            return 1.0, True
            
        if cv_experience >= job_experience_required:
            return 1.0, True
            
        # Partial matching if at least 80% of required experience
        if cv_experience >= job_experience_required * 0.8:
            ratio = cv_experience / job_experience_required
            return ratio, False
            
        return 0.0, False

    def _calculate_education_match(
        self, 
        cv_education: List[Dict[str, str]], 
        job_education_required: str
    ) -> Tuple[float, bool]:
        """
        Calculate match score based on education.
        
        Args:
            cv_education (list): Education entries from CV
            job_education_required (str): Education requirement from job
            
        Returns:
            tuple: (score, is_match)
        """
        if not job_education_required:
            return 1.0, True
            
        # Extract degrees from CV
        cv_degrees = []
        for edu in cv_education:
            degree = edu.get('degree', '').lower()
            field = edu.get('field', '').lower()
            
            cv_degrees.append(f"{degree} {field}".strip())
            
        # If no degrees found in CV
        if not cv_degrees:
            return 0.0, False
            
        # Preprocess the job education requirement
        job_edu_proc = self.preprocess_text(job_education_required)
        
        # Check for matches using TF-IDF and cosine similarity
        tfidf_vectorizer = TfidfVectorizer()
        
        # Combine all CV degrees for comparison
        all_cv_degrees = " ".join(cv_degrees)
        all_cv_degrees_proc = self.preprocess_text(all_cv_degrees)
        
        if not all_cv_degrees_proc or not job_edu_proc:
            return 0.5, False
            
        try:
            tfidf_matrix = tfidf_vectorizer.fit_transform([all_cv_degrees_proc, job_edu_proc])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Consider a match if similarity > 0.6
            return similarity, similarity > 0.6
        except:
            logger.warning("Could not calculate education similarity, returning partial match")
            return 0.5, False

    def _calculate_title_relevance(
        self, 
        cv_experience_details: List[Dict[str, str]], 
        job_title: str
    ) -> Tuple[float, float]:
        """
        Calculate match score based on job title relevance to past roles.
        
        Args:
            cv_experience_details (list): Work experience entries from CV
            job_title (str): Job title
            
        Returns:
            tuple: (score, relevance)
        """
        if not job_title or not cv_experience_details:
            return 0.5, 0.5
            
        # Preprocess job title
        job_title_proc = self.preprocess_text(job_title)
        
        # Get all previous titles from CV
        cv_titles = [exp.get('title', '') for exp in cv_experience_details]
        cv_titles_proc = [self.preprocess_text(title) for title in cv_titles if title]
        
        if not cv_titles_proc or not job_title_proc:
            return 0.5, 0.5
            
        # Calculate similarity between the job title and each CV title
        try:
            tfidf_vectorizer = TfidfVectorizer()
            all_titles = cv_titles_proc + [job_title_proc]
            tfidf_matrix = tfidf_vectorizer.fit_transform(all_titles)
            
            # Calculate similarity with each previous title
            similarities = []
            for i in range(len(cv_titles_proc)):
                similarity = cosine_similarity(
                    tfidf_matrix[i:i+1], 
                    tfidf_matrix[-1::]
                )[0][0]
                similarities.append(similarity)
            
            # Take the highest similarity as the score
            if similarities:
                max_similarity = max(similarities)
                return max_similarity, max_similarity
                
            return 0.5, 0.5
        except:
            logger.warning("Could not calculate title similarity, returning partial match")
            return 0.5, 0.5

    def _calculate_location_match(
        self, 
        cv_location: str, 
        job_location: str, 
        job_is_remote: bool
    ) -> Tuple[float, bool]:
        """
        Calculate match score based on location.
        
        Args:
            cv_location (str): Location from CV
            job_location (str): Location from job posting
            job_is_remote (bool): Whether the job is remote
            
        Returns:
            tuple: (score, is_match)
        """
        # If job is remote, location is a perfect match
        if job_is_remote:
            return 1.0, True
            
        if not cv_location or not job_location:
            return 0.5, False
            
        # Normalize locations by converting to lowercase and removing common words
        cv_loc_norm = cv_location.lower()
        job_loc_norm = job_location.lower()
        
        # First check: exact match on city or country level
        if cv_loc_norm == job_loc_norm:
            return 1.0, True
            
        # Second check: city or region is contained in the other
        if cv_loc_norm in job_loc_norm or job_loc_norm in cv_loc_norm:
            return 0.8, True
            
        # Third check: Extract components and check for overlap
        cv_loc_words = set(self.preprocess_text(cv_loc_norm).split())
        job_loc_words = set(self.preprocess_text(job_loc_norm).split())
        
        overlap = cv_loc_words.intersection(job_loc_words)
        
        if overlap:
            score = len(overlap) / max(len(cv_loc_words), len(job_loc_words))
            return score, score > 0.5
        
        # TODO: Use Google Maps API for more accurate location matching
        
        return 0.0, False

    def match_cv_to_job(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match a CV to a job, return score and details.
        
        Args:
            cv_data (dict): Structured CV data
            job_data (dict): Structured job posting data
            
        Returns:
            dict: Match results with score and details
        """
        logger.info(f"Matching CV to job: {job_data.get('title', 'Unknown position')}")
        
        match_results = self.calculate_match_score(cv_data, job_data)
        
        return {
            'cv': cv_data.get('personal_info', {}).get('name', 'Anonymous Candidate'),
            'job': job_data.get('title', 'Unknown position'),
            'match_score': match_results['scores']['total'],
            'match_details': match_results
        }

    def match_job_to_cv(self, job_data: Dict[str, Any], cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match a job to a CV, return score and details.
        
        Args:
            job_data (dict): Structured job posting data
            cv_data (dict): Structured CV data
            
        Returns:
            dict: Match results with score and details
        """
        logger.info(f"Matching job: {job_data.get('title', 'Unknown position')} to candidate")
        
        match_results = self.calculate_match_score(cv_data, job_data)
        
        return {
            'job': job_data.get('title', 'Unknown position'),
            'cv': cv_data.get('personal_info', {}).get('name', 'Anonymous Candidate'),
            'match_score': match_results['scores']['total'],
            'match_details': match_results
        }
