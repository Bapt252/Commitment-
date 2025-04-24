
"""
Nexten Matching Service
-----------------------
Service de matching complet implémentant l'approche en trois phases:
1. Parsing CV via OpenAI
2. Questionnaires
3. Matching intelligent

Auteur: Claude/Anthropic
Date: 24/04/2025
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from app.algorithms.nexten_matcher import NextenMatchingAlgorithm, match_candidate_to_job
from app.algorithms.matcher import calculate_skills_match, calculate_experience_match, calculate_description_match

# Configuration du logger
logger = logging.getLogger(__name__)

async def parse_cv_with_openai(cv_file_path: str, openai_client: Any) -> Dict[str, Any]:
    """
    Parser un CV avec OpenAI pour extraire les informations structurées
    
    Args:
        cv_file_path: Chemin vers le fichier CV
        openai_client: Client OpenAI configuré
        
    Returns:
        dict: Données structurées du CV
    """
    # Extraction du texte du CV
    cv_text = await extract_text_from_cv(cv_file_path)
    
    # Requête à OpenAI pour l'extraction structurée
    prompt = f"""
    À partir de ce CV, extrais les informations suivantes au format JSON :
    - name: Nom complet
    - job_title: Titre du poste actuel ou le plus récent
    - skills: Liste des compétences techniques
    - experience: Nombre total d'années d'expérience
    - education: Formation
    - summary: Résumé du profil
    - previous_positions: Liste des postes précédents avec leur durée
    
    CV:
    {cv_text}
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Tu es un assistant spécialisé dans l'extraction précise de données depuis des CV."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Convertir la réponse JSON en dictionnaire Python
        cv_data = json.loads(response.choices[0].message.content)
        
        # Normalisation des données
        cv_data = normalize_cv_data(cv_data)
        
        return cv_data
    except Exception as e:
        logger.error(f"Erreur lors du parsing du CV: {str(e)}", exc_info=True)
        return {}

async def extract_text_from_cv(cv_file_path: str) -> str:
    """
    Extraire le texte d'un CV au format PDF ou DOCX
    
    Args:
        cv_file_path: Chemin vers le fichier CV
        
    Returns:
        str: Texte extrait du CV
    """
    # Extension du fichier
    file_extension = cv_file_path.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return await extract_text_from_pdf(cv_file_path)
    elif file_extension in ['docx', 'doc']:
        return await extract_text_from_docx(cv_file_path)
    else:
        raise ValueError(f"Format de fichier non supporté: {file_extension}")

async def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extraire le texte d'un fichier PDF
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        str: Texte extrait du PDF
    """
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}", exc_info=True)
        return ""

async def extract_text_from_docx(docx_path: str) -> str:
    """
    Extraire le texte d'un fichier DOCX
    
    Args:
        docx_path: Chemin vers le fichier DOCX
        
    Returns:
        str: Texte extrait du DOCX
    """
    try:
        import docx
        
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte du DOCX: {str(e)}", exc_info=True)
        return ""

def normalize_cv_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliser les données extraites du CV
    
    Args:
        cv_data: Données brutes extraites du CV
        
    Returns:
        dict: Données normalisées
    """
    # Convertir les compétences en liste si ce n'est pas déjà le cas
    if 'skills' in cv_data and isinstance(cv_data['skills'], str):
        cv_data['skills'] = [skill.strip() for skill in cv_data['skills'].split(',')]
    
    # Nettoyer chaque compétence
    if 'skills' in cv_data and isinstance(cv_data['skills'], list):
        cv_data['skills'] = [skill.strip() for skill in cv_data['skills']]
    
    # S'assurer que l'expérience est une chaîne de caractères
    if 'experience' in cv_data and not isinstance(cv_data['experience'], str):
        cv_data['experience'] = str(cv_data['experience'])
    
    return cv_data

async def nexten_matching_process(candidate_id: int, job_id: int, db: Any, openai_client: Any) -> Dict[str, Any]:
    """
    Processus complet de matching en trois phases:
    1. Parsing CV via OpenAI
    2. Questionnaires
    3. Matching intelligent
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        
    Returns:
        dict: Résultat du matching avec score et insights
    """
    # 1. Récupération des données
    candidate_record = await db.get_candidate(candidate_id)
    job_record = await db.get_job(job_id)
    
    # 2. Parsing du CV via OpenAI si nécessaire
    if candidate_record.get('cv_parsed_data') is None and candidate_record.get('cv_path'):
        cv_data = await parse_cv_with_openai(candidate_record['cv_path'], openai_client)
        await db.update_candidate_cv_data(candidate_id, cv_data)
    else:
        cv_data = candidate_record.get('cv_parsed_data', {})
    
    # 3. Récupération des réponses aux questionnaires
    candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
    company_questionnaire = await db.get_job_questionnaire(job_id)
    
    # 4. Construction des structures de données complètes
    candidate_data = {
        'id': candidate_id,
        'cv': cv_data,
        'questionnaire': candidate_questionnaire
    }
    
    job_data = {
        'id': job_id,
        'description': job_record,
        'questionnaire': company_questionnaire
    }
    
    # 5. Calcul du matching avec l'algorithme Nexten
    matcher = NextenMatchingAlgorithm()
    result = matcher.calculate_match(candidate_data, job_data)
    
    # 6. Enregistrement du résultat
    match_id = await db.save_matching_result(candidate_id, job_id, result)
    
    # 7. Ajout des métadonnées
    result['match_id'] = match_id
    result['candidate'] = {
        'id': candidate_id,
        'name': candidate_record.get('name', ''),
    }
    result['job'] = {
        'id': job_id,
        'title': job_record.get('title', ''),
        'company': job_record.get('company', '')
    }
    
    return result

async def bulk_matching_process(candidate_id: int, job_ids: List[int], db: Any, openai_client: Any, min_score: float = 0.3) -> List[Dict[str, Any]]:
    """
    Processus de matching en masse pour un candidat avec plusieurs offres
    
    Args:
        candidate_id: ID du candidat
        job_ids: Liste des IDs d'offres d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        min_score: Score minimum pour inclure un match (défaut: 0.3)
        
    Returns:
        list: Liste des résultats de matching triés par score
    """
    # 1. Récupération des données du candidat
    candidate_record = await db.get_candidate(candidate_id)
    
    # 2. Parsing du CV via OpenAI si nécessaire
    if candidate_record.get('cv_parsed_data') is None and candidate_record.get('cv_path'):
        cv_data = await parse_cv_with_openai(candidate_record['cv_path'], openai_client)
        await db.update_candidate_cv_data(candidate_id, cv_data)
    else:
        cv_data = candidate_record.get('cv_parsed_data', {})
    
    # 3. Récupération du questionnaire candidat
    candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
    
    # 4. Construction de la structure de données du candidat
    candidate_data = {
        'id': candidate_id,
        'cv': cv_data,
        'questionnaire': candidate_questionnaire
    }
    
    # 5. Récupération et traitement des offres d'emploi
    results = []
    matcher = NextenMatchingAlgorithm()
    
    for job_id in job_ids:
        # Récupération des données de l'offre
        job_record = await db.get_job(job_id)
        company_questionnaire = await db.get_job_questionnaire(job_id)
        
        # Construction de la structure de données de l'offre
        job_data = {
            'id': job_id,
            'description': job_record,
            'questionnaire': company_questionnaire
        }
        
        # Calcul du matching
        result = matcher.calculate_match(candidate_data, job_data)
        
        # Filtrer selon le score minimum
        if result['score'] < min_score:
            continue
            
        # Enregistrement du résultat
        match_id = await db.save_matching_result(candidate_id, job_id, result)
        
        # Ajout des métadonnées
        match_result = {
            'match_id': match_id,
            'candidate': {
                'id': candidate_id,
                'name': candidate_record.get('name', ''),
            },
            'job': {
                'id': job_id,
                'title': job_record.get('title', ''),
                'company': job_record.get('company', '')
            },
            'score': result['score'],
            'category': result['category'],
            'details': result['details'],
            'insights': result['insights']
        }
        
        results.append(match_result)
    
    # Tri des résultats par score décroissant
    return sorted(results, key=lambda x: x['score'], reverse=True)

async def job_candidates_matching_process(job_id: int, candidate_ids: List[int], db: Any, openai_client: Any, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Processus de matching pour une offre d'emploi avec plusieurs candidats
    
    Args:
        job_id: ID de l'offre d'emploi
        candidate_ids: Liste des IDs de candidats
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        limit: Nombre maximum de résultats à retourner (défaut: 10)
        
    Returns:
        list: Liste des résultats de matching triés par score
    """
    # 1. Récupération des données de l'offre
    job_record = await db.get_job(job_id)
    company_questionnaire = await db.get_job_questionnaire(job_id)
    
    # 2. Construction de la structure de données de l'offre
    job_data = {
        'id': job_id,
        'description': job_record,
        'questionnaire': company_questionnaire
    }
    
    # 3. Traitement des candidats
    results = []
    matcher = NextenMatchingAlgorithm()
    
    for candidate_id in candidate_ids:
        # Récupération des données du candidat
        candidate_record = await db.get_candidate(candidate_id)
        
        # Parsing du CV si nécessaire
        if candidate_record.get('cv_parsed_data') is None and candidate_record.get('cv_path'):
            cv_data = await parse_cv_with_openai(candidate_record['cv_path'], openai_client)
            await db.update_candidate_cv_data(candidate_id, cv_data)
        else:
            cv_data = candidate_record.get('cv_parsed_data', {})
        
        # Récupération du questionnaire candidat
        candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
        
        # Construction de la structure de données du candidat
        candidate_data = {
            'id': candidate_id,
            'cv': cv_data,
            'questionnaire': candidate_questionnaire
        }
        
        # Calcul du matching
        result = matcher.calculate_match(candidate_data, job_data)
        
        # Enregistrement du résultat
        match_id = await db.save_matching_result(candidate_id, job_id, result)
        
        # Ajout des métadonnées
        match_result = {
            'match_id': match_id,
            'candidate': {
                'id': candidate_id,
                'name': candidate_record.get('name', ''),
            },
            'job': {
                'id': job_id,
                'title': job_record.get('title', ''),
                'company': job_record.get('company', '')
            },
            'score': result['score'],
            'category': result['category'],
            'details': result['details'],
            'insights': result['insights']
        }
        
        results.append(match_result)
    
    # Tri des résultats par score décroissant et limitation
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    return sorted_results[:limit] if limit > 0 else sorted_results

# Structure des questionnaires Nexten
CANDIDATE_QUESTIONNAIRE_STRUCTURE = {
    "informations_personnelles": {
        "nom_prenom": "",
        "poste_souhaite": ""
    },
    "mobilite_preferences": {
        "mode_travail": "",  # Sur site, Hybride, Full remote
        "localisation": "",
        "type_contrat": "",  # CDI, CDD, Freelance
        "taille_entreprise": ""  # Startup, PME, Grand groupe, Peu importe
    },
    "motivations_secteurs": {
        "secteurs": [],  # Liste des secteurs d'intérêt
        "valeurs": [],  # Valeurs importantes pour le candidat
        "technologies": []  # Technologies préférées
    },
    "disponibilite_situation": {
        "disponibilite": "",  # Date de disponibilité
        "experience": "",  # Années d'expérience
        "salaire": {
            "min": 0,
            "max": 0
        }
    }
}

# Structure du questionnaire entreprise
COMPANY_QUESTIONNAIRE_STRUCTURE = {
    "poste_propose": "",
    "mode_travail": "",  # Sur site, Hybride, Remote
    "localisation": "",
    "type_contrat": "",
    "taille_entreprise": "",
    "secteur": "",
    "valeurs": [],
    "technologies": [],
    "technologies_requises": [],  # Sous-ensemble obligatoire
    "date_debut": "",
    "experience_requise": "",
    "salaire": {
        "min": 0,
        "max": 0
    }
}
