"""
Module pour le matching avancé basé sur les questionnaires structurés.
Ce module implémente des algorithmes de matching améliorés qui exploitent
les données structurées des questionnaires candidat et entreprise.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

# Configuration du logging
logger = logging.getLogger(__name__)

# Modèle de vectorisation sémantique (à charger une fois)
# Note: Nécessite l'installation de sentence-transformers
try:
    text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
except:
    logger.warning("Impossible de charger SentenceTransformer. Utilisation du fallback.")
    text_encoder = None

# Tables de compatibilité pour les questions à choix
ENVIRONMENT_COMPATIBILITY = {
    "calme et silencieux": {
        "calme et silencieux": 1.0,
        "dynamique avec espaces calmes": 0.7,
        "open space collaboratif": 0.3,
        "très dynamique et animé": 0.1
    },
    "dynamique avec espaces calmes": {
        "calme et silencieux": 0.7,
        "dynamique avec espaces calmes": 1.0,
        "open space collaboratif": 0.8,
        "très dynamique et animé": 0.5
    },
    "open space collaboratif": {
        "calme et silencieux": 0.3,
        "dynamique avec espaces calmes": 0.8,
        "open space collaboratif": 1.0,
        "très dynamique et animé": 0.9
    },
    "très dynamique et animé": {
        "calme et silencieux": 0.1,
        "dynamique avec espaces calmes": 0.5,
        "open space collaboratif": 0.9,
        "très dynamique et animé": 1.0
    }
}

WORK_MODE_COMPATIBILITY = {
    "100% présentiel": {
        "100% présentiel": 1.0,
        "hybride (3j bureau / 2j remote)": 0.8,
        "hybride (2j bureau / 3j remote)": 0.5,
        "100% télétravail": 0.1
    },
    "hybride (3j bureau / 2j remote)": {
        "100% présentiel": 0.8,
        "hybride (3j bureau / 2j remote)": 1.0,
        "hybride (2j bureau / 3j remote)": 0.9,
        "100% télétravail": 0.3
    },
    "hybride (2j bureau / 3j remote)": {
        "100% présentiel": 0.5,
        "hybride (3j bureau / 2j remote)": 0.9,
        "hybride (2j bureau / 3j remote)": 1.0,
        "100% télétravail": 0.7
    },
    "100% télétravail": {
        "100% présentiel": 0.1,
        "hybride (3j bureau / 2j remote)": 0.3,
        "hybride (2j bureau / 3j remote)": 0.7,
        "100% télétravail": 1.0
    }
}

COMPANY_SIZE_COMPATIBILITY = {
    "startup (<20 personnes)": {
        "startup (<20 personnes)": 1.0,
        "petite entreprise (20-100)": 0.8,
        "entreprise moyenne (100-500)": 0.4,
        "grande entreprise (500+)": 0.2
    },
    "petite entreprise (20-100)": {
        "startup (<20 personnes)": 0.8,
        "petite entreprise (20-100)": 1.0,
        "entreprise moyenne (100-500)": 0.7,
        "grande entreprise (500+)": 0.3
    },
    "entreprise moyenne (100-500)": {
        "startup (<20 personnes)": 0.4,
        "petite entreprise (20-100)": 0.7,
        "entreprise moyenne (100-500)": 1.0,
        "grande entreprise (500+)": 0.7
    },
    "grande entreprise (500+)": {
        "startup (<20 personnes)": 0.2,
        "petite entreprise (20-100)": 0.3,
        "entreprise moyenne (100-500)": 0.7,
        "grande entreprise (500+)": 1.0
    }
}

# Mapping des valeurs d'entreprise et soft skills connexes
VALUES_RELATIONSHIPS = {
    "innovation": ["créativité", "adaptabilité", "prise de risque", "curiosité", "amélioration continue"],
    "collaboration": ["esprit d'équipe", "communication", "entraide", "partage", "collectif"],
    "excellence": ["qualité", "rigueur", "expertise", "performance", "précision"],
    "agilité": ["adaptabilité", "flexibilité", "réactivité", "itération", "amélioration continue"],
    "diversité": ["inclusion", "ouverture d'esprit", "respect", "tolérance", "équité"],
    "responsabilité": ["autonomie", "fiabilité", "engagement", "éthique", "proactivité"],
    "transparence": ["honnêteté", "communication", "intégrité", "ouverture", "partage"],
    "respect": ["écoute", "empathie", "considération", "bienveillance", "politesse"],
    "confiance": ["autonomie", "responsabilisation", "délégation", "honnêteté", "fiabilité"]
}

def evaluate_questionnaire_match(
    candidate_responses: Dict[str, Any], 
    company_responses: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fonction principale qui évalue la correspondance entre les réponses
    du candidat et celles de l'entreprise aux questionnaires structurés.
    
    Args:
        candidate_responses: Dictionnaire des réponses du candidat
        company_responses: Dictionnaire des réponses de l'entreprise
        
    Returns:
        Dict contenant le score global et les sous-scores par catégorie
    """
    try:
        # Initialiser les scores par catégorie
        category_scores = {
            "work_environment": 0.0,
            "work_style": 0.0,
            "values_culture": 0.0,
            "career_goals": 0.0,
            "technical_skills": 0.0
        }
        
        # Évaluer la compatibilité environnement de travail
        if "environment_preference" in candidate_responses and "environment_offered" in company_responses:
            category_scores["work_environment"] = evaluate_environment_compatibility(
                candidate_responses["environment_preference"],
                company_responses["environment_offered"]
            )
        
        # Évaluer le mode de travail
        if "work_mode_preference" in candidate_responses and "work_mode_offered" in company_responses:
            category_scores["work_environment"] += evaluate_work_mode_compatibility(
                candidate_responses["work_mode_preference"],
                company_responses["work_mode_offered"]
            )
            # Moyenne des scores d'environnement
            category_scores["work_environment"] /= 2
            
        # Évaluer le style de travail et la culture
        if "team_size_preference" in candidate_responses and "team_size" in company_responses:
            category_scores["work_style"] = evaluate_team_compatibility(
                candidate_responses["team_size_preference"],
                company_responses["team_size"]
            )
        
        # Évaluer les valeurs et la culture
        if "values_important" in candidate_responses and "company_values" in company_responses:
            category_scores["values_culture"] = evaluate_values_compatibility(
                candidate_responses["values_important"],
                company_responses["company_values"]
            )
        
        # Évaluer les objectifs de carrière
        if "career_goals" in candidate_responses and "growth_opportunities" in company_responses:
            category_scores["career_goals"] = evaluate_career_compatibility(
                candidate_responses["career_goals"],
                company_responses["growth_opportunities"]
            )
        
        # Évaluer les compétences techniques (si présentes)
        if "technical_skills" in candidate_responses and "required_skills" in company_responses:
            category_scores["technical_skills"] = evaluate_skills_compatibility(
                candidate_responses["technical_skills"],
                company_responses["required_skills"]
            )
        
        # Calculer le score global
        weights = {
            "work_environment": 0.2,
            "work_style": 0.15,
            "values_culture": 0.25,
            "career_goals": 0.2,
            "technical_skills": 0.2
        }
        
        overall_score = sum(
            score * weights[category] 
            for category, score in category_scores.items()
        ) / sum(
            weights[category] 
            for category, score in category_scores.items() 
            if score > 0
        )
        
        # Générer les points forts et les points de divergence
        strengths = identify_matching_strengths(category_scores)
        gaps = identify_matching_gaps(category_scores)
        
        # Préparer les recommandations
        recommendations = generate_matching_recommendations(
            candidate_responses, 
            company_responses, 
            category_scores
        )
        
        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation du questionnaire: {str(e)}")
        # Retourner une structure basique en cas d'erreur
        return {
            "overall_score": 0.5,  # Score neutre par défaut
            "category_scores": {
                "work_environment": 0.5,
                "work_style": 0.5,
                "values_culture": 0.5,
                "career_goals": 0.5,
                "technical_skills": 0.5
            },
            "strengths": ["Analyse incomplète - erreur de traitement"],
            "gaps": ["Analyse incomplète - erreur de traitement"],
            "recommendations": ["Réessayer l'analyse ou contacter le support technique"]
        }

def evaluate_environment_compatibility(
    candidate_preference: str, 
    company_offered: str
) -> float:
    """
    Évalue la compatibilité entre la préférence d'environnement du candidat et celle offerte par l'entreprise.
    
    Args:
        candidate_preference: Préférence d'environnement du candidat
        company_offered: Environnement offert par l'entreprise
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    candidate_preference = candidate_preference.lower()
    company_offered = company_offered.lower()
    
    # Utiliser la table de compatibilité
    if candidate_preference in ENVIRONMENT_COMPATIBILITY and company_offered in ENVIRONMENT_COMPATIBILITY[candidate_preference]:
        return ENVIRONMENT_COMPATIBILITY[candidate_preference][company_offered]
    
    # Logique de fallback si les valeurs exactes ne sont pas dans le dictionnaire
    if "calme" in candidate_preference and "calme" in company_offered:
        return 0.9
    elif "dynamique" in candidate_preference and "dynamique" in company_offered:
        return 0.9
    elif ("calme" in candidate_preference and "dynamique" in company_offered) or \
         ("dynamique" in candidate_preference and "calme" in company_offered):
        return 0.3
    
    # Par défaut, correspondance moyenne
    return 0.5

def evaluate_work_mode_compatibility(
    candidate_preference: str, 
    company_offered: str
) -> float:
    """
    Évalue la compatibilité entre le mode de travail préféré du candidat et celui offert par l'entreprise.
    
    Args:
        candidate_preference: Mode de travail préféré du candidat
        company_offered: Mode de travail offert par l'entreprise
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    candidate_preference = candidate_preference.lower()
    company_offered = company_offered.lower()
    
    # Utiliser la table de compatibilité
    if candidate_preference in WORK_MODE_COMPATIBILITY and company_offered in WORK_MODE_COMPATIBILITY[candidate_preference]:
        return WORK_MODE_COMPATIBILITY[candidate_preference][company_offered]
    
    # Logique de fallback basée sur des mots-clés
    if "télétravail" in candidate_preference and "télétravail" in company_offered:
        return 0.9
    elif "présentiel" in candidate_preference and "présentiel" in company_offered:
        return 0.9
    elif "hybride" in candidate_preference and "hybride" in company_offered:
        return 0.8
    elif ("télétravail" in candidate_preference and "présentiel" in company_offered) or \
         ("présentiel" in candidate_preference and "télétravail" in company_offered):
        return 0.1
    
    # Par défaut, correspondance moyenne
    return 0.5

def evaluate_team_compatibility(
    candidate_preference: str,
    company_team_size: str
) -> float:
    """
    Évalue la compatibilité entre la préférence de taille d'équipe du candidat et celle de l'entreprise.
    
    Args:
        candidate_preference: Préférence de taille d'équipe du candidat
        company_team_size: Taille d'équipe de l'entreprise
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    candidate_preference = candidate_preference.lower()
    company_team_size = company_team_size.lower()
    
    # Utiliser la table de compatibilité pour la taille d'entreprise
    if candidate_preference in COMPANY_SIZE_COMPATIBILITY and company_team_size in COMPANY_SIZE_COMPATIBILITY[candidate_preference]:
        return COMPANY_SIZE_COMPATIBILITY[candidate_preference][company_team_size]
    
    # Logique de fallback basée sur des mots-clés
    if "petit" in candidate_preference and "petit" in company_team_size:
        return 0.9
    elif "grand" in candidate_preference and "grand" in company_team_size:
        return 0.9
    elif "moyen" in candidate_preference and "moyen" in company_team_size:
        return 0.9
    elif ("petit" in candidate_preference and "grand" in company_team_size) or \
         ("grand" in candidate_preference and "petit" in company_team_size):
        return 0.3
    
    # Par défaut, correspondance moyenne
    return 0.5

def evaluate_values_compatibility(
    candidate_values: List[str],
    company_values: List[str]
) -> float:
    """
    Évalue la compatibilité entre les valeurs importantes pour le candidat et celles de l'entreprise.
    
    Args:
        candidate_values: Liste des valeurs importantes pour le candidat
        company_values: Liste des valeurs de l'entreprise
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    # Convertir en minuscules pour la comparaison
    candidate_values = [val.lower() for val in candidate_values]
    company_values = [val.lower() for val in company_values]
    
    # Correspondances directes
    direct_matches = set(candidate_values) & set(company_values)
    direct_match_score = len(direct_matches) / max(len(candidate_values), 1)
    
    # Correspondances indirectes (valeurs connexes)
    indirect_matches = 0
    for cand_value in candidate_values:
        if cand_value not in direct_matches:  # Ne pas compter les matches directs deux fois
            for comp_value in company_values:
                # Vérifier les relations dans les deux sens
                if cand_value in VALUES_RELATIONSHIPS.get(comp_value, []) or \
                   comp_value in VALUES_RELATIONSHIPS.get(cand_value, []):
                    indirect_matches += 0.5  # Valeur partielle pour les correspondances indirectes
    
    # Score combiné pondéré (70% correspondances directes, 30% indirectes)
    total_possible = len(candidate_values)
    if total_possible == 0:
        return 0.5  # Score moyen par défaut si pas de valeurs fournies
    
    indirect_score = indirect_matches / total_possible
    
    return 0.7 * direct_match_score + 0.3 * indirect_score

def evaluate_career_compatibility(
    candidate_goals: Union[str, List[str]],
    company_opportunities: Union[str, List[str]]
) -> float:
    """
    Évalue la compatibilité entre les objectifs de carrière du candidat et les opportunités de l'entreprise.
    
    Args:
        candidate_goals: Objectifs de carrière du candidat (texte ou liste)
        company_opportunities: Opportunités de croissance de l'entreprise (texte ou liste)
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    # Normaliser en texte
    if isinstance(candidate_goals, list):
        candidate_text = " ".join(candidate_goals)
    else:
        candidate_text = candidate_goals
        
    if isinstance(company_opportunities, list):
        company_text = " ".join(company_opportunities)
    else:
        company_text = company_opportunities
    
    # Si le modèle de vectorisation sémantique est disponible
    if text_encoder:
        try:
            # Encoder les textes
            candidate_vector = text_encoder.encode([candidate_text])[0]
            company_vector = text_encoder.encode([company_text])[0]
            
            # Calculer la similarité cosinus
            similarity = np.dot(candidate_vector, company_vector) / \
                         (np.linalg.norm(candidate_vector) * np.linalg.norm(company_vector))
            
            return float(similarity)
        except Exception as e:
            logger.warning(f"Erreur lors de l'encodage sémantique: {str(e)}")
    
    # Fallback: analyse de mots-clés si la vectorisation échoue
    career_keywords = [
        "leadership", "management", "technique", "expertise", "international",
        "développement", "croissance", "formation", "apprentissage", "évolution",
        "progression", "responsabilité", "projet", "innovation", "recherche"
    ]
    
    # Compter les mots-clés communs
    common_keywords = 0
    for keyword in career_keywords:
        if keyword in candidate_text.lower() and keyword in company_text.lower():
            common_keywords += 1
    
    keyword_score = common_keywords / len(career_keywords)
    
    # Pour le fallback, on se base uniquement sur les mots-clés
    return min(keyword_score * 1.5, 1.0)  # Ajustement pour compenser l'absence de vectorisation

def evaluate_skills_compatibility(
    candidate_skills: Dict[str, Any],
    company_required_skills: Dict[str, Any]
) -> float:
    """
    Évalue la compatibilité entre les compétences techniques du candidat et celles requises par l'entreprise.
    
    Args:
        candidate_skills: Compétences techniques du candidat avec niveaux
        company_required_skills: Compétences requises par l'entreprise avec niveaux
        
    Returns:
        Score de compatibilité entre 0 et 1
    """
    # Vérifier si les structures de données contiennent des skills
    if not candidate_skills or not company_required_skills:
        return 0.5  # Score moyen par défaut si pas de données
    
    # Normaliser les structures
    if isinstance(candidate_skills, list):
        candidate_dict = {skill['name'].lower(): skill.get('level', 3) for skill in candidate_skills}
    elif isinstance(candidate_skills, dict):
        candidate_dict = {k.lower(): v for k, v in candidate_skills.items()}
    else:
        return 0.5  # Format non reconnu
    
    if isinstance(company_required_skills, list):
        company_dict = {skill['name'].lower(): skill.get('level', 3) for skill in company_required_skills}
    elif isinstance(company_required_skills, dict):
        company_dict = {k.lower(): v for k, v in company_required_skills.items()}
    else:
        return 0.5  # Format non reconnu
    
    # Calculer les scores pour chaque compétence requise
    total_score = 0
    max_possible = 0
    
    for skill_name, required_level in company_dict.items():
        max_possible += 1
        if skill_name in candidate_dict:
            candidate_level = candidate_dict[skill_name]
            if candidate_level >= required_level:
                total_score += 1
            else:
                # Score partiel si le candidat a la compétence mais pas au niveau requis
                total_score += candidate_level / required_level
    
    # Retourner le score normalisé
    if max_possible > 0:
        return total_score / max_possible
    else:
        return 0.5  # Score moyen par défaut si pas de compétences requises

def identify_matching_strengths(category_scores: Dict[str, float]) -> List[str]:
    """
    Identifie les points forts du matching entre le candidat et l'entreprise.
    
    Args:
        category_scores: Dictionnaire des scores par catégorie
        
    Returns:
        Liste des points forts identifiés
    """
    strengths = []
    
    # Définir des seuils pour les différentes catégories
    thresholds = {
        "work_environment": 0.8,
        "work_style": 0.8, 
        "values_culture": 0.85,
        "career_goals": 0.8,
        "technical_skills": 0.75
    }
    
    # Vérifier chaque catégorie et ajouter des points forts
    for category, score in category_scores.items():
        if score >= thresholds.get(category, 0.8):
            if category == "work_environment":
                strengths.append("Excellente compatibilité avec l'environnement de travail proposé")
            elif category == "work_style":
                strengths.append("Bon alignement avec le style de travail de l'équipe")
            elif category == "values_culture":
                strengths.append("Forte résonance avec les valeurs et la culture de l'entreprise")
            elif category == "career_goals":
                strengths.append("Objectifs de carrière bien alignés avec les opportunités offertes")
            elif category == "technical_skills":
                strengths.append("Profil technique très adapté aux besoins du poste")
    
    # Ajouter un point fort global si le profil est exceptionnellement bon
    if len(strengths) >= 3:
        strengths.insert(0, "Correspondance globale exceptionnelle entre le profil et le poste")
    
    return strengths

def identify_matching_gaps(category_scores: Dict[str, float]) -> List[str]:
    """
    Identifie les écarts ou points de divergence entre le candidat et l'entreprise.
    
    Args:
        category_scores: Dictionnaire des scores par catégorie
        
    Returns:
        Liste des écarts identifiés
    """
    gaps = []
    
    # Définir des seuils pour les différentes catégories
    thresholds = {
        "work_environment": 0.4,
        "work_style": 0.4,
        "values_culture": 0.5,
        "career_goals": 0.5,
        "technical_skills": 0.6
    }
    
    # Vérifier chaque catégorie et ajouter des écarts
    for category, score in category_scores.items():
        if score <= thresholds.get(category, 0.5):
            if category == "work_environment":
                gaps.append("Préférence d'environnement de travail différente de ce qui est proposé")
            elif category == "work_style":
                gaps.append("Style de travail potentiellement incompatible avec l'équipe")
            elif category == "values_culture":
                gaps.append("Potentiel désalignement avec la culture d'entreprise")
            elif category == "career_goals":
                gaps.append("Objectifs de carrière qui pourraient ne pas être satisfaits dans ce poste")
            elif category == "technical_skills":
                gaps.append("Écarts techniques significatifs par rapport aux besoins du poste")
    
    # Si aucun écart significatif n'est détecté
    if not gaps:
        gaps.append("Pas d'écarts significatifs détectés")
    
    return gaps

def generate_matching_recommendations(
    candidate_responses: Dict[str, Any],
    company_responses: Dict[str, Any],
    category_scores: Dict[str, float]
) -> List[str]:
    """
    Génère des recommandations personnalisées basées sur l'analyse des correspondances.
    
    Args:
        candidate_responses: Réponses du candidat au questionnaire
        company_responses: Réponses de l'entreprise au questionnaire
        category_scores: Scores par catégorie
        
    Returns:
        Liste de recommandations personnalisées
    """
    recommendations = []
    
    # Recommandations basées sur les scores par catégorie
    low_scores = [category for category, score in category_scores.items() if score < 0.6]
    
    for category in low_scores:
        if category == "work_environment":
            recommendations.append(
                "Discuter des aménagements possibles de l'environnement de travail lors de l'entretien"
            )
        elif category == "work_style":
            recommendations.append(
                "Aborder les méthodes de travail et l'intégration dans l'équipe pendant l'entretien"
            )
        elif category == "values_culture":
            recommendations.append(
                "Explorer plus en détail la culture d'entreprise et les valeurs communes"
            )
        elif category == "career_goals":
            recommendations.append(
                "Clarifier les opportunités d'évolution et les possibilités d'apprentissage"
            )
        elif category == "technical_skills":
            recommendations.append(
                "Préparer un plan de développement des compétences techniques manquantes"
            )
    
    # Si tout est bon, recommandations générales positives
    if not low_scores:
        recommendations.append(
            "Mettre en avant les points d'alignement forts avec l'entreprise lors de l'entretien"
        )
        recommendations.append(
            "Préparer des exemples concrets illustrant votre affinité avec la culture de l'entreprise"
        )
    
    return recommendations

def integrate_questionnaire_data(
    basic_match_results: Dict[str, Any],
    questionnaire_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Intègre les résultats du matching de questionnaire aux résultats de matching de base.
    
    Args:
        basic_match_results: Résultats du matching basé sur les compétences/expérience
        questionnaire_results: Résultats du matching basé sur les questionnaires
        
    Returns:
        Résultats de matching combinés
    """
    # Extraire les scores de base
    base_overall = basic_match_results.get("overall_score", 0.5)
    
    # Extraire les scores de questionnaire
    quest_overall = questionnaire_results.get("overall_score", 0.5)
    
    # Pondération: 60% base technique, 40% questionnaire
    combined_score = 0.6 * base_overall + 0.4 * quest_overall
    
    # Combiner les détails des scores
    base_details = basic_match_results.get("score_details", [])
    quest_details = [
        {
            "category": f"questionnaire_{cat}",
            "score": score,
            "explanation": f"Évaluation basée sur les préférences de {cat.replace('_', ' ')}"
        }
        for cat, score in questionnaire_results.get("category_scores", {}).items()
    ]
    
    combined_details = base_details + quest_details
    
    # Combiner les forces
    base_strengths = basic_match_results.get("strengths", [])
    quest_strengths = questionnaire_results.get("strengths", [])
    combined_strengths = base_strengths + quest_strengths
    
    # Combiner les écarts
    base_gaps = basic_match_results.get("gaps", [])
    quest_gaps = questionnaire_results.get("gaps", [])
    combined_gaps = base_gaps + quest_gaps
    
    # Combiner les recommandations
    base_recommendations = basic_match_results.get("recommendations", [])
    quest_recommendations = questionnaire_results.get("recommendations", [])
    combined_recommendations = base_recommendations + quest_recommendations
    
    # Construire le résultat final
    return {
        "job_post_id": basic_match_results.get("job_post_id"),
        "candidate_id": basic_match_results.get("candidate_id"),
        "overall_score": combined_score,
        "score_details": combined_details,
        "strengths": combined_strengths,
        "gaps": combined_gaps,
        "recommendations": combined_recommendations,
        "created_at": basic_match_results.get("created_at")
    }
