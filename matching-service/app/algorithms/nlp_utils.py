"""
Utilitaires NLP pour le service de matching Nexten
--------------------------------------------------
Fonctions pour le traitement du langage naturel utilisées dans l'algorithme de matching.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import re
import logging
from typing import List, Set, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """
    Normalise un texte en le mettant en minuscules et en supprimant les caractères spéciaux
    
    Args:
        text: Texte à normaliser
        
    Returns:
        Texte normalisé
    """
    if not text:
        return ""
    
    # Convertir en minuscules
    text = text.lower()
    
    # Supprimer les caractères spéciaux
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extrait les mots-clés importants d'un texte en utilisant TF-IDF
    
    Args:
        text: Texte dont extraire les mots-clés
        max_keywords: Nombre maximum de mots-clés à extraire
        
    Returns:
        Liste des mots-clés extraits
    """
    if not text or len(text.strip()) < 10:
        return []
    
    try:
        # Créer un vectoriseur TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words=['french', 'english'],
            ngram_range=(1, 2)  # Considérer les unigrammes et bigrammes
        )
        
        # Transformer le texte
        tfidf_matrix = vectorizer.fit_transform([text])
        
        # Obtenir les mots-clés
        feature_names = vectorizer.get_feature_names_out()
        scores = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
        
        # Créer un dictionnaire mots-clés / scores
        keyword_scores = {feature_names[i]: scores[i] for i in range(len(feature_names))}
        
        # Trier par score
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les mots-clés
        return [kw[0] for kw in sorted_keywords]
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des mots-clés: {str(e)}", exc_info=True)
        
        # Fallback simple en cas d'erreur
        words = normalize_text(text).split()
        unique_words = []
        
        # Prendre uniquement les mots uniques avec une longueur minimale
        for word in words:
            if word not in unique_words and len(word) > 3:
                unique_words.append(word)
                if len(unique_words) >= max_keywords:
                    break
        
        return unique_words

def calculate_similarity(keywords1: List[str], keywords2: List[str]) -> float:
    """
    Calcule la similarité entre deux ensembles de mots-clés en utilisant le coefficient de Jaccard
    
    Args:
        keywords1: Premier ensemble de mots-clés
        keywords2: Deuxième ensemble de mots-clés
        
    Returns:
        Score de similarité entre 0 et 1
    """
    if not keywords1 or not keywords2:
        return 0.0
    
    # Convertir les listes en ensembles
    set1 = set(keywords1)
    set2 = set(keywords2)
    
    # Calculer l'intersection
    intersection = set1.intersection(set2)
    
    # Calculer l'union
    union = set1.union(set2)
    
    # Calculer le coefficient de Jaccard
    if len(union) > 0:
        similarity = len(intersection) / len(union)
    else:
        similarity = 0.0
    
    return similarity

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Calcule la similarité sémantique entre deux textes en utilisant TF-IDF et similarité cosinus
    
    Args:
        text1: Premier texte
        text2: Deuxième texte
        
    Returns:
        Score de similarité entre 0 et 1
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        # Créer un vectoriseur TF-IDF
        vectorizer = TfidfVectorizer(stop_words=['french', 'english'])
        
        # Transformer les textes
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculer la similarité cosinus
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la similarité sémantique: {str(e)}", exc_info=True)
        return 0.0

def are_skills_similar(skill1: str, skill2: str, threshold: float = 0.85) -> bool:
    """
    Détermine si deux compétences sont similaires (synonymes, variantes, etc.)
    
    Args:
        skill1: Première compétence
        skill2: Deuxième compétence
        threshold: Seuil de similarité pour considérer les compétences comme similaires
        
    Returns:
        True si les compétences sont similaires, False sinon
    """
    # Normalisation
    s1 = normalize_text(skill1)
    s2 = normalize_text(skill2)
    
    # Vérification d'égalité après normalisation
    if s1 == s2:
        return True
    
    # Vérification d'inclusion
    if len(s1) > 3 and len(s2) > 3:
        if s1 in s2 or s2 in s1:
            return True
    
    # Dictionnaire de synonymes et d'abréviations
    skill_synonyms = {
        # Langages
        "js": ["javascript"],
        "ts": ["typescript"],
        "py": ["python"],
        "c#": ["csharp", "dotnet", ".net"],
        
        # Frameworks
        "react": ["reactjs", "react.js"],
        "vue": ["vuejs", "vue.js"],
        "angular": ["angularjs", "angular.js"],
        "django": ["django framework"],
        "flask": ["flask framework"],
        "express": ["expressjs", "express.js"],
        "node": ["nodejs", "node.js"],
        
        # DevOps et cloud
        "aws": ["amazon web services"],
        "azure": ["microsoft azure"],
        "gcp": ["google cloud platform", "google cloud"],
        "k8s": ["kubernetes"],
        "ci/cd": ["continuous integration", "continuous deployment", "devops pipeline"],
        
        # Data
        "ml": ["machine learning"],
        "ai": ["artificial intelligence", "intelligence artificielle"],
        "dl": ["deep learning"],
        "nlp": ["natural language processing", "traitement du langage naturel"],
        
        # Bases de données
        "sql": ["mysql", "postgresql", "mariadb", "tsql", "base de données relationnelle"],
        "nosql": ["mongodb", "couchdb", "cassandra", "dynamodb", "base de données non relationnelle"]
    }
    
    # Vérification dans le dictionnaire des synonymes
    for base_skill, synonyms in skill_synonyms.items():
        if s1 == base_skill and any(syn == s2 for syn in synonyms):
            return True
        if s2 == base_skill and any(syn == s1 for syn in synonyms):
            return True
    
    # Vérification de la distance de Levenshtein pour détecter les fautes d'orthographe
    try:
        from Levenshtein import ratio
        if len(s1) > 3 and len(s2) > 3 and ratio(s1, s2) > threshold:
            return True
    except ImportError:
        pass
    
    return False

def find_common_skills(candidate_skills: List[str], job_skills: List[str]) -> List[str]:
    """
    Trouve les compétences communes entre un candidat et une offre d'emploi
    
    Args:
        candidate_skills: Liste des compétences du candidat
        job_skills: Liste des compétences requises pour le poste
        
    Returns:
        Liste des compétences communes
    """
    common_skills = []
    
    for c_skill in candidate_skills:
        for j_skill in job_skills:
            if are_skills_similar(c_skill, j_skill):
                common_skills.append(j_skill)  # Utiliser la version de l'offre pour la cohérence
                break
    
    return common_skills

def find_missing_skills(candidate_skills: List[str], job_skills: List[str]) -> List[str]:
    """
    Trouve les compétences requises pour le poste mais manquantes chez le candidat
    
    Args:
        candidate_skills: Liste des compétences du candidat
        job_skills: Liste des compétences requises pour le poste
        
    Returns:
        Liste des compétences manquantes
    """
    missing_skills = []
    
    for j_skill in job_skills:
        skill_found = False
        for c_skill in candidate_skills:
            if are_skills_similar(j_skill, c_skill):
                skill_found = True
                break
        
        if not skill_found:
            missing_skills.append(j_skill)
    
    return missing_skills
