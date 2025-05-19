"""
Générateur de données synthétiques pour CV et offres d'emploi.

Ce module génère des datasets artificiels mais réalistes pour:
- Tests du système de matching
- Entraînement de modèles ML
- Benchmarking et évaluation
- Tests de régression
"""

import logging
import random
import string
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

from ..core.models import CV, JobOffer, MatchResult

logger = logging.getLogger(__name__)


class GenerationQuality(Enum):
    """Niveau de qualité de génération."""
    LOW = "low"           # Données basiques, moins de variété
    MEDIUM = "medium"     # Qualité standard
    HIGH = "high"         # Haute qualité, maximum de réalisme


@dataclass
class DatasetConfig:
    """Configuration pour la génération de datasets."""
    # Tailles
    num_cvs: int = 1000
    num_jobs: int = 500
    
    # Qualité et diversité
    quality_level: GenerationQuality = GenerationQuality.HIGH
    diversity_enabled: bool = True
    realism_level: float = 0.8  # 0-1, plus élevé = plus réaliste
    
    # Localisation et langue
    language: str = 'fr'
    primary_country: str = 'france'
    location_diversity: bool = True
    
    # Secteurs et compétences
    sectors: List[str] = field(default_factory=lambda: [
        'technology', 'finance', 'retail', 'healthcare', 'engineering',
        'education', 'consulting', 'logistics', 'creative', 'legal'
    ])
    
    # Biais intentionnels (pour testing)
    inject_bias: bool = False
    bias_types: List[str] = field(default_factory=list)
    bias_strength: float = 0.2  # 0-1
    
    # Patterns de matching
    generate_ground_truth: bool = True
    match_difficulty: str = 'medium'  # 'easy', 'medium', 'hard'
    
    # Seed pour reproductibilité
    seed: Optional[int] = None


class SyntheticDataGenerator:
    """
    Générateur de données synthétiques pour le système de matching.
    
    Génère des CV et offres d'emploi réalistes avec:
    - Diversité démographique contrôlée
    - Cohérence sectorielle
    - Variabilité de qualité
    - Patterns de matching complexes
    """
    
    def __init__(self, config: Optional[DatasetConfig] = None):
        """
        Initialise le générateur.
        
        Args:
            config: Configuration de génération
        """
        self.config = config or DatasetConfig()
        
        # Initialiser le seed
        if self.config.seed:
            random.seed(self.config.seed)
        
        # Charger les données de référence
        self.reference_data = self._load_reference_data()
        
        # Générateurs spécialisés
        self.cv_generator = CVGenerator(self.config, self.reference_data)
        self.job_generator = JobOfferGenerator(self.config, self.reference_data)
        
        # Cache pour cohérence
        self.generated_companies = {}
        self.skill_clusters = self._build_skill_clusters()
        
        logger.info(f"SyntheticDataGenerator initialized with {self.config.quality_level.value} quality")
    
    def generate_cvs(self, count: Optional[int] = None) -> List[CV]:
        """
        Génère une liste de CV synthétiques.
        
        Args:
            count: Nombre de CV à générer (défaut: config.num_cvs)
            
        Returns:
            Liste de CV générés
        """
        count = count or self.config.num_cvs
        
        logger.info(f"Generating {count} synthetic CVs...")
        
        cvs = []
        for i in range(count):
            cv = self.cv_generator.generate_single_cv(i)
            cvs.append(cv)
            
            if (i + 1) % 100 == 0:
                logger.debug(f"Generated {i + 1}/{count} CVs")
        
        # Post-processing pour cohérence globale
        cvs = self._post_process_cvs(cvs)
        
        logger.info(f"Successfully generated {len(cvs)} CVs")
        return cvs
    
    def generate_jobs(self, count: Optional[int] = None) -> List[JobOffer]:
        """
        Génère une liste d'offres d'emploi synthétiques.
        
        Args:
            count: Nombre d'offres à générer (défaut: config.num_jobs)
            
        Returns:
            Liste d'offres d'emploi générées
        """
        count = count or self.config.num_jobs
        
        logger.info(f"Generating {count} synthetic job offers...")
        
        jobs = []
        for i in range(count):
            job = self.job_generator.generate_single_job(i)
            jobs.append(job)
            
            if (i + 1) % 50 == 0:
                logger.debug(f"Generated {i + 1}/{count} jobs")
        
        # Post-processing pour cohérence
        jobs = self._post_process_jobs(jobs)
        
        logger.info(f"Successfully generated {len(jobs)} job offers")
        return jobs
    
    def generate_ground_truth_matches(self, 
                                    cvs: List[CV], 
                                    jobs: List[JobOffer],
                                    num_matches: Optional[int] = None) -> List[MatchResult]:
        """
        Génère des matches de vérité terrain basés sur des règles.
        
        Args:
            cvs: Liste des CV
            jobs: Liste des offres d'emploi
            num_matches: Nombre de matches à générer
            
        Returns:
            Liste de MatchResult avec scores de vérité terrain
        """
        logger.info("Generating ground truth matches...")
        
        if not self.config.generate_ground_truth:
            return []
        
        # Calculer des matches basés sur des règles déterministes
        matches = []
        
        for job in jobs:
            # Trouver les meilleurs candidats pour chaque job
            candidates_scores = []
            
            for cv in cvs:
                score = self._calculate_ground_truth_score(cv, job)
                if score > 0.3:  # Seuil minimum
                    candidates_scores.append((cv, score))
            
            # Trier et sélectionner les top matches
            candidates_scores.sort(key=lambda x: x[1], reverse=True)
            top_candidates = candidates_scores[:random.randint(3, 8)]
            
            for cv, score in top_candidates:
                # Ajouter du bruit au score pour le réalisme
                noisy_score = max(0.0, min(1.0, score + random.gauss(0, 0.05)))
                
                match = MatchResult(
                    candidate_id=cv.id,
                    job_id=job.id,
                    score=noisy_score,
                    explanation="Ground truth match based on synthetic rules",
                    timestamp=datetime.now(),
                    metadata={
                        'ground_truth': True,
                        'base_score': score,
                        'noise_added': noisy_score - score
                    }
                )
                matches.append(match)
        
        # Limiter le nombre si spécifié
        if num_matches and len(matches) > num_matches:
            matches = random.sample(matches, num_matches)
        
        # Trier par score décroissant
        matches.sort(key=lambda m: m.score, reverse=True)
        
        logger.info(f"Generated {len(matches)} ground truth matches")
        return matches
    
    def generate_benchmark_dataset(self, 
                                 name: str,
                                 scenarios: List[str]) -> Dict[str, Any]:
        """
        Génère un dataset de benchmark avec différents scenarios.
        
        Args:
            name: Nom du benchmark
            scenarios: Liste des scenarios à tester
            
        Returns:
            Dataset structuré pour benchmarking
        """
        logger.info(f"Generating benchmark dataset: {name}")
        
        benchmark_data = {
            'name': name,
            'created_at': datetime.now(),
            'config': self.config,
            'scenarios': {}
        }
        
        base_cvs = self.generate_cvs(500)  # Dataset de base
        base_jobs = self.generate_jobs(250)
        
        for scenario in scenarios:
            logger.info(f"Generating scenario: {scenario}")
            
            if scenario == 'balanced':
                # Dataset équilibré
                scenario_cvs = base_cvs
                scenario_jobs = base_jobs
            
            elif scenario == 'gender_imbalanced':
                # Déséquilibre de genre
                scenario_cvs = self._apply_gender_bias(base_cvs, bias_ratio=0.7)
                scenario_jobs = base_jobs
            
            elif scenario == 'skill_mismatch':
                # Mismatch de compétences volontaire
                scenario_cvs = base_cvs
                scenario_jobs = self._create_mismatched_jobs(base_jobs)
            
            elif scenario == 'location_diverse':
                # Forte diversité géographique
                scenario_cvs = self._increase_location_diversity(base_cvs)
                scenario_jobs = self._increase_location_diversity(base_jobs)
            
            elif scenario == 'experience_pyramid':
                # Distribution pyramidale d'expérience
                scenario_cvs = self._create_experience_pyramid(base_cvs)
                scenario_jobs = base_jobs
            
            elif scenario == 'tech_heavy':
                # Focus sur le secteur technologique
                scenario_cvs = self._filter_by_sector(base_cvs, 'technology', 0.6)
                scenario_jobs = self._filter_by_sector(base_jobs, 'technology', 0.7)
            
            else:
                # Scenario par défaut
                scenario_cvs = base_cvs[:200]
                scenario_jobs = base_jobs[:100]
            
            # Générer vérité terrain pour le scenario
            ground_truth = self.generate_ground_truth_matches(scenario_cvs, scenario_jobs)
            
            benchmark_data['scenarios'][scenario] = {
                'cvs': scenario_cvs,
                'jobs': scenario_jobs,
                'ground_truth': ground_truth,
                'stats': {
                    'num_cvs': len(scenario_cvs),
                    'num_jobs': len(scenario_jobs),
                    'num_matches': len(ground_truth),
                    'avg_match_score': sum(m.score for m in ground_truth) / len(ground_truth) if ground_truth else 0
                }
            }
        
        logger.info(f"Benchmark dataset '{name}' generated with {len(scenarios)} scenarios")
        return benchmark_data
    
    # Méthodes privées
    
    def _load_reference_data(self) -> Dict[str, Any]:
        """Charge les données de référence pour la génération."""
        return {
            'skills_by_sector': {
                'technology': [
                    'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'Docker',
                    'Kubernetes', 'AWS', 'Machine Learning', 'Data Science',
                    'DevOps', 'Agile', 'Git', 'SQL', 'NoSQL', 'TensorFlow'
                ],
                'finance': [
                    'Financial Analysis', 'Risk Management', 'Excel', 'Bloomberg',
                    'Derivatives', 'Portfolio Management', 'VBA', 'Python',
                    'Accounting', 'IFRS', 'Audit', 'Compliance', 'Trading'
                ],
                'retail': [
                    'Customer Service', 'Sales', 'Merchandising', 'CRM',
                    'Point of Sale', 'Inventory Management', 'Marketing',
                    'E-commerce', 'Visual Merchandising', 'Category Management'
                ],
                'healthcare': [
                    'Patient Care', 'Medical Records', 'Clinical Research',
                    'Pharmacy', 'Medical Imaging', 'EMR Systems', 'HIPAA',
                    'Healthcare Administration', 'Nursing', 'Laboratory'
                ],
                'engineering': [
                    'CAD', 'Project Management', 'AutoCAD', 'SolidWorks',
                    'Quality Control', 'Manufacturing', 'Lean Six Sigma',
                    'Technical Drawing', 'Materials Science', 'Safety Standards'
                ]
            },
            
            'job_titles_by_sector': {
                'technology': [
                    'Software Engineer', 'Data Scientist', 'DevOps Engineer',
                    'Product Manager', 'UX Designer', 'Frontend Developer',
                    'Backend Developer', 'Machine Learning Engineer', 'QA Engineer'
                ],
                'finance': [
                    'Financial Analyst', 'Risk Analyst', 'Investment Manager',
                    'Accountant', 'Auditor', 'Compliance Officer', 'Trader',
                    'Portfolio Manager', 'Financial Advisor'
                ],
                'retail': [
                    'Sales Associate', 'Store Manager', 'Merchandiser',
                    'Customer Service Representative', 'Category Manager',
                    'E-commerce Manager', 'Marketing Coordinator'
                ]
            },
            
            'companies_by_sector': {
                'technology': [
                    'TechCorp', 'InnovSoft', 'DataFlow Inc', 'CloudTech',
                    'AI Solutions', 'DevHub', 'CodeCraft', 'DigitalNext'
                ],
                'finance': [
                    'Capital Partners', 'InvestCorp', 'Financial Solutions',
                    'Asset Management', 'Risk Advisory', 'Trading House'
                ],
                'retail': [
                    'RetailChain', 'Fashion Hub', 'Commerce Plus',
                    'MarketLeader', 'Consumer Goods', 'Retail Solutions'
                ]
            },
            
            'france_cities': [
                'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes',
                'Strasbourg', 'Bordeaux', 'Lille', 'Rennes', 'Reims',
                'Saint-Étienne', 'Dijon', 'Grenoble', 'Angers', 'Nîmes'
            ],
            
            'education_institutions': [
                'Université Paris-Sorbonne', 'HEC Paris', 'École Polytechnique',
                'INSEAD', 'Sciences Po Paris', 'Université de Lyon',
                'Centrale Paris', 'École Normale Supérieure',
                'Université Toulouse', 'EDHEC Business School'
            ],
            
            'degree_types': [
                'Licence', 'Master', 'Doctorat', 'MBA', 'Ingénieur',
                'BTS', 'DUT', 'Magistère', 'Grande École'
            ]
        }
    
    def _build_skill_clusters(self) -> Dict[str, List[str]]:
        """Construit des clusters de compétences liées."""
        clusters = {
            'web_development': ['HTML', 'CSS', 'JavaScript', 'React', 'Vue.js', 'Angular'],
            'data_science': ['Python', 'R', 'Machine Learning', 'Statistics', 'TensorFlow', 'Pandas'],
            'cloud_computing': ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Terraform'],
            'project_management': ['Agile', 'Scrum', 'Kanban', 'JIRA', 'Project Planning'],
            'digital_marketing': ['SEO', 'SEM', 'Google Analytics', 'Social Media', 'Content Marketing']
        }
        return clusters
    
    def _calculate_ground_truth_score(self, cv: CV, job: JobOffer) -> float:
        """
        Calcule un score de vérité terrain basé sur des règles.
        
        Args:
            cv: CV candidat
            job: Offre d'emploi
            
        Returns:
            Score de matching 0-1
        """
        score_components = {}
        
        # Correspondance des compétences (40%)
        cv_skills = set(skill.lower() for skill in cv.skills)
        job_skills = set(skill.lower() for skill in job.required_skills)
        
        if job_skills:
            skills_match = len(cv_skills & job_skills) / len(job_skills)
        else:
            skills_match = 0.5  # Score neutre si pas de compétences spécifiées
        
        score_components['skills'] = skills_match * 0.4
        
        # Correspondance d'expérience (30%)
        if hasattr(cv, 'experience_years') and hasattr(job, 'required_experience'):
            exp_diff = abs(cv.experience_years - job.required_experience)
            exp_score = max(0, 1 - exp_diff / 10)  # Pénalité graduée
        else:
            exp_score = 0.7  # Score par défaut
        
        score_components['experience'] = exp_score * 0.3
        
        # Correspondance de secteur (20%)
        if hasattr(cv, 'sector') and hasattr(job, 'sector'):
            sector_score = 1.0 if cv.sector == job.sector else 0.3
        else:
            sector_score = 0.6
        
        score_components['sector'] = sector_score * 0.2
        
        # Correspondance géographique (10%)
        if hasattr(cv, 'location') and hasattr(job, 'location'):
            # Simplification: même ville = 1.0, même région = 0.7, sinon 0.3
            if cv.location == job.location:
                location_score = 1.0
            elif cv.location.split(',')[0] == job.location.split(',')[0]:  # Même région
                location_score = 0.7
            else:
                location_score = 0.3
        else:
            location_score = 0.5
        
        score_components['location'] = location_score * 0.1
        
        # Score final
        total_score = sum(score_components.values())
        
        # Ajouter de la variabilité basée sur la difficulté
        if self.config.match_difficulty == 'easy':
            total_score = min(1.0, total_score * 1.2)
        elif self.config.match_difficulty == 'hard':
            total_score = total_score * 0.8
        
        return round(total_score, 3)
    
    def _post_process_cvs(self, cvs: List[CV]) -> List[CV]:
        """Post-traite les CV pour cohérence globale."""
        # Assurer la diversité démographique
        if self.config.diversity_enabled:
            cvs = self._ensure_demographic_diversity(cvs)
        
        # Injection de biais si configuré
        if self.config.inject_bias:
            cvs = self._inject_bias_patterns(cvs)
        
        return cvs
    
    def _post_process_jobs(self, jobs: List[JobOffer]) -> List[JobOffer]:
        """Post-traite les offres d'emploi pour cohérence."""
        # Distribution sectorielle équilibrée
        sector_distribution = self._balance_sector_distribution(jobs)
        
        return jobs
    
    def _ensure_demographic_diversity(self, cvs: List[CV]) -> List[CV]:
        """Assure une diversité démographique dans les CV."""
        # Simplification: ajuster les attributs existants
        total_cvs = len(cvs)
        
        # Distribution de genre approximative (50-50 avec variation)
        gender_split = random.uniform(0.45, 0.55)
        female_count = int(total_cvs * gender_split)
        
        for i, cv in enumerate(cvs):
            # Assigner un genre de manière équilibrée (simulation)
            if i < female_count:
                cv.metadata = cv.metadata or {}
                cv.metadata['gender'] = 'female'
            else:
                cv.metadata = cv.metadata or {}
                cv.metadata['gender'] = 'male'
        
        return cvs
    
    def _inject_bias_patterns(self, cvs: List[CV]) -> List[CV]:
        """Injecte des patterns de biais spécifiques pour testing."""
        for bias_type in self.config.bias_types:
            if bias_type == 'gender_tech':
                # Sous-représenter les femmes en tech
                cvs = self._apply_gender_bias(cvs, bias_ratio=0.3)
            elif bias_type == 'age_senior':
                # Biais contre les seniors
                cvs = self._apply_age_bias(cvs)
            elif bias_type == 'education_privilege':
                # Privilège pour les grandes écoles
                cvs = self._apply_education_bias(cvs)
        
        return cvs
    
    def _apply_gender_bias(self, cvs: List[CV], bias_ratio: float = 0.3) -> List[CV]:
        """Applique un biais de genre."""
        tech_cvs = [cv for cv in cvs if getattr(cv, 'sector', None) == 'technology']
        
        # Modifier la représentation féminine en tech
        for cv in tech_cvs:
            if random.random() > bias_ratio:
                cv.metadata = cv.metadata or {}
                cv.metadata['gender'] = 'male'
        
        return cvs
    
    def _apply_age_bias(self, cvs: List[CV]) -> List[CV]:
        """Applique un biais d'âge."""
        # Les seniors ont moins d'opportunités dans certains secteurs
        for cv in cvs:
            if hasattr(cv, 'age') and cv.age > 50:
                # Réduire artificiellement leurs compétences "modernes"
                modern_skills = ['React', 'Machine Learning', 'Docker', 'Kubernetes']
                cv.skills = [s for s in cv.skills if s not in modern_skills]
        
        return cvs
    
    def _apply_education_bias(self, cvs: List[CV]) -> List[CV]:
        """Applique un biais éducationnel."""
        # Favoriser les diplômés de grandes écoles
        prestigious_schools = ['HEC Paris', 'École Polytechnique', 'INSEAD']
        
        for cv in cvs:
            if hasattr(cv, 'education') and cv.education:
                for edu in cv.education:
                    if edu.institution in prestigious_schools:
                        # Booster artificiellement leurs compétences
                        cv.skills.extend(['Leadership', 'Strategic Planning', 'Business Development'])
                        break
        
        return cvs
    
    def _balance_sector_distribution(self, jobs: List[JobOffer]) -> Dict[str, int]:
        """Équilibre la distribution sectorielle."""
        sector_counts = defaultdict(int)
        for job in jobs:
            if hasattr(job, 'sector'):
                sector_counts[job.sector] += 1
        
        return dict(sector_counts)
    
    # Méthodes pour les scenarios de benchmark
    
    def _create_mismatched_jobs(self, jobs: List[JobOffer]) -> List[JobOffer]:
        """Crée des jobs avec mismatch volontaire."""
        for job in jobs[:len(jobs)//2]:  # 50% des jobs
            # Mélanger les compétences entre secteurs
            random_sector = random.choice(list(self.reference_data['skills_by_sector'].keys()))
            random_skills = random.sample(
                self.reference_data['skills_by_sector'][random_sector], 
                min(5, len(self.reference_data['skills_by_sector'][random_sector]))
            )
            job.required_skills = random_skills
        
        return jobs
    
    def _increase_location_diversity(self, data_list: List) -> List:
        """Augmente la diversité géographique."""
        cities = self.reference_data['france_cities']
        
        for item in data_list:
            if hasattr(item, 'location'):
                # Répartir plus uniformément sur toutes les villes
                item.location = random.choice(cities)
        
        return data_list
    
    def _create_experience_pyramid(self, cvs: List[CV]) -> List[CV]:
        """Crée une distribution pyramidale d'expérience."""
        # 50% junior (0-3 ans), 30% mid (4-8 ans), 20% senior (9+ ans)
        total = len(cvs)
        
        for i, cv in enumerate(cvs):
            if i < total * 0.5:
                exp_years = random.randint(0, 3)
            elif i < total * 0.8:
                exp_years = random.randint(4, 8)
            else:
                exp_years = random.randint(9, 20)
            
            cv.experience_years = exp_years
        
        return cvs
    
    def _filter_by_sector(self, data_list: List, sector: str, ratio: float) -> List:
        """Filtre pour concentrer sur un secteur."""
        sector_items = [item for item in data_list if getattr(item, 'sector', None) == sector]
        other_items = [item for item in data_list if getattr(item, 'sector', None) != sector]
        
        # Garder ratio% du secteur et compléter avec les autres
        target_sector_count = int(len(data_list) * ratio)
        target_other_count = len(data_list) - target_sector_count
        
        result = sector_items[:target_sector_count]
        result.extend(other_items[:target_other_count])
        
        return result


class CVGenerator:
    """Générateur spécialisé pour les CV."""
    
    def __init__(self, config: DatasetConfig, reference_data: Dict[str, Any]):
        self.config = config
        self.reference_data = reference_data
    
    def generate_single_cv(self, index: int) -> CV:
        """Génère un CV synthétique."""
        # Choisir un secteur
        sector = random.choice(self.config.sectors)
        
        # Informations personnelles
        first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Antoine', 'Julie', 'Nicolas', 'Emma']
        last_names = ['Dupont', 'Martin', 'Bernard', 'Durand', 'Lemoine', 'Garcia']
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Générer ID unique
        cv_id = f"cv_{index}_{hashlib.md5(f'{first_name}{last_name}{index}'.encode()).hexdigest()[:8]}"
        
        # Compétences basées sur le secteur
        sector_skills = self.reference_data['skills_by_sector'].get(sector, [])
        num_skills = random.randint(3, min(10, len(sector_skills)))
        skills = random.sample(sector_skills, num_skills)
        
        # Ajouter quelques compétences transversales
        transversal_skills = ['Communication', 'Teamwork', 'Problem Solving', 'Time Management']
        skills.extend(random.sample(transversal_skills, random.randint(1, 3)))
        
        # Expérience
        experience_years = random.randint(0, 25)
        
        # Éducation
        institution = random.choice(self.reference_data['education_institutions'])
        degree = random.choice(self.reference_data['degree_types'])
        
        education = [{
            'institution': institution,
            'degree': degree,
            'field': sector.title(),
            'year': 2024 - random.randint(1, 10)
        }]
        
        # Localisation
        location = random.choice(self.reference_data['france_cities'])
        
        # Créer le CV
        cv = CV(
            id=cv_id,
            personal_info={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{first_name.lower()}.{last_name.lower()}@email.com",
                'phone': f"0{random.randint(100000000, 999999999)}"
            },
            skills=skills,
            experience=self._generate_experience(sector, experience_years),
            education=education,
            metadata={
                'sector': sector,
                'experience_years': experience_years,
                'location': location,
                'generation_index': index,
                'age': random.randint(22, 65)
            }
        )
        
        return cv
    
    def _generate_experience(self, sector: str, years: int) -> List[Dict[str, Any]]:
        """Génère l'expérience professionnelle."""
        if years == 0:
            return []
        
        experience = []
        current_year = 2024
        remaining_years = years
        
        # Générer 1-4 postes selon l'expérience
        num_jobs = min(4, max(1, years // 3))
        
        job_titles = self.reference_data['job_titles_by_sector'].get(sector, ['Consultant'])
        companies = self.reference_data['companies_by_sector'].get(sector, ['Generic Corp'])
        
        for i in range(num_jobs):
            job_years = random.randint(1, min(8, remaining_years))
            
            experience.append({
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'duration_years': job_years,
                'start_year': current_year - remaining_years,
                'end_year': current_year - remaining_years + job_years,
                'description': f"Professional experience in {sector}"
            })
            
            remaining_years -= job_years
            if remaining_years <= 0:
                break
        
        return experience


class JobOfferGenerator:
    """Générateur spécialisé pour les offres d'emploi."""
    
    def __init__(self, config: DatasetConfig, reference_data: Dict[str, Any]):
        self.config = config
        self.reference_data = reference_data
    
    def generate_single_job(self, index: int) -> JobOffer:
        """Génère une offre d'emploi synthétique."""
        # Secteur et titre
        sector = random.choice(self.config.sectors)
        job_titles = self.reference_data['job_titles_by_sector'].get(sector, ['Specialist'])
        title = random.choice(job_titles)
        
        # ID unique
        job_id = f"job_{index}_{hashlib.md5(f'{title}{sector}{index}'.encode()).hexdigest()[:8]}"
        
        # Compétences requises
        sector_skills = self.reference_data['skills_by_sector'].get(sector, [])
        num_required_skills = random.randint(3, min(8, len(sector_skills)))
        required_skills = random.sample(sector_skills, num_required_skills)
        
        # Compétences optionnelles
        optional_skills = [
            skill for skill in sector_skills 
            if skill not in required_skills
        ][:random.randint(1, 4)]
        
        # Expérience requise
        required_experience = random.randint(0, 15)
        
        # Entreprise
        companies = self.reference_data['companies_by_sector'].get(sector, ['Global Corp'])
        company = random.choice(companies)
        
        # Localisation
        location = random.choice(self.reference_data['france_cities'])
        
        # Salaire (optionnel)
        base_salary = {
            'technology': random.randint(35000, 100000),
            'finance': random.randint(30000, 120000),
            'retail': random.randint(25000, 60000),
            'healthcare': random.randint(30000, 80000),
            'engineering': random.randint(35000, 90000)
        }.get(sector, random.randint(30000, 70000))
        
        salary_range = {
            'min': base_salary,
            'max': int(base_salary * random.uniform(1.1, 1.5))
        }
        
        # Créer l'offre
        job = JobOffer(
            id=job_id,
            title=title,
            company=company,
            description=f"Great opportunity in {sector} for {title} position",
            required_skills=required_skills,
            optional_skills=optional_skills,
            location=location,
            employment_type=random.choice(['full_time', 'part_time', 'contract', 'internship']),
            salary_range=salary_range,
            metadata={
                'sector': sector,
                'required_experience': required_experience,
                'posting_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'generation_index': index
            }
        )
        
        return job
