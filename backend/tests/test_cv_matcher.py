import pytest

from app.models.cv import CV, CVSkill, CVExperience, CVEducation
from app.models.job import JobPosition, JobRequirement
from app.services.cv_matcher import CVMatcherService


@pytest.fixture
def sample_cv():
    return CV(
        name="Jean Dupont",
        email="jean.dupont@example.com",
        position="Développeur Python Senior",
        skills=[
            CVSkill(name="Python"),
            CVSkill(name="FastAPI"),
            CVSkill(name="Docker"),
            CVSkill(name="PostgreSQL"),
            CVSkill(name="JavaScript"),
        ],
        softwares=["Python", "Docker", "PostgreSQL", "Git"],
        experiences=[
            CVExperience(
                title="Développeur Senior",
                company="Tech Corp",
                start_date="2018-01",
                end_date="2021-12",
                description="Développement backend avec Python"
            ),
            CVExperience(
                title="Développeur",
                company="Startup Inc",
                start_date="2015-03",
                end_date="2017-12",
                description="Développement full-stack"
            )
        ],
        education=[
            CVEducation(
                degree="Master en Informatique",
                institution="Université de Technologie",
                start_date="2011-09",
                end_date="2015-06"
            )
        ]
    )


@pytest.fixture
def sample_job():
    return JobPosition(
        title="Développeur Backend Senior",
        company="Solutions Entreprise",
        description="Nous recherchons un développeur backend expérimenté",
        required_skills=[
            JobRequirement(name="Python", importance=10),
            JobRequirement(name="FastAPI", importance=8),
            JobRequirement(name="MongoDB", importance=6),
            JobRequirement(name="Docker", importance=7)
        ],
        required_experience=3,
        required_education="Informatique",
        required_softwares=[
            JobRequirement(name="Python", importance=10),
            JobRequirement(name="Git", importance=5),
            JobRequirement(name="MongoDB", importance=6)
        ]
    )


@pytest.fixture
def cv_matcher_service():
    return CVMatcherService()


def test_match_cv_to_job(cv_matcher_service, sample_cv, sample_job):
    # Calcul du matching
    result = cv_matcher_service.match_cv_to_job(sample_cv, sample_job)
    
    # Assertions
    assert result.total_score > 0
    assert result.skills_score > 0
    assert result.software_score > 0
    assert result.experience_score > 0
    assert result.education_score > 0
    
    # Devrait trouver 3 compétences sur 4 requises
    assert len(result.missing_skills) == 1
    assert "MongoDB" in result.missing_skills
    
    # Devrait trouver 2 logiciels sur 3 requis
    assert len(result.missing_softwares) == 1
    assert "MongoDB" in result.missing_softwares


def test_match_cv_to_job_perfect_match(cv_matcher_service, sample_cv):
    # Création d'une offre d'emploi qui correspond parfaitement au CV
    perfect_job = JobPosition(
        title="Développeur Python Senior",
        company="Entreprise Tech",
        required_skills=[
            JobRequirement(name="Python", importance=10),
            JobRequirement(name="FastAPI", importance=8),
            JobRequirement(name="Docker", importance=7),
        ],
        required_experience=3,
        required_education="Informatique",
        required_softwares=[
            JobRequirement(name="Python", importance=10),
            JobRequirement(name="Git", importance=5),
        ]
    )
    
    # Calcul du matching
    result = cv_matcher_service.match_cv_to_job(sample_cv, perfect_job)
    
    # Assertions
    assert result.skills_score == 100.0
    assert result.software_score == 100.0
    assert result.education_score == 100.0
    assert len(result.missing_skills) == 0
    assert len(result.missing_softwares) == 0


def test_match_cv_to_job_no_match(cv_matcher_service, sample_cv):
    # Création d'une offre d'emploi qui ne correspond pas du tout au CV
    no_match_job = JobPosition(
        title="Architecte Java Enterprise",
        company="Entreprise Corp",
        required_skills=[
            JobRequirement(name="Java", importance=10),
            JobRequirement(name="Spring", importance=9),
            JobRequirement(name="Hibernate", importance=8),
        ],
        required_experience=10,
        required_education="Doctorat en Informatique",
        required_softwares=[
            JobRequirement(name="Java", importance=10),
            JobRequirement(name="Maven", importance=8),
            JobRequirement(name="Jenkins", importance=7),
        ]
    )
    
    # Calcul du matching
    result = cv_matcher_service.match_cv_to_job(sample_cv, no_match_job)
    
    # Assertions
    assert result.skills_score == 0.0
    assert result.software_score == 0.0
    assert result.education_score == 0.0
    assert len(result.missing_skills) == 3
    assert len(result.missing_softwares) == 3
