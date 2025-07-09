#!/usr/bin/env python3
"""
🚀 CV Parser Optimizer - Nextvision V3.0
==========================================

Optimiseur de prompts pour améliorer la performance du CV parsing de 54.5% à >90%

Key Features:
- Prompts optimisés pour extraction de données
- Validation multi-niveaux
- Retry logic intelligent
- Formatage standardisé
- Performance monitoring

Author: Nextvision Team
Version: 3.0.0 - Performance Optimization
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DataQuality(Enum):
    """Niveaux de qualité des données extraites"""
    EXCELLENT = "excellent"    # >95% données valides
    GOOD = "good"             # 80-95% données valides  
    ACCEPTABLE = "acceptable"  # 60-80% données valides
    POOR = "poor"             # <60% données valides

@dataclass
class CVExtractionResult:
    """Résultat d'extraction de CV optimisé"""
    # Informations personnelles (OBLIGATOIRES)
    nom: str = ""
    prenom: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""
    
    # Expérience professionnelle (CRITIQUE)
    annees_experience: int = 0
    poste_actuel: str = ""
    entreprise_actuelle: str = ""
    postes_precedents: List[str] = None
    entreprises_precedentes: List[str] = None
    
    # Compétences (CRITIQUE)
    competences_techniques: List[str] = None
    competences_transversales: List[str] = None
    technologies: List[str] = None
    certifications: List[str] = None
    
    # Formation (IMPORTANT)
    niveau_formation: str = ""
    domaine_formation: str = ""
    etablissement: str = ""
    diplomes: List[str] = None
    
    # Informations complémentaires
    langues: List[str] = None
    objectif_professionnel: str = ""
    resume_profil: str = ""
    secteurs_experience: List[str] = None
    
    # Métadonnées de qualité
    quality_score: float = 0.0
    quality_level: DataQuality = DataQuality.POOR
    missing_fields: List[str] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        """Initialise les listes vides"""
        if self.postes_precedents is None:
            self.postes_precedents = []
        if self.entreprises_precedentes is None:
            self.entreprises_precedentes = []
        if self.competences_techniques is None:
            self.competences_techniques = []
        if self.competences_transversales is None:
            self.competences_transversales = []
        if self.technologies is None:
            self.technologies = []
        if self.certifications is None:
            self.certifications = []
        if self.diplomes is None:
            self.diplomes = []
        if self.langues is None:
            self.langues = []
        if self.secteurs_experience is None:
            self.secteurs_experience = []
        if self.missing_fields is None:
            self.missing_fields = []

class CVParserOptimizer:
    """Optimiseur de parsing CV avec prompts améliorés"""
    
    def __init__(self):
        self.required_fields = [
            "nom", "prenom", "email", "telephone", 
            "annees_experience", "competences_techniques"
        ]
        self.important_fields = [
            "poste_actuel", "entreprise_actuelle", "niveau_formation", 
            "domaine_formation", "technologies"
        ]
        
    def get_optimized_prompt(self, cv_text: str) -> str:
        """Génère un prompt optimisé pour l'extraction de données CV"""
        
        prompt = f"""
Tu es un expert en extraction de données CV avec 15 ans d'expérience. 
Analyse ce CV et extrais EXACTEMENT les informations demandées avec une précision maximale.

=== RÈGLES CRITIQUES ===
1. Si une information n'est PAS présente, ne l'invente JAMAIS
2. Retourne "N/A" ou liste vide [] si donnée manquante
3. Sois EXTRÊMEMENT précis sur les années d'expérience
4. Extrais TOUTES les compétences techniques mentionnées
5. Sépare clairement nom/prénom même si format inhabituel

=== CV À ANALYSER ===
{cv_text}

=== FORMAT DE RÉPONSE OBLIGATOIRE ===
{{
    "nom": "Nom de famille EXACT du CV",
    "prenom": "Prénom EXACT du CV", 
    "email": "adresse@email.com ou N/A",
    "telephone": "numéro complet ou N/A",
    "adresse": "adresse complète ou N/A",
    
    "annees_experience": nombre_exact_d_annees_pro,
    "poste_actuel": "titre exact du poste actuel ou N/A",
    "entreprise_actuelle": "nom exact entreprise actuelle ou N/A",
    "postes_precedents": ["poste1", "poste2", "poste3"],
    "entreprises_precedentes": ["entreprise1", "entreprise2"],
    
    "competences_techniques": ["compétence1", "compétence2", "compétence3"],
    "competences_transversales": ["leadership", "gestion", "communication"],
    "technologies": ["Python", "Java", "React", "Docker"],
    "certifications": ["AWS", "PMP", "Scrum Master"],
    
    "niveau_formation": "Bac+3/Bac+5/Master/Doctorat ou N/A",
    "domaine_formation": "Informatique/Commerce/Ingénieur ou N/A", 
    "etablissement": "nom école/université ou N/A",
    "diplomes": ["diplôme1", "diplôme2"],
    
    "langues": ["Français", "Anglais", "Espagnol"],
    "objectif_professionnel": "objectif mentionné ou N/A",
    "resume_profil": "résumé profil en 1-2 phrases ou N/A",
    "secteurs_experience": ["IT", "Finance", "Conseil"]
}}

ATTENTION: Respecte EXACTEMENT ce format JSON. Une seule réponse. Sois factuel et précis.
"""
        return prompt
    
    def validate_extraction(self, result: Dict[str, Any]) -> Tuple[float, DataQuality, List[str]]:
        """Valide la qualité de l'extraction"""
        
        total_fields = len(self.required_fields) + len(self.important_fields)
        valid_fields = 0
        missing_fields = []
        
        # Validation champs obligatoires (poids 2x)
        for field in self.required_fields:
            value = result.get(field, "")
            if value and value != "N/A" and value != "" and value != 0:
                valid_fields += 2
            else:
                missing_fields.append(field)
        
        # Validation champs importants (poids 1x)
        for field in self.important_fields:
            value = result.get(field, "")
            if value and value != "N/A" and value != "":
                valid_fields += 1
            else:
                missing_fields.append(field)
        
        # Validation spécifique
        
        # Email valide
        email = result.get("email", "")
        if email and "@" in email and "." in email:
            valid_fields += 1
        
        # Téléphone valide  
        phone = result.get("telephone", "")
        if phone and len(re.sub(r'[^\d]', '', phone)) >= 8:
            valid_fields += 1
        
        # Expérience cohérente
        exp = result.get("annees_experience", 0)
        if isinstance(exp, int) and 0 <= exp <= 50:
            valid_fields += 1
        
        # Compétences non vides
        comp_tech = result.get("competences_techniques", [])
        if comp_tech and len(comp_tech) > 0:
            valid_fields += 2
        
        # Score final
        max_possible = (len(self.required_fields) * 2) + len(self.important_fields) + 5
        quality_score = (valid_fields / max_possible) * 100
        
        # Déterminer niveau de qualité
        if quality_score >= 95:
            quality_level = DataQuality.EXCELLENT
        elif quality_score >= 80:
            quality_level = DataQuality.GOOD
        elif quality_score >= 60:
            quality_level = DataQuality.ACCEPTABLE
        else:
            quality_level = DataQuality.POOR
            
        return quality_score, quality_level, missing_fields
    
    def enhance_extraction(self, raw_result: Dict[str, Any]) -> CVExtractionResult:
        """Améliore et standardise l'extraction"""
        
        # Nettoyage et standardisation
        enhanced = {}
        
        # Nettoyage nom/prénom
        nom = str(raw_result.get("nom", "")).strip().title()
        prenom = str(raw_result.get("prenom", "")).strip().title()
        enhanced["nom"] = nom if nom != "N/A" else ""
        enhanced["prenom"] = prenom if prenom != "N/A" else ""
        
        # Nettoyage email
        email = str(raw_result.get("email", "")).strip().lower()
        enhanced["email"] = email if "@" in email else ""
        
        # Nettoyage téléphone
        phone = str(raw_result.get("telephone", "")).strip()
        # Garder seulement chiffres et espaces/tirets
        phone_clean = re.sub(r'[^\d\s\-\.\+\(\)]', '', phone)
        enhanced["telephone"] = phone_clean if len(re.sub(r'[^\d]', '', phone_clean)) >= 8 else ""
        
        # Autres champs texte
        text_fields = ["adresse", "poste_actuel", "entreprise_actuelle", 
                      "niveau_formation", "domaine_formation", "etablissement",
                      "objectif_professionnel", "resume_profil"]
        
        for field in text_fields:
            value = str(raw_result.get(field, "")).strip()
            enhanced[field] = value if value != "N/A" else ""
        
        # Années d'expérience
        try:
            exp = int(raw_result.get("annees_experience", 0))
            enhanced["annees_experience"] = max(0, min(exp, 50))  # Cap à 50 ans
        except (ValueError, TypeError):
            enhanced["annees_experience"] = 0
        
        # Listes
        list_fields = ["postes_precedents", "entreprises_precedentes", 
                      "competences_techniques", "competences_transversales",
                      "technologies", "certifications", "diplomes", 
                      "langues", "secteurs_experience"]
        
        for field in list_fields:
            value = raw_result.get(field, [])
            if isinstance(value, list):
                # Nettoyer et filtrer
                cleaned = [str(item).strip() for item in value if item and str(item).strip() != "N/A"]
                enhanced[field] = cleaned
            else:
                enhanced[field] = []
        
        # Créer l'objet résultat
        result = CVExtractionResult(**enhanced)
        
        # Calculer la qualité
        quality_score, quality_level, missing_fields = self.validate_extraction(enhanced)
        
        result.quality_score = round(quality_score, 1)
        result.quality_level = quality_level
        result.missing_fields = missing_fields
        result.confidence_score = min(95.0, quality_score * 1.1)
        
        return result
    
    def should_retry(self, result: CVExtractionResult, attempt: int) -> bool:
        """Détermine si un retry est nécessaire"""
        
        if attempt >= 3:  # Max 3 tentatives
            return False
            
        # Retry si qualité insuffisante
        if result.quality_level in [DataQuality.POOR]:
            return True
            
        # Retry si champs critiques manquants
        critical_missing = any(field in result.missing_fields 
                             for field in ["nom", "prenom", "competences_techniques"])
        
        if critical_missing:
            return True
            
        return False
    
    def get_retry_prompt(self, cv_text: str, previous_result: CVExtractionResult, attempt: int) -> str:
        """Génère un prompt de retry amélioré"""
        
        missing_info = ", ".join(previous_result.missing_fields)
        
        prompt = f"""
RETRY #{attempt} - EXTRACTION CV AMÉLIORÉE

Tentative précédente INSUFFISANTE. Champs manquants: {missing_info}

=== ANALYSE PLUS APPROFONDIE REQUISE ===
Lis TRÈS attentivement le CV ci-dessous et extrais TOUTES les informations possibles.

FOCUS SPÉCIAL sur:
- Nom/Prénom (même si format inhabituel)
- TOUTES les compétences techniques mentionnées
- Expérience EXACTE (compter les années)
- Formation précise

=== CV À RÉANALYSER ===
{cv_text}

=== INSTRUCTIONS RENFORCÉES ===
1. Lis CHAQUE ligne du CV attentivement
2. Cherche les informations dans TOUT le document
3. N'ignore AUCUNE compétence technique
4. Calcule précisément les années d'expérience
5. Si format nom inhabituel, devine intelligemment

RETOURNE le même format JSON que demandé précédemment.
Sois PLUS précis et exhaustif cette fois.
"""
        return prompt

# ================================
# TESTS ET VALIDATION
# ================================

def test_cv_optimizer():
    """Test de l'optimiseur CV"""
    
    # CV test simulé
    cv_test = """
    Jean DUPONT
    Développeur Senior Python
    jean.dupont@email.com
    06 12 34 56 78
    
    EXPÉRIENCE:
    2020-2024: Développeur Senior - TechCorp
    2018-2020: Développeur Python - StartupXYZ
    
    COMPÉTENCES:
    - Python, Django, Flask
    - React, JavaScript
    - Docker, Kubernetes
    - PostgreSQL, MongoDB
    
    FORMATION:
    Master Informatique - EPITECH (2018)
    """
    
    optimizer = CVParserOptimizer()
    
    # Test prompt génération
    prompt = optimizer.get_optimized_prompt(cv_test)
    print("✅ Prompt généré")
    
    # Simulation résultat parsing
    mock_result = {
        "nom": "DUPONT",
        "prenom": "Jean", 
        "email": "jean.dupont@email.com",
        "telephone": "06 12 34 56 78",
        "annees_experience": 6,
        "competences_techniques": ["Python", "Django", "Flask", "React", "Docker"],
        "niveau_formation": "Master",
        "domaine_formation": "Informatique"
    }
    
    # Test validation
    enhanced_result = optimizer.enhance_extraction(mock_result)
    
    print(f"✅ Qualité: {enhanced_result.quality_level.value} ({enhanced_result.quality_score}%)")
    print(f"✅ Confiance: {enhanced_result.confidence_score}%")
    print(f"✅ Champs manquants: {len(enhanced_result.missing_fields)}")
    
    return enhanced_result

if __name__ == "__main__":
    print("🚀 === CV PARSER OPTIMIZER V3.0 ===")
    print("Optimiseur de performance pour parsing CV Nextvision")
    print()
    
    # Test de l'optimiseur
    result = test_cv_optimizer()
    
    print("\n📊 === RÉSULTAT TEST ===")
    print(f"Nom: {result.nom} {result.prenom}")
    print(f"Email: {result.email}")
    print(f"Expérience: {result.annees_experience} ans")
    print(f"Compétences: {len(result.competences_techniques)} identifiées")
    print(f"Score qualité: {result.quality_score}% ({result.quality_level.value})")
    
    if result.quality_score >= 90:
        print("🎯 ✅ OBJECTIF >90% ATTEINT!")
    else:
        print(f"🎯 ⚠️ Objectif >90% non atteint ({result.quality_score}%)")
        
    print("\n🔧 Intégration recommandée:")
    print("1. Remplacer les prompts actuels par get_optimized_prompt()")
    print("2. Ajouter la validation avec validate_extraction()")  
    print("3. Implémenter la logique de retry avec should_retry()")
    print("4. Utiliser enhance_extraction() pour la standardisation")
