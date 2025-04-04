import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configurer le logging
logger = logging.getLogger(__name__)

# Chargement du modèle spaCy (lazy loading)
nlp = None

def load_nlp_model():
    """Charge le modèle spaCy de manière paresseuse"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("fr_core_news_lg")
        except:
            try:
                nlp = spacy.load("en_core_web_lg")
            except:
                nlp = spacy.load("fr_core_news_sm")
    return nlp

async def analyze_questionnaire_responses(
    questionnaire_id: int,
    candidate_id: int, 
    answers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyse les réponses d'un candidat à un questionnaire.
    Retourne une analyse détaillée avec scores, forces, faiblesses et recommandations.
    """
    try:
        # Récupérer les informations du questionnaire (à remplacer par une requête DB)
        # Cette partie simule la récupération d'un questionnaire
        questionnaire = get_mock_questionnaire(questionnaire_id)
        
        # Analyser les réponses
        analysis_results = analyze_responses(questionnaire, answers)
        
        # Générer les recommandations
        strengths, areas_for_improvement, job_categories = generate_recommendations(analysis_results)
        
        # Construire le résultat final
        result = {
            "candidate_id": candidate_id,
            "questionnaire_id": questionnaire_id,
            "scores": analysis_results["scores"],
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "recommended_job_categories": job_categories,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Analyse des réponses au questionnaire {questionnaire_id} pour le candidat {candidate_id} complétée")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des réponses: {str(e)}")
        raise

def get_mock_questionnaire(questionnaire_id: int) -> Dict[str, Any]:
    """
    Simule la récupération d'un questionnaire depuis la base de données.
    Dans une implémentation réelle, cette fonction interrogerait la base de données.
    """
    # Questionnaire technique
    if questionnaire_id == 1:
        return {
            "id": 1,
            "title": "Évaluation des compétences techniques",
            "description": "Questionnaire pour évaluer les compétences techniques des candidats",
            "categories": ["technical", "programming", "database", "soft_skills"],
            "questions": [
                {
                    "id": 1,
                    "text": "Quel est votre niveau en Python?",
                    "category": "programming",
                    "type": "rating",
                    "options": ["1", "2", "3", "4", "5"]
                },
                {
                    "id": 2,
                    "text": "Décrivez votre expérience avec les bases de données SQL et NoSQL.",
                    "category": "database",
                    "type": "text"
                },
                {
                    "id": 3,
                    "text": "Comment gérez-vous les situations de stress au travail?",
                    "category": "soft_skills",
                    "type": "text"
                },
                {
                    "id": 4,
                    "text": "Quel est votre niveau en développement web front-end?",
                    "category": "programming",
                    "type": "rating",
                    "options": ["1", "2", "3", "4", "5"]
                }
            ]
        }
    # Questionnaire de compatibilité d'entreprise
    elif questionnaire_id == 2:
        return {
            "id": 2,
            "title": "Compatibilité culturelle",
            "description": "Évaluer la compatibilité avec la culture d'entreprise",
            "categories": ["culture", "values", "work_style"],
            "questions": [
                {
                    "id": 1,
                    "text": "Comment préférez-vous travailler : en équipe ou individuellement?",
                    "category": "work_style",
                    "type": "choice",
                    "options": ["Équipe", "Individuellement", "Les deux dépendant du contexte"]
                },
                {
                    "id": 2,
                    "text": "Quelles valeurs d'entreprise sont les plus importantes pour vous?",
                    "category": "values",
                    "type": "text"
                }
            ]
        }
    # Fallback
    return {
        "id": questionnaire_id,
        "title": "Questionnaire général",
        "description": "Questionnaire d'évaluation",
        "categories": ["general"],
        "questions": [
            {
                "id": 1,
                "text": "Question générique",
                "category": "general",
                "type": "text"
            }
        ]
    }

def analyze_responses(questionnaire: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyse les réponses aux questions en fonction de leur type.
    """
    categories = questionnaire.get("categories", ["general"])
    analysis = {
        "scores": {cat: 0.0 for cat in categories},
        "responses_by_category": {cat: [] for cat in categories},
        "details": []
    }
    
    # Créer un dictionnaire pour accéder facilement aux questions par ID
    questions_by_id = {q["id"]: q for q in questionnaire["questions"]}
    
    # Réponses de référence pour comparaison (pourrait être chargé depuis une base de données)
    reference_responses = get_reference_responses()
    
    for answer in answers:
        question_id = answer.get("question_id")
        value = answer.get("value")
        
        if question_id not in questions_by_id:
            continue
            
        question = questions_by_id[question_id]
        category = question.get("category", "general")
        
        # Ajouter la réponse à la liste des réponses par catégorie
        analysis["responses_by_category"][category].append({
            "question": question["text"],
            "answer": value
        })
        
        # Analyser en fonction du type de question
        if question.get("type") == "rating":
            # Convertir en float si nécessaire
            if isinstance(value, str):
                try:
                    value = float(value)
                except ValueError:
                    value = 0
                    
            # Normaliser sur une échelle de 0 à 1
            max_rating = 5  # Supposons que le maximum est 5
            normalized_score = value / max_rating
            
            analysis["details"].append({
                "question_id": question_id,
                "score": normalized_score,
                "category": category,
                "notes": f"Auto-évaluation: {value}/{max_rating}"
            })
            
            # Ajouter à la moyenne de la catégorie
            analysis["scores"][category] = (
                analysis["scores"][category] + normalized_score
            ) / 2  # Simple moyenne, peut être amélioré
            
        elif question.get("type") == "text":
            # Analyser le texte de la réponse
            if category in reference_responses and value:
                # Utiliser NLP pour comparer avec des réponses de référence
                similarity_score = text_similarity_score(value, reference_responses[category])
                
                analysis["details"].append({
                    "question_id": question_id,
                    "score": similarity_score,
                    "category": category,
                    "notes": "Basé sur la similarité avec les réponses de référence"
                })
                
                # Ajouter à la moyenne de la catégorie
                analysis["scores"][category] = (
                    analysis["scores"][category] + similarity_score
                ) / 2  # Simple moyenne, peut être amélioré
                
        elif question.get("type") == "choice":
            # Analyser la réponse à choix
            if category == "work_style" and value:
                # Exemple spécifique pour work_style
                if value == "Les deux dépendant du contexte":
                    score = 0.9  # Flexibilité valorisée
                elif value == "Équipe":
                    score = 0.8  # Travail d'équipe valorisé
                else:  # Individuellement
                    score = 0.6  # Travail individuel moins valorisé dans cet exemple
                
                analysis["details"].append({
                    "question_id": question_id,
                    "score": score,
                    "category": category,
                    "notes": f"Préférence de travail: {value}"
                })
                
                # Ajouter à la moyenne de la catégorie
                analysis["scores"][category] = (
                    analysis["scores"][category] + score
                ) / 2  # Simple moyenne
    
    # Calculer un score global
    if analysis["scores"]:
        analysis["scores"]["overall"] = sum(
            score for cat, score in analysis["scores"].items() if cat != "overall"
        ) / len(analysis["scores"])
    else:
        analysis["scores"]["overall"] = 0.0
        
    return analysis

def text_similarity_score(input_text: str, reference_texts: List[str]) -> float:
    """
    Calcule un score de similarité entre le texte d'entrée et une liste de textes de référence.
    Utilise TF-IDF et similarité cosinus.
    """
    if not input_text or not reference_texts:
        return 0.0
        
    # Préparer les textes
    all_texts = [input_text] + reference_texts
    
    # Vectoriser avec TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except:
        return 0.0
        
    # Calculer la similarité entre l'entrée et chaque référence
    input_vector = tfidf_matrix[0:1]
    reference_vectors = tfidf_matrix[1:]
    
    # Calculer les similarités
    similarities = cosine_similarity(input_vector, reference_vectors).flatten()
    
    # Retourner la similarité maximale
    if len(similarities) > 0:
        return float(max(similarities))
    else:
        return 0.0

def get_reference_responses() -> Dict[str, List[str]]:
    """
    Retourne des réponses de référence par catégorie pour la comparaison.
    Dans une implémentation réelle, ces réponses pourraient être stockées en base de données
    ou calibrées par des experts.
    """
    return {
        "programming": [
            "Je code régulièrement en Python et j'ai développé plusieurs projets significatifs.",
            "J'utilise Python quotidiennement pour l'analyse de données et le développement web.",
            "J'ai contribué à des projets open source en Python et maîtrise les bonnes pratiques."
        ],
        "database": [
            "J'ai travaillé avec MySQL et PostgreSQL pour des applications à forte charge.",
            "J'ai de l'expérience avec MongoDB et Redis pour des applications nécessitant une grande scalabilité.",
            "J'ai conçu et optimisé des schémas de bases de données pour des applications d'entreprise."
        ],
        "soft_skills": [
            "Je gère le stress en priorisant les tâches et en pratiquant des techniques de respiration.",
            "Je reste calme sous pression et j'identifie rapidement les actions prioritaires.",
            "Je communique ouvertement avec l'équipe et je n'hésite pas à demander de l'aide si nécessaire."
        ],
        "values": [
            "Je valorise la transparence, l'innovation et le respect dans une entreprise.",
            "L'équilibre vie professionnelle/vie personnelle, la diversité et l'éthique sont essentiels pour moi.",
            "Je recherche des entreprises qui valorisent l'apprentissage continu et l'autonomie."
        ]
    }

def generate_recommendations(analysis: Dict[str, Any]) -> tuple:
    """
    Génère des recommandations basées sur l'analyse des réponses.
    """
    strengths = []
    areas_for_improvement = []
    job_categories = []
    
    # Identifier les forces (scores > 0.7)
    for category, score in analysis["scores"].items():
        if category == "overall":
            continue
            
        if score > 0.7:
            strengths.append(category_to_readable(category))
        elif score < 0.5:
            areas_for_improvement.append(category_to_readable(category))
    
    # Recommandations de catégories d'emploi basées sur les forces
    if "programming" in analysis["scores"] and analysis["scores"]["programming"] > 0.7:
        job_categories.append("Développeur logiciel")
        
    if "database" in analysis["scores"] and analysis["scores"]["database"] > 0.7:
        job_categories.append("Ingénieur base de données")
        
    if "soft_skills" in analysis["scores"] and analysis["scores"]["soft_skills"] > 0.7:
        job_categories.append("Chef de projet")
        
    if "technical" in analysis["scores"] and analysis["scores"]["technical"] > 0.7:
        job_categories.append("Ingénieur système")
        
    # Ajouter d'autres catégories en fonction des combinaisons de compétences
    if (
        "programming" in analysis["scores"] and analysis["scores"]["programming"] > 0.6 and
        "database" in analysis["scores"] and analysis["scores"]["database"] > 0.6
    ):
        job_categories.append("Développeur backend")
    
    # S'il n'y a pas de catégories recommandées, ajouter une catégorie générique
    if not job_categories:
        job_categories.append("Analyste Junior")
    
    return strengths, areas_for_improvement, job_categories

def category_to_readable(category: str) -> str:
    """
    Convertit une clé de catégorie en texte lisible.
    """
    category_mapping = {
        "programming": "Programmation",
        "database": "Bases de données",
        "soft_skills": "Compétences interpersonnelles",
        "technical": "Compétences techniques",
        "culture": "Adaptation culturelle",
        "values": "Alignement des valeurs",
        "work_style": "Style de travail",
        "general": "Connaissances générales"
    }
    
    return category_mapping.get(category, category.replace("_", " ").title())
