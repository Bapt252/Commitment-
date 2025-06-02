"""
SuperSmartMatch V2 - Unified Models

Unified data models that bridge between legacy algorithms and V2 enhancements
while maintaining compatibility with existing 40K lines Nexten Matcher.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AlgorithmType(Enum):
    """Available matching algorithms"""
    NEXTEN = "nexten"
    SMART = "smart" 
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContractType(Enum):
    """Employment contract types"""
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"

@dataclass
class MatchingContext:
    """Context information for intelligent algorithm selection"""
    candidate_skills: List[str] = field(default_factory=list)
    candidate_experience: int = 0  # years
    locations: List[str] = field(default_factory=list)
    mobility_constraints: str = "flexible"
    questionnaire_completeness: float = 0.0
    company_questionnaires_completeness: float = 0.0
    has_geographic_constraints: bool = False
    requires_semantic_analysis: bool = False
    requires_validation: bool = False
    critical_match: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'candidate_skills': self.candidate_skills,
            'candidate_experience': self.candidate_experience,
            'locations': self.locations,
            'mobility_constraints': self.mobility_constraints,
            'questionnaire_completeness': self.questionnaire_completeness,
            'company_questionnaires_completeness': self.company_questionnaires_completeness,
            'has_geographic_constraints': self.has_geographic_constraints,
            'requires_semantic_analysis': self.requires_semantic_analysis,
            'requires_validation': self.requires_validation,
            'critical_match': self.critical_match
        }

@dataclass
class Skill:
    """Unified skill representation"""
    name: str
    level: SkillLevel = SkillLevel.INTERMEDIATE
    years_experience: int = 1
    category: str = "technical"
    verified: bool = False
    certifications: List[str] = field(default_factory=list)
    last_used: Optional[str] = None
    proficiency_score: float = 0.5  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'level': self.level.value,
            'years_experience': self.years_experience,
            'category': self.category,
            'verified': self.verified,
            'certifications': self.certifications,
            'last_used': self.last_used,
            'proficiency_score': self.proficiency_score
        }

@dataclass
class Experience:
    """Unified work experience representation"""
    company: str
    position: str
    duration_months: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str = ""
    skills_used: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    sector: str = ""
    team_size: int = 0
    technologies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'company': self.company,
            'position': self.position,
            'duration_months': self.duration_months,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description': self.description,
            'skills_used': self.skills_used,
            'achievements': self.achievements,
            'responsibilities': self.responsibilities,
            'sector': self.sector,
            'team_size': self.team_size,
            'technologies': self.technologies
        }

@dataclass
class Education:
    """Unified education representation"""
    degree: str
    field: str
    institution: str
    graduation_year: int
    grade: str = ""
    honors: List[str] = field(default_factory=list)
    relevant_courses: List[str] = field(default_factory=list)
    thesis_topic: str = ""
    gpa: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'degree': self.degree,
            'field': self.field,
            'institution': self.institution,
            'graduation_year': self.graduation_year,
            'grade': self.grade,
            'honors': self.honors,
            'relevant_courses': self.relevant_courses,
            'thesis_topic': self.thesis_topic,
            'gpa': self.gpa
        }

@dataclass
class Location:
    """Unified location representation"""
    city: str = ""
    country: str = ""
    region: str = ""
    postal_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "UTC"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'city': self.city,
            'country': self.country,
            'region': self.region,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone
        }

@dataclass
class CandidateProfile:
    """Unified candidate profile for V2"""
    id: str
    name: str
    email: str
    
    # Skills and experience
    technical_skills: List[Skill] = field(default_factory=list)
    soft_skills: List[Skill] = field(default_factory=list)
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    
    # Personal information
    location: Optional[Location] = None
    languages: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    
    # Preferences
    mobility_preferences: str = "flexible"
    remote_work_preference: str = "hybrid"
    availability: str = "immediate"
    salary_expectation: Optional[Dict[str, Any]] = None
    
    # V2 Enhanced fields
    questionnaire_responses: Optional[Dict[str, Any]] = None
    personality_insights: Optional[Dict[str, Any]] = None
    career_goals: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'technical_skills': [skill.to_dict() for skill in self.technical_skills],
            'soft_skills': [skill.to_dict() for skill in self.soft_skills],
            'experiences': [exp.to_dict() for exp in self.experiences],
            'education': [edu.to_dict() for edu in self.education],
            'location': self.location.to_dict() if self.location else None,
            'languages': self.languages,
            'certifications': self.certifications,
            'mobility_preferences': self.mobility_preferences,
            'remote_work_preference': self.remote_work_preference,
            'availability': self.availability,
            'salary_expectation': self.salary_expectation,
            'questionnaire_responses': self.questionnaire_responses,
            'personality_insights': self.personality_insights,
            'career_goals': self.career_goals,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills (technical + soft)"""
        return self.technical_skills + self.soft_skills
    
    def get_total_experience_years(self) -> int:
        """Calculate total experience in years"""
        total_months = sum(exp.duration_months for exp in self.experiences)
        return total_months // 12
    
    def has_skill(self, skill_name: str) -> bool:
        """Check if candidate has specific skill"""
        all_skills = self.get_all_skills()
        return any(skill.name.lower() == skill_name.lower() for skill in all_skills)

@dataclass
class CompanyOffer:
    """Unified company offer for V2"""
    id: str
    company_name: str
    position_title: str
    
    # Requirements
    required_skills: List[Skill] = field(default_factory=list)
    preferred_skills: List[Skill] = field(default_factory=list)
    experience_requirements: Dict[str, Any] = field(default_factory=dict)
    education_requirements: Optional[Education] = None
    
    # Job details
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    
    # Location and work setup
    location: Optional[Location] = None
    remote_policy: str = "office"  # office, remote, hybrid
    travel_requirements: str = "none"
    
    # Employment details
    contract_type: ContractType = ContractType.PERMANENT
    salary_range: Optional[Dict[str, Any]] = None
    working_hours: str = "full-time"
    
    # Company information
    company_size: str = ""
    sector: str = ""
    company_culture: Dict[str, Any] = field(default_factory=dict)
    
    # V2 Enhanced fields
    company_questionnaire: Optional[Dict[str, Any]] = None
    hiring_urgency: str = "normal"  # low, normal, high, urgent
    team_composition: Dict[str, Any] = field(default_factory=dict)
    growth_opportunities: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'position_title': self.position_title,
            'required_skills': [skill.to_dict() for skill in self.required_skills],
            'preferred_skills': [skill.to_dict() for skill in self.preferred_skills],
            'experience_requirements': self.experience_requirements,
            'education_requirements': self.education_requirements.to_dict() if self.education_requirements else None,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'location': self.location.to_dict() if self.location else None,
            'remote_policy': self.remote_policy,
            'travel_requirements': self.travel_requirements,
            'contract_type': self.contract_type.value,
            'salary_range': self.salary_range,
            'working_hours': self.working_hours,
            'company_size': self.company_size,
            'sector': self.sector,
            'company_culture': self.company_culture,
            'company_questionnaire': self.company_questionnaire,
            'hiring_urgency': self.hiring_urgency,
            'team_composition': self.team_composition,
            'growth_opportunities': self.growth_opportunities,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'expires_at': self.expires_at
        }
    
    def get_all_required_skills(self) -> List[Skill]:
        """Get all required skills"""
        return self.required_skills
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills (required + preferred)"""
        return self.required_skills + self.preferred_skills

@dataclass
class MatchingConfig:
    """Unified matching configuration"""
    algorithm: str = "auto"
    
    # Scoring weights
    skill_weight: float = 0.4
    experience_weight: float = 0.3
    location_weight: float = 0.2
    culture_weight: float = 0.1
    questionnaire_weight: float = 0.0
    
    # Performance settings
    max_results: int = 50
    min_score_threshold: float = 0.0
    enable_explanations: bool = True
    enable_recommendations: bool = True
    
    # Algorithm-specific settings
    enable_semantic_analysis: bool = True
    enable_geographical_optimization: bool = True
    enable_questionnaire_matching: bool = True
    
    # V2 Enhanced settings
    enable_fallback: bool = True
    enable_caching: bool = True
    custom_weights: Optional[Dict[str, float]] = None
    context_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'algorithm': self.algorithm,
            'skill_weight': self.skill_weight,
            'experience_weight': self.experience_weight,
            'location_weight': self.location_weight,
            'culture_weight': self.culture_weight,
            'questionnaire_weight': self.questionnaire_weight,
            'max_results': self.max_results,
            'min_score_threshold': self.min_score_threshold,
            'enable_explanations': self.enable_explanations,
            'enable_recommendations': self.enable_recommendations,
            'enable_semantic_analysis': self.enable_semantic_analysis,
            'enable_geographical_optimization': self.enable_geographical_optimization,
            'enable_questionnaire_matching': self.enable_questionnaire_matching,
            'enable_fallback': self.enable_fallback,
            'enable_caching': self.enable_caching,
            'custom_weights': self.custom_weights,
            'context_data': self.context_data
        }

@dataclass
class SkillMatch:
    """Detailed skill matching information"""
    skill_name: str
    candidate_level: str
    required_level: str
    match_score: float
    gap_analysis: str = ""
    recommendations: List[str] = field(default_factory=list)

@dataclass
class MatchingResult:
    """Unified matching result"""
    # Core identification
    offer_id: str
    candidate_id: str
    
    # Overall scoring
    overall_score: float
    confidence: float
    
    # Detailed breakdown
    skill_match_score: float
    experience_match_score: float
    location_match_score: float
    culture_match_score: float
    questionnaire_match_score: Optional[float] = None
    
    # Detailed analysis
    matched_skills: List[SkillMatch] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    experience_analysis: Dict[str, Any] = field(default_factory=dict)
    location_analysis: Dict[str, Any] = field(default_factory=dict)
    culture_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # V2 Enhanced insights
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    growth_potential: str = ""
    
    # Algorithm metadata
    algorithm_used: str = ""
    processing_time_ms: float = 0.0
    explanation: str = ""
    debug_info: Optional[Dict[str, Any]] = None
    
    # Legacy compatibility fields
    match_score: Optional[float] = None  # For V1 compatibility
    confidence_score: Optional[float] = None  # For V1 compatibility
    
    def __post_init__(self):
        # Ensure legacy compatibility
        if self.match_score is None:
            self.match_score = self.overall_score
        if self.confidence_score is None:
            self.confidence_score = self.confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility"""
        return {
            'offer_id': self.offer_id,
            'candidate_id': self.candidate_id,
            'overall_score': self.overall_score,
            'confidence': self.confidence,
            'skill_match_score': self.skill_match_score,
            'experience_match_score': self.experience_match_score,
            'location_match_score': self.location_match_score,
            'culture_match_score': self.culture_match_score,
            'questionnaire_match_score': self.questionnaire_match_score,
            'matched_skills': [
                {
                    'skill_name': sm.skill_name,
                    'candidate_level': sm.candidate_level,
                    'required_level': sm.required_level,
                    'match_score': sm.match_score,
                    'gap_analysis': sm.gap_analysis,
                    'recommendations': sm.recommendations
                } for sm in self.matched_skills
            ],
            'missing_skills': self.missing_skills,
            'experience_analysis': self.experience_analysis,
            'location_analysis': self.location_analysis,
            'culture_analysis': self.culture_analysis,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'risk_factors': self.risk_factors,
            'growth_potential': self.growth_potential,
            'algorithm_used': self.algorithm_used,
            'processing_time_ms': self.processing_time_ms,
            'explanation': self.explanation,
            'debug_info': self.debug_info,
            # Legacy compatibility
            'match_score': self.match_score,
            'confidence_score': self.confidence_score
        }
    
    def get_score_breakdown(self) -> Dict[str, float]:
        """Get detailed score breakdown"""
        return {
            'overall': self.overall_score,
            'skills': self.skill_match_score,
            'experience': self.experience_match_score,
            'location': self.location_match_score,
            'culture': self.culture_match_score,
            'questionnaire': self.questionnaire_match_score or 0.0
        }

# Helper functions for model conversion

def dict_to_candidate_profile(data: Dict[str, Any]) -> CandidateProfile:
    """Convert dictionary to CandidateProfile"""
    
    # Convert skills
    technical_skills = []
    for skill_data in data.get('technical_skills', []):
        if isinstance(skill_data, str):
            technical_skills.append(Skill(name=skill_data))
        else:
            technical_skills.append(Skill(
                name=skill_data['name'],
                level=SkillLevel(skill_data.get('level', 'intermediate')),
                years_experience=skill_data.get('years_experience', 1),
                category=skill_data.get('category', 'technical'),
                verified=skill_data.get('verified', False),
                certifications=skill_data.get('certifications', []),
                last_used=skill_data.get('last_used'),
                proficiency_score=skill_data.get('proficiency_score', 0.5)
            ))
    
    soft_skills = []
    for skill_data in data.get('soft_skills', []):
        if isinstance(skill_data, str):
            soft_skills.append(Skill(name=skill_data, category='soft'))
        else:
            soft_skills.append(Skill(
                name=skill_data['name'],
                level=SkillLevel(skill_data.get('level', 'intermediate')),
                years_experience=skill_data.get('years_experience', 1),
                category='soft',
                verified=skill_data.get('verified', False),
                certifications=skill_data.get('certifications', []),
                last_used=skill_data.get('last_used'),
                proficiency_score=skill_data.get('proficiency_score', 0.5)
            ))
    
    # Convert experiences
    experiences = []
    for exp_data in data.get('experiences', []):
        experiences.append(Experience(
            company=exp_data['company'],
            position=exp_data['position'],
            duration_months=exp_data['duration_months'],
            start_date=exp_data.get('start_date'),
            end_date=exp_data.get('end_date'),
            description=exp_data.get('description', ''),
            skills_used=exp_data.get('skills_used', []),
            achievements=exp_data.get('achievements', []),
            responsibilities=exp_data.get('responsibilities', []),
            sector=exp_data.get('sector', ''),
            team_size=exp_data.get('team_size', 0),
            technologies=exp_data.get('technologies', [])
        ))
    
    # Convert education
    education = []
    for edu_data in data.get('education', []):
        education.append(Education(
            degree=edu_data['degree'],
            field=edu_data['field'],
            institution=edu_data['institution'],
            graduation_year=edu_data['graduation_year'],
            grade=edu_data.get('grade', ''),
            honors=edu_data.get('honors', []),
            relevant_courses=edu_data.get('relevant_courses', []),
            thesis_topic=edu_data.get('thesis_topic', ''),
            gpa=edu_data.get('gpa', 0.0)
        ))
    
    # Convert location
    location = None
    if data.get('location'):
        loc_data = data['location']
        location = Location(
            city=loc_data.get('city', ''),
            country=loc_data.get('country', ''),
            region=loc_data.get('region', ''),
            postal_code=loc_data.get('postal_code', ''),
            latitude=loc_data.get('latitude'),
            longitude=loc_data.get('longitude'),
            timezone=loc_data.get('timezone', 'UTC')
        )
    
    return CandidateProfile(
        id=data['id'],
        name=data['name'],
        email=data['email'],
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        experiences=experiences,
        education=education,
        location=location,
        languages=data.get('languages', []),
        certifications=data.get('certifications', []),
        mobility_preferences=data.get('mobility_preferences', 'flexible'),
        remote_work_preference=data.get('remote_work_preference', 'hybrid'),
        availability=data.get('availability', 'immediate'),
        salary_expectation=data.get('salary_expectation'),
        questionnaire_responses=data.get('questionnaire_responses'),
        personality_insights=data.get('personality_insights'),
        career_goals=data.get('career_goals', []),
        created_at=data.get('created_at'),
        updated_at=data.get('updated_at')
    )

def dict_to_company_offer(data: Dict[str, Any]) -> CompanyOffer:
    """Convert dictionary to CompanyOffer"""
    
    # Convert required skills
    required_skills = []
    for skill_data in data.get('required_skills', []):
        if isinstance(skill_data, str):
            required_skills.append(Skill(name=skill_data))
        else:
            required_skills.append(Skill(
                name=skill_data['name'],
                level=SkillLevel(skill_data.get('level', 'intermediate')),
                years_experience=skill_data.get('years_experience', 1),
                category=skill_data.get('category', 'technical')
            ))
    
    # Convert preferred skills
    preferred_skills = []
    for skill_data in data.get('preferred_skills', []):
        if isinstance(skill_data, str):
            preferred_skills.append(Skill(name=skill_data))
        else:
            preferred_skills.append(Skill(
                name=skill_data['name'],
                level=SkillLevel(skill_data.get('level', 'intermediate')),
                years_experience=skill_data.get('years_experience', 1),
                category=skill_data.get('category', 'technical')
            ))
    
    # Convert location
    location = None
    if data.get('location'):
        loc_data = data['location']
        location = Location(
            city=loc_data.get('city', ''),
            country=loc_data.get('country', ''),
            region=loc_data.get('region', ''),
            postal_code=loc_data.get('postal_code', ''),
            latitude=loc_data.get('latitude'),
            longitude=loc_data.get('longitude'),
            timezone=loc_data.get('timezone', 'UTC')
        )
    
    return CompanyOffer(
        id=data['id'],
        company_name=data['company_name'],
        position_title=data['position_title'],
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_requirements=data.get('experience_requirements', {}),
        description=data.get('description', ''),
        requirements=data.get('requirements', []),
        responsibilities=data.get('responsibilities', []),
        benefits=data.get('benefits', []),
        location=location,
        remote_policy=data.get('remote_policy', 'office'),
        travel_requirements=data.get('travel_requirements', 'none'),
        contract_type=ContractType(data.get('contract_type', 'permanent')),
        salary_range=data.get('salary_range'),
        working_hours=data.get('working_hours', 'full-time'),
        company_size=data.get('company_size', ''),
        sector=data.get('sector', ''),
        company_culture=data.get('company_culture', {}),
        company_questionnaire=data.get('company_questionnaire'),
        hiring_urgency=data.get('hiring_urgency', 'normal'),
        team_composition=data.get('team_composition', {}),
        growth_opportunities=data.get('growth_opportunities', []),
        created_at=data.get('created_at'),
        updated_at=data.get('updated_at'),
        expires_at=data.get('expires_at')
    )
