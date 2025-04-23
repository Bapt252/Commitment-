import re
import math
from collections import Counter
from flask import current_app
from app.algorithms.nlp_utils import normalize_text, extract_keywords, calculate_similarity

def calculate_skills_match(profile_skills, job_skills):
    """
    Calculer la correspondance des compétences entre un profil et une offre d'emploi
    
    Args:
        profile_skills (list): Liste des compétences du profil
        job_skills (list): Liste des compétences requises pour le poste
    
    Returns:
        float: Score de correspondance entre 0 et 1
    """
    if not profile_skills or not job_skills:
        return 0.0
    
    # Normaliser les compétences
    normalized_profile_skills = [normalize_text(skill) for skill in profile_skills]
    normalized_job_skills = [normalize_text(skill) for skill in job_skills]
    
    # Calculer l'intersection des compétences
    matched_skills = set(normalized_profile_skills).intersection(set(normalized_job_skills))
    
    # Calculer le score
    match_score = len(matched_skills) / len(normalized_job_skills)
    
    return match_score

def calculate_experience_match(profile_experience, job_required_experience):
    """
    Calculer la correspondance d'expérience entre un profil et une offre d'emploi
    
    Args:
        profile_experience (str): Expérience du profil (ex: "5 ans")
        job_required_experience (str): Expérience requise pour le poste (ex: "3-5 ans")
    
    Returns:
        float: Score de correspondance entre 0 et 1
    """
    try:
        # Extraire les années d'expérience du profil
        profile_years = extract_years_from_experience(profile_experience)
        
        # Extraire l'expérience minimale et maximale requise pour le poste
        min_years, max_years = extract_min_max_years(job_required_experience)
        
        if profile_years is None or min_years is None:
            return 0.5  # Score neutre si les données sont manquantes
        
        # Calculer le score de correspondance
        if profile_years < min_years:
            # Expérience insuffisante
            ratio = profile_years / min_years if min_years > 0 else 0
            score = max(0, ratio * 0.8)  # Pénaliser légèrement l'expérience insuffisante
        elif max_years is not None and profile_years > max_years:
            # Surqualifié (légèrement pénalisé mais moins que sous-qualifié)
            score = 0.9
        else:
            # Expérience dans la fourchette requise, score idéal
            score = 1.0
        
        return score
    except Exception as e:
        current_app.logger.error(f"Erreur lors du calcul de la correspondance d'expérience: {str(e)}", exc_info=True)
        return 0.5  # Score neutre en cas d'erreur

def extract_years_from_experience(experience_text):
    """
    Extraire le nombre d'années d'expérience à partir d'un texte
    
    Args:
        experience_text (str): Texte décrivant l'expérience (ex: "5 ans")
    
    Returns:
        int or None: Nombre d'années d'expérience ou None si non détecté
    """
    if not experience_text or experience_text == "Non détecté":
        return None
    
    # Recherche de motifs comme "5 ans", "5+ ans", "cinq ans", etc.
    pattern = r'(\d+)(?:\+)?\s*(?:an|ans|années)'
    match = re.search(pattern, experience_text.lower())
    
    if match:
        return int(match.group(1))
    
    # Conversion de texte en nombre pour les cas comme "cinq ans"
    number_words = {
        'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
        'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10
    }
    
    for word, value in number_words.items():
        if f"{word} an" in experience_text.lower() or f"{word} ans" in experience_text.lower():
            return value
    
    return None

def extract_min_max_years(required_experience):
    """
    Extraire l'expérience minimale et maximale requise
    
    Args:
        required_experience (str): Texte décrivant l'expérience requise (ex: "3-5 ans")
    
    Returns:
        tuple: (min_years, max_years) ou (min_years, None) si pas de maximum
    """
    if not required_experience:
        return None, None
    
    # Recherche de motifs comme "3-5 ans", "minimum 3 ans", "au moins 3 ans", etc.
    range_pattern = r'(\d+)\s*-\s*(\d+)\s*(?:an|ans|années)'
    min_pattern = r'(?:minimum|min|au moins)\s*(\d+)\s*(?:an|ans|années)'
    single_pattern = r'(\d+)\s*(?:an|ans|années)'
    
    # Vérifier d'abord s'il y a une fourchette
    range_match = re.search(range_pattern, required_experience.lower())
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))
    
    # Vérifier s'il y a un minimum explicite
    min_match = re.search(min_pattern, required_experience.lower())
    if min_match:
        return int(min_match.group(1)), None
    
    # Vérifier s'il y a juste un nombre
    single_match = re.search(single_pattern, required_experience.lower())
    if single_match:
        return int(single_match.group(1)), int(single_match.group(1))
    
    return None, None

def calculate_description_match(profile_description, job_description):
    """
    Calculer la correspondance entre la description du profil et celle du poste
    
    Args:
        profile_description (str): Description du profil ou résumé du CV
        job_description (str): Description du poste
    
    Returns:
        float: Score de correspondance entre 0 et 1
    """
    if not profile_description or not job_description:
        return 0.5  # Score neutre si les données sont manquantes
    
    try:
        # Extraire des mots-clés des descriptions
        profile_keywords = extract_keywords(profile_description)
        job_keywords = extract_keywords(job_description)
        
        # Calculer la similarité entre les descriptions
        similarity_score = calculate_similarity(profile_keywords, job_keywords)
        
        return similarity_score
    except Exception as e:
        current_app.logger.error(f"Erreur lors du calcul de la correspondance de description: {str(e)}", exc_info=True)
        return 0.5  # Score neutre en cas d'erreur

def match_profile_to_jobs(profile_data, jobs_data):
    """
    Associer un profil à des offres d'emploi
    
    Args:
        profile_data (dict): Données du profil
        jobs_data (list): Liste des offres d'emploi
    
    Returns:
        list: Liste des correspondances avec scores
    """
    matching_results = []
    
    # Extraire les données pertinentes du profil
    profile_skills = profile_data.get('skills', [])
    profile_experience = profile_data.get('experience', '')
    profile_description = profile_data.get('summary', '')
    profile_job_title = profile_data.get('job_title', '')
    
    for job in jobs_data:
        # Extraire les données pertinentes de l'offre d'emploi
        job_id = job.get('id')
        job_title = job.get('title', '')
        job_skills = job.get('required_skills', [])
        job_required_experience = job.get('required_experience', '')
        job_description = job.get('description', '')
        
        # Calculer les scores par catégorie
        skills_score = calculate_skills_match(profile_skills, job_skills)
        experience_score = calculate_experience_match(profile_experience, job_required_experience)
        description_score = calculate_description_match(profile_description, job_description)
        title_score = calculate_similarity([normalize_text(profile_job_title)], [normalize_text(job_title)])
        
        # Pondérer les scores selon l'importance
        weights = {
            'skills': 0.45,
            'experience': 0.20,
            'description': 0.25,
            'title': 0.10
        }
        
        # Calculer le score global
        total_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            description_score * weights['description'] +
            title_score * weights['title']
        )
        
        # Ajouter au résultat
        matching_results.append({
            'job_id': job_id,
            'job_title': job_title,
            'matching_score': round(total_score, 2),
            'details': {
                'skills_match': round(skills_score, 2),
                'experience_match': round(experience_score, 2),
                'description_match': round(description_score, 2),
                'title_match': round(title_score, 2)
            }
        })
    
    return matching_results

def match_job_to_profiles(job_data, profiles_data):
    """
    Associer une offre d'emploi à des profils
    
    Args:
        job_data (dict): Données de l'offre d'emploi
        profiles_data (list): Liste des profils
    
    Returns:
        list: Liste des correspondances avec scores
    """
    matching_results = []
    
    # Extraire les données pertinentes de l'offre d'emploi
    job_title = job_data.get('title', '')
    job_skills = job_data.get('required_skills', [])
    job_required_experience = job_data.get('required_experience', '')
    job_description = job_data.get('description', '')
    
    for profile in profiles_data:
        # Extraire les données pertinentes du profil
        profile_id = profile.get('id')
        profile_name = profile.get('name', '')
        profile_skills = profile.get('skills', [])
        profile_experience = profile.get('experience', '')
        profile_description = profile.get('summary', '')
        profile_job_title = profile.get('job_title', '')
        
        # Calculer les scores par catégorie
        skills_score = calculate_skills_match(profile_skills, job_skills)
        experience_score = calculate_experience_match(profile_experience, job_required_experience)
        description_score = calculate_description_match(profile_description, job_description)
        title_score = calculate_similarity([normalize_text(profile_job_title)], [normalize_text(job_title)])
        
        # Pondérer les scores selon l'importance
        weights = {
            'skills': 0.45,
            'experience': 0.20,
            'description': 0.25,
            'title': 0.10
        }
        
        # Calculer le score global
        total_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            description_score * weights['description'] +
            title_score * weights['title']
        )
        
        # Ajouter au résultat
        matching_results.append({
            'profile_id': profile_id,
            'candidate_name': profile_name,
            'job_title': profile_job_title,
            'matching_score': round(total_score, 2),
            'details': {
                'skills_match': round(skills_score, 2),
                'experience_match': round(experience_score, 2),
                'description_match': round(description_score, 2),
                'title_match': round(title_score, 2)
            }
        })
    
    return matching_results
