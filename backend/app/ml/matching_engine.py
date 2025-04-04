import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configurer le logging
logger = logging.getLogger(__name__)

async def generate_matches(
    job_post_id: int, 
    candidate_ids: List[int], 
    min_score: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Génère des matchings entre une fiche de poste et plusieurs candidats.
    Utilise les modèles ML pour calculer les scores de correspondance.
    """
    results = []
    
    try:
        # Récupérer les données de la fiche de poste depuis la base de données
        job_post = get_mock_job_post(job_post_id)
        
        for candidate_id in candidate_ids:
            # Récupérer les données du candidat
            candidate = get_mock_candidate(candidate_id)
            
            # Calculer les scores de matching par catégorie
            skill_score = calculate_skill_match(job_post, candidate)
            experience_score = calculate_experience_match(job_post, candidate)
            education_score = calculate_education_match(job_post, candidate)
            
            # Calculer le score global (pondéré selon l'importance de chaque catégorie)
            weights = {"skills": 0.5, "experience": 0.3, "education": 0.2}
            overall_score = (
                skill_score * weights["skills"] +
                experience_score * weights["experience"] +
                education_score * weights["education"]
            )
            
            # Ne retenir que les matchings au-dessus du score minimum
            if overall_score >= min_score:
                # Créer les détails du score
                score_details = [
                    {
                        "category": "skills",
                        "score": skill_score,
                        "explanation": "Évaluation basée sur les compétences techniques requises"
                    },
                    {
                        "category": "experience",
                        "score": experience_score,
                        "explanation": "Évaluation basée sur l'expérience professionnelle"
                    },
                    {
                        "category": "education",
                        "score": education_score,
                        "explanation": "Évaluation basée sur la formation et les diplômes"
                    }
                ]
                
                # Identifier les forces et faiblesses
                strengths = identify_strengths(job_post, candidate)
                gaps = identify_gaps(job_post, candidate)
                
                # Générer des recommandations personnalisées
                recommendations = generate_recommendations(job_post, candidate, gaps)
                
                # Créer le résultat final
                result = {
                    "job_post_id": job_post_id,
                    "candidate_id": candidate_id,
                    "overall_score": overall_score,
                    "score_details": score_details,
                    "strengths": strengths,
                    "gaps": gaps,
                    "recommendations": recommendations,
                    "created_at": datetime.now().isoformat()
                }
                
                results.append(result)
        
        logger.info(f"Matching généré pour la fiche de poste {job_post_id} et {len(results)} candidats")
        return results
    except Exception as e:
        logger.error(f"Erreur lors de la génération des matchings: {str(e)}")
        raise

def get_mock_job_post(job_post_id: int) -> Dict[str, Any]:
    """
    Simule la récupération d'une fiche de poste depuis la base de données.
    Dans une implémentation réelle, cette fonction interrogerait la base de données.
    """
    # Fiche de poste pour un développeur Python
    if job_post_id == 1:
        return {
            "id": 1,
            "title": "Développeur Python Sénior",
            "description": "Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe.",
            "company": "TechCorp",
            "location": "Paris",
            "contract_type": "CDI",
            "salary_range": "55K-70K€",
            "required_skills": [
                {"name": "Python", "level": 4, "required": True},
                {"name": "Django", "level": 3, "required": True},
                {"name": "SQL", "level": 3, "required": True},
                {"name": "Git", "level": 3, "required": True},
                {"name": "Docker", "level": 2, "required": False},
                {"name": "AWS", "level": 2, "required": False}
            ],
            "required_experience": {
                "min_years": 5,
                "domains": ["développement web", "backend", "API REST"],
                "description": "Expérience significative en développement d'applications web avec Python"
            },
            "required_education": {
                "level": "Bac+5",
                "domains": ["informatique", "génie logiciel", "mathématiques appliquées"],
                "required": True
            }
        }
    # Fiche de poste pour un data scientist
    elif job_post_id == 2:
        return {
            "id": 2,
            "title": "Data Scientist",
            "description": "Rejoignez notre équipe de data science pour travailler sur des projets innovants.",
            "company": "DataInsight",
            "location": "Lyon",
            "contract_type": "CDI",
            "salary_range": "50K-65K€",
            "required_skills": [
                {"name": "Python", "level": 4, "required": True},
                {"name": "Machine Learning", "level": 4, "required": True},
                {"name": "SQL", "level": 3, "required": True},
                {"name": "Pandas", "level": 4, "required": True},
                {"name": "TensorFlow", "level": 3, "required": False},
                {"name": "Data Visualization", "level": 3, "required": False}
            ],
            "required_experience": {
                "min_years": 3,
                "domains": ["data science", "machine learning", "analyse de données"],
                "description": "Expérience en conception et déploiement de modèles ML"
            },
            "required_education": {
                "level": "Bac+5",
                "domains": ["informatique", "data science", "statistiques", "mathématiques"],
                "required": True
            }
        }
    # Fiche de poste par défaut
    return {
        "id": job_post_id,
        "title": "Poste générique",
        "description": "Description générique d'un poste",
        "company": "Entreprise",
        "location": "Ville",
        "contract_type": "CDI",
        "salary_range": "Selon profil",
        "required_skills": [
            {"name": "Compétence 1", "level": 3, "required": True},
            {"name": "Compétence 2", "level": 2, "required": False}
        ],
        "required_experience": {
            "min_years": 3,
            "domains": ["domaine 1", "domaine 2"],
            "description": "Expérience dans le domaine"
        },
        "required_education": {
            "level": "Bac+3",
            "domains": ["domaine d'étude"],
            "required": False
        }
    }

def get_mock_candidate(candidate_id: int) -> Dict[str, Any]:
    """
    Simule la récupération d'un candidat depuis la base de données.
    """
    # Candidat développeur Python
    if candidate_id == 1:
        return {
            "id": 1,
            "name": "Jean Dupont",
            "skills": [
                {"name": "Python", "level": 4, "years": 7},
                {"name": "Django", "level": 4, "years": 5},
                {"name": "SQL", "level": 3, "years": 7},
                {"name": "Git", "level": 4, "years": 7},
                {"name": "JavaScript", "level": 3, "years": 4},
                {"name": "Docker", "level": 3, "years": 2}
            ],
            "experience": [
                {
                    "title": "Développeur Python Senior",
                    "company": "WebTech",
                    "years": 4,
                    "description": "Développement d'applications web avec Django, API REST, etc."
                },
                {
                    "title": "Développeur Backend",
                    "company": "SoftCorp",
                    "years": 3,
                    "description": "Développement backend avec Python et PHP"
                }
            ],
            "education": [
                {
                    "degree": "Master en Informatique",
                    "institution": "Université de Paris",
                    "year": 2015,
                    "domain": "informatique"
                }
            ]
        }
    # Candidat data scientist
    elif candidate_id == 2:
        return {
            "id": 2,
            "name": "Marie Martin",
            "skills": [
                {"name": "Python", "level": 4, "years": 5},
                {"name": "Machine Learning", "level": 3, "years": 3},
                {"name": "SQL", "level": 4, "years": 5},
                {"name": "Pandas", "level": 4, "years": 4},
                {"name": "TensorFlow", "level": 2, "years": 1},
                {"name": "Data Visualization", "level": 4, "years": 4}
            ],
            "experience": [
                {
                    "title": "Data Analyst",
                    "company": "AnalyticsPlus",
                    "years": 3,
                    "description": "Analyse de données clients, création de tableaux de bord"
                },
                {
                    "title": "Stagiaire Data Science",
                    "company": "BigData",
                    "years": 1,
                    "description": "Projets de machine learning sur données e-commerce"
                }
            ],
            "education": [
                {
                    "degree": "Master en Data Science",
                    "institution": "École Polytechnique",
                    "year": 2019,
                    "domain": "data science"
                },
                {
                    "degree": "Licence en Mathématiques",
                    "institution": "Université de Lyon",
                    "year": 2017,
                    "domain": "mathématiques"
                }
            ]
        }
    # Candidat développeur frontend (moins adapté pour le poste Python)
    elif candidate_id == 3:
        return {
            "id": 3,
            "name": "Sophie Bernard",
            "skills": [
                {"name": "JavaScript", "level": 5, "years": 6},
                {"name": "React", "level": 4, "years": 4},
                {"name": "HTML/CSS", "level": 5, "years": 6},
                {"name": "Python", "level": 2, "years": 1},
                {"name": "Git", "level": 3, "years": 4}
            ],
            "experience": [
                {
                    "title": "Développeur Frontend",
                    "company": "WebAgency",
                    "years": 4,
                    "description": "Développement d'interfaces utilisateur avec React"
                },
                {
                    "title": "Intégrateur Web",
                    "company": "DesignStudio",
                    "years": 2,
                    "description": "Intégration HTML/CSS, JavaScript"
                }
            ],
            "education": [
                {
                    "degree": "Licence en Informatique",
                    "institution": "Université de Nantes",
                    "year": 2016,
                    "domain": "informatique"
                }
            ]
        }
    # Candidat générique
    return {
        "id": candidate_id,
        "name": f"Candidat {candidate_id}",
        "skills": [
            {"name": "Compétence 1", "level": 3, "years": 3},
            {"name": "Compétence 2", "level": 2, "years": 2}
        ],
        "experience": [
            {
                "title": "Poste précédent",
                "company": "Entreprise précédente",
                "years": 3,
                "description": "Description du poste précédent"
            }
        ],
        "education": [
            {
                "degree": "Diplôme",
                "institution": "Institution",
                "year": 2020,
                "domain": "domaine"
            }
        ]
    }

def calculate_skill_match(job_post: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """
    Calcule le score de correspondance des compétences entre une fiche de poste et un candidat.
    """
    try:
        # Dictionnaire des compétences du candidat pour un accès facile
        candidate_skills = {skill["name"].lower(): skill for skill in candidate["skills"]}
        
        total_score = 0.0
        total_weight = 0.0
        
        for job_skill in job_post["required_skills"]:
            skill_name = job_skill["name"].lower()
            required = job_skill.get("required", True)
            required_level = job_skill.get("level", 1)
            
            # Poids différent selon que la compétence est requise ou non
            weight = 3.0 if required else 1.0
            total_weight += weight
            
            # Vérifier si le candidat possède cette compétence
            if skill_name in candidate_skills:
                candidate_skill = candidate_skills[skill_name]
                candidate_level = candidate_skill.get("level", 0)
                
                # Calculer le score pour cette compétence (0 à 1)
                if candidate_level >= required_level:
                    skill_score = 1.0
                else:
                    # Proportion du niveau requis
                    skill_score = candidate_level / required_level
                
                # Bonus pour l'expérience dans cette compétence
                experience_years = candidate_skill.get("years", 0)
                experience_bonus = min(experience_years / 5.0, 0.2)  # Max 20% de bonus
                
                total_score += (skill_score + experience_bonus) * weight
            elif required:
                # Pénalité sévère pour une compétence requise manquante
                # On ne l'ajoute pas du tout au score
                pass
            else:
                # Petite pénalité pour une compétence optionnelle manquante
                total_score += 0.1 * weight
        
        # Normaliser le score
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
            
        # Limiter le score entre 0 et 1
        return min(max(final_score, 0.0), 1.0)
    except Exception as e:
        logger.error(f"Erreur lors du calcul du score de compétences: {str(e)}")
        return 0.0

def calculate_experience_match(job_post: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """
    Calcule le score de correspondance d'expérience entre une fiche de poste et un candidat.
    """
    try:
        required_experience = job_post.get("required_experience", {})
        required_years = required_experience.get("min_years", 0)
        required_domains = required_experience.get("domains", [])
        
        # Calculer le nombre total d'années d'expérience du candidat
        total_years = sum(exp.get("years", 0) for exp in candidate.get("experience", []))
        
        # Score basé sur les années d'expérience
        if total_years >= required_years:
            years_score = 1.0
        else:
            years_score = total_years / required_years if required_years > 0 else 0.0
        
        # Score basé sur les domaines d'expérience
        domains_score = 0.0
        if required_domains:
            # Extraire le texte des expériences du candidat
            candidate_exp_text = " ".join([
                f"{exp.get('title', '')} {exp.get('description', '')}"
                for exp in candidate.get("experience", [])
            ]).lower()
            
            # Compter combien de domaines requis sont présents dans l'expérience du candidat
            domain_matches = 0
            for domain in required_domains:
                if domain.lower() in candidate_exp_text:
                    domain_matches += 1
            
            domains_score = domain_matches / len(required_domains)
        
        # Pondération: 60% années, 40% domaines
        final_score = 0.6 * years_score + 0.4 * domains_score
        
        return min(max(final_score, 0.0), 1.0)
    except Exception as e:
        logger.error(f"Erreur lors du calcul du score d'expérience: {str(e)}")
        return 0.0

def calculate_education_match(job_post: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """
    Calcule le score de correspondance de formation entre une fiche de poste et un candidat.
    """
    try:
        required_education = job_post.get("required_education", {})
        required_level = required_education.get("level", "")
        required_domains = required_education.get("domains", [])
        is_required = required_education.get("required", False)
        
        # Si l'éducation n'est pas requise, score minimum assuré
        if not is_required:
            base_score = 0.7
        else:
            base_score = 0.0
        
        # Vérifier si le candidat a le niveau requis
        level_score = 0.0
        if required_level:
            # Mapper les niveaux d'éducation à des scores numériques
            education_levels = {
                "Bac": 1,
                "Bac+2": 2,
                "Bac+3": 3,
                "Licence": 3,
                "Bac+4": 4,
                "Bac+5": 5,
                "Master": 5,
                "Doctorat": 8,
                "PhD": 8
            }
            
            required_level_score = education_levels.get(required_level, 0)
            
            # Trouver le niveau d'éducation le plus élevé du candidat
            candidate_max_level = 0
            for edu in candidate.get("education", []):
                degree = edu.get("degree", "").lower()
                
                # Détecter le niveau à partir du nom du diplôme
                for level_name, level_score in education_levels.items():
                    if level_name.lower() in degree:
                        candidate_max_level = max(candidate_max_level, level_score)
            
            # Calculer le score basé sur le niveau
            if candidate_max_level >= required_level_score:
                level_score = 1.0
            else:
                level_score = candidate_max_level / required_level_score if required_level_score > 0 else 0.0
        
        # Score basé sur les domaines d'éducation
        domains_score = 0.0
        if required_domains:
            # Extraire les domaines d'éducation du candidat
            candidate_domains = [
                edu.get("domain", "").lower() for edu in candidate.get("education", [])
            ]
            
            # Compter combien de domaines requis correspondent
            domain_matches = 0
            for domain in required_domains:
                if any(required_domain.lower() in candidate_domain for required_domain in required_domains for candidate_domain in candidate_domains):
                    domain_matches += 1
            
            domains_score = domain_matches / len(required_domains)
        
        # Calculer le score final
        if is_required:
            # Pondération: 60% niveau, 40% domaines
            final_score = 0.6 * level_score + 0.4 * domains_score
        else:
            # Si non requis, partir du score de base et ajouter un bonus
            bonus = 0.3 * (0.6 * level_score + 0.4 * domains_score)
            final_score = base_score + bonus
        
        return min(max(final_score, 0.0), 1.0)
    except Exception as e:
        logger.error(f"Erreur lors du calcul du score d'éducation: {str(e)}")
        return 0.0

def identify_strengths(job_post: Dict[str, Any], candidate: Dict[str, Any]) -> List[str]:
    """
    Identifie les forces du candidat par rapport au poste.
    """
    strengths = []
    
    # Convertir les compétences du candidat en dictionnaire pour un accès facile
    candidate_skills = {skill["name"].lower(): skill for skill in candidate["skills"]}
    
    # Identifier les compétences où le candidat excelle
    for job_skill in job_post["required_skills"]:
        skill_name = job_skill["name"]
        required_level = job_skill.get("level", 1)
        
        if skill_name.lower() in candidate_skills:
            candidate_skill = candidate_skills[skill_name.lower()]
            candidate_level = candidate_skill.get("level", 0)
            
            # Si le candidat excède le niveau requis
            if candidate_level > required_level:
                experience_years = candidate_skill.get("years", 0)
                if experience_years > 3:
                    strengths.append(f"Expert en {skill_name} avec {experience_years} ans d'expérience")
                else:
                    strengths.append(f"Bonnes compétences en {skill_name}")
    
    # Analyser l'expérience
    required_years = job_post.get("required_experience", {}).get("min_years", 0)
    total_years = sum(exp.get("years", 0) for exp in candidate.get("experience", []))
    
    if total_years > required_years + 2:
        strengths.append(f"Expérience professionnelle significative ({total_years} ans)")
    
    # Ajouter des forces spécifiques selon le domaine
    for exp in candidate.get("experience", []):
        if "développement web" in job_post.get("required_experience", {}).get("domains", []) and \
           "développement web" in exp.get("description", "").lower():
            strengths.append("Expérience en développement web")
            break
    
    for exp in candidate.get("experience", []):
        if "data science" in job_post.get("required_experience", {}).get("domains", []) and \
           "machine learning" in exp.get("description", "").lower():
            strengths.append("Expérience en Machine Learning")
            break
    
    return strengths

def identify_gaps(job_post: Dict[str, Any], candidate: Dict[str, Any]) -> List[str]:
    """
    Identifie les lacunes du candidat par rapport au poste.
    """
    gaps = []
    
    # Convertir les compétences du candidat en dictionnaire pour un accès facile
    candidate_skills = {skill["name"].lower(): skill for skill in candidate["skills"]}
    
    # Identifier les compétences manquantes ou insuffisantes
    for job_skill in job_post["required_skills"]:
        skill_name = job_skill["name"]
        required = job_skill.get("required", True)
        required_level = job_skill.get("level", 1)
        
        if skill_name.lower() not in candidate_skills and required:
            gaps.append(f"Compétence manquante: {skill_name}")
        elif skill_name.lower() in candidate_skills:
            candidate_level = candidate_skills[skill_name.lower()].get("level", 0)
            if candidate_level < required_level and required:
                gaps.append(f"Niveau insuffisant en {skill_name}")
    
    # Vérifier l'expérience
    required_years = job_post.get("required_experience", {}).get("min_years", 0)
    total_years = sum(exp.get("years", 0) for exp in candidate.get("experience", []))
    
    if total_years < required_years:
        gaps.append(f"Expérience professionnelle insuffisante ({total_years}/{required_years} ans)")
    
    # Vérifier les domaines d'expérience manquants
    required_domains = job_post.get("required_experience", {}).get("domains", [])
    candidate_exp_text = " ".join([
        f"{exp.get('title', '')} {exp.get('description', '')}"
        for exp in candidate.get("experience", [])
    ]).lower()
    
    for domain in required_domains:
        if domain.lower() not in candidate_exp_text:
            gaps.append(f"Expérience manquante dans le domaine: {domain}")
    
    # Vérifier l'éducation si requise
    required_education = job_post.get("required_education", {})
    if required_education.get("required", False):
        required_level = required_education.get("level", "")
        
        # Mapper les niveaux d'éducation
        education_levels = {
            "Bac": 1, "Bac+2": 2, "Bac+3": 3, "Licence": 3,
            "Bac+4": 4, "Bac+5": 5, "Master": 5, "Doctorat": 8, "PhD": 8
        }
        
        required_level_score = education_levels.get(required_level, 0)
        
        # Vérifier si le candidat a le niveau requis
        has_required_level = False
        for edu in candidate.get("education", []):
            degree = edu.get("degree", "").lower()
            for level_name, level_score in education_levels.items():
                if level_name.lower() in degree and level_score >= required_level_score:
                    has_required_level = True
                    break
        
        if not has_required_level and required_level:
            gaps.append(f"Niveau d'éducation requis non atteint: {required_level}")
    
    return gaps

def generate_recommendations(job_post: Dict[str, Any], candidate: Dict[str, Any], gaps: List[str]) -> List[str]:
    """
    Génère des recommandations personnalisées basées sur les lacunes identifiées.
    """
    recommendations = []
    
    # Transformer les lacunes en recommandations
    for gap in gaps:
        if "manquante" in gap:
            skill_name = re.search(r"Compétence manquante: (.*)", gap)
            if skill_name:
                recommendations.append(f"Formation recommandée en {skill_name.group(1)}")
        
        elif "insuffisant" in gap and "en" in gap:
            skill_name = re.search(r"Niveau insuffisant en (.*)", gap)
            if skill_name:
                recommendations.append(f"Approfondir les connaissances en {skill_name.group(1)}")
        
        elif "Expérience professionnelle insuffisante" in gap:
            recommendations.append("Acquérir plus d'expérience professionnelle dans le domaine")
        
        elif "Expérience manquante dans le domaine" in gap:
            domain = re.search(r"Expérience manquante dans le domaine: (.*)", gap)
            if domain:
                recommendations.append(f"Acquérir de l'expérience en {domain.group(1)}")
        
        elif "Niveau d'éducation requis non atteint" in gap:
            level = re.search(r"Niveau d'éducation requis non atteint: (.*)", gap)
            if level:
                recommendations.append(f"Envisager une formation pour atteindre le niveau {level.group(1)}")
    
    # Ajouter des recommandations générales si peu de lacunes spécifiques
    if not recommendations:
        recommendations.append("Préparer des exemples concrets de réalisations pour l'entretien")
    
    if len(recommendations) < 2:
        recommendations.append("Mettre en avant vos compétences transférables pendant l'entretien")
    
    return recommendations
