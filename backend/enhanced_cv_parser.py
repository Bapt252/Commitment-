#!/usr/bin/env python3
"""
🚀 Enhanced CV Parser - Optimisation du Parser Existant
=======================================================

Améliore le parser CV/FDP existant avec :
- Prompts optimisés pour >90% qualité
- Validation multi-niveaux
- Retry logic intelligent
- Compatible avec l'architecture existante

Author: Nextvision Team
Version: 3.0 - Real Integration
"""

import json
import re
import time
import openai
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import de l'optimiseur
from cv_parser_optimizer import CVParserOptimizer, CVExtractionResult, DataQuality

class EnhancedCVParser:
    """Parser CV amélioré qui s'intègre avec le système existant"""
    
    def __init__(self, api_key: str = None):
        self.optimizer = CVParserOptimizer()
        
        # Utiliser la clé API existante ou celle fournie
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        # Configuration OpenAI optimisée
        self.model = os.environ.get('MODEL', 'gpt-3.5-turbo')
        self.temperature = 0.2  # Plus bas pour plus de précision
        self.max_tokens = 2500   # Plus élevé pour les CVs complexes
    
    def extract_cv_info_with_enhanced_gpt(self, cv_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Parse CV avec GPT optimisé - Compatible avec l'API existante
        
        Cette fonction remplace/améliore la fonction existante analyze_with_gpt()
        """
        
        if not self.api_key:
            raise Exception("Clé API OpenAI non configurée")
        
        # Limiter la taille du contenu
        if len(cv_text) > 20000:
            cv_text = cv_text[:20000] + "...[contenu tronqué]"
        
        # Tentatives avec retry logic
        for attempt in range(1, max_retries + 1):
            try:
                # Générer le prompt selon la tentative
                if attempt == 1:
                    prompt = self.optimizer.get_optimized_prompt(cv_text)
                else:
                    # Retry avec prompt adaptatif
                    prompt = self.optimizer.get_retry_prompt(cv_text, previous_result, attempt)
                
                # Appel OpenAI optimisé
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es un expert en extraction de données CV avec 15 ans d'expérience. Tu es extrêmement précis et ne jamais inventer d'informations."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                # Extraire et parser la réponse
                result_text = response.choices[0].message.content.strip()
                raw_result = self.parse_gpt_response(result_text)
                
                # Améliorer l'extraction avec l'optimiseur
                enhanced_result = self.optimizer.enhance_extraction(raw_result)
                
                # Vérifier si retry nécessaire
                if not self.optimizer.should_retry(enhanced_result, attempt):
                    # Convertir en format compatible avec l'API existante
                    return self.convert_to_api_format(enhanced_result)
                
                previous_result = enhanced_result
                
            except Exception as e:
                if attempt == max_retries:
                    # En cas d'échec final, retourner un résultat minimal
                    return {
                        "success": False,
                        "error": f"Échec après {max_retries} tentatives: {str(e)}",
                        "quality_score": 0,
                        "data": {}
                    }
                
                print(f"Tentative {attempt} échouée: {e}")
                time.sleep(1)  # Pause avant retry
        
        # Ne devrait pas arriver
        return {"success": False, "error": "Erreur inattendue"}
    
    def parse_gpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse la réponse GPT en JSON"""
        
        try:
            # Essayer de parser directement
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Extraire le JSON du markdown si nécessaire
            json_pattern = r'```json\s*(.*?)\s*```'
            match = re.search(json_pattern, response_text, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            
            # Dernière tentative : extraire JSON brut
            json_pattern2 = r'\{.*\}'
            match2 = re.search(json_pattern2, response_text, re.DOTALL)
            
            if match2:
                return json.loads(match2.group(0))
            
            # Si tout échoue, retourner structure vide
            return {}
    
    def convert_to_api_format(self, enhanced_result: CVExtractionResult) -> Dict[str, Any]:
        """Convertit le résultat optimisé au format API existant"""
        
        # Format compatible avec ton API existante
        api_result = {
            "success": enhanced_result.quality_score >= 60,  # Seuil minimum
            "quality_score": enhanced_result.quality_score,
            "quality_level": enhanced_result.quality_level.value,
            "confidence": enhanced_result.confidence_score,
            "missing_fields": enhanced_result.missing_fields,
            
            # Données principales
            "data": {
                # Informations personnelles
                "nom": enhanced_result.nom,
                "prenom": enhanced_result.prenom,
                "email": enhanced_result.email,
                "telephone": enhanced_result.telephone,
                "adresse": enhanced_result.adresse,
                
                # Expérience
                "annees_experience": enhanced_result.annees_experience,
                "poste_actuel": enhanced_result.poste_actuel,
                "entreprise_actuelle": enhanced_result.entreprise_actuelle,
                "postes_precedents": enhanced_result.postes_precedents,
                "entreprises_precedentes": enhanced_result.entreprises_precedentes,
                
                # Compétences
                "competences_techniques": enhanced_result.competences_techniques,
                "competences_transversales": enhanced_result.competences_transversales,
                "technologies": enhanced_result.technologies,
                "certifications": enhanced_result.certifications,
                
                # Formation
                "niveau_formation": enhanced_result.niveau_formation,
                "domaine_formation": enhanced_result.domaine_formation,
                "etablissement": enhanced_result.etablissement,
                "diplomes": enhanced_result.diplomes,
                
                # Autres
                "langues": enhanced_result.langues,
                "objectif_professionnel": enhanced_result.objectif_professionnel,
                "resume_profil": enhanced_result.resume_profil,
                "secteurs_experience": enhanced_result.secteurs_experience
            }
        }
        
        return api_result
    
    def analyze_with_gpt(self, text: str) -> Dict[str, Any]:
        """
        Fonction de compatibilité avec l'API existante
        
        Cette fonction remplace directement analyze_with_gpt() dans parse_fdp_gpt.py
        """
        return self.extract_cv_info_with_enhanced_gpt(text)

# ================================
# FONCTIONS DE COMPATIBILITÉ API
# ================================

def create_enhanced_parser() -> EnhancedCVParser:
    """Crée une instance du parser amélioré"""
    return EnhancedCVParser()

def enhanced_analyze_with_gpt(text: str) -> Dict[str, Any]:
    """
    Fonction de remplacement pour analyze_with_gpt() existante
    
    Usage: Remplacer l'import dans gpt_parser.py par cette fonction
    """
    parser = create_enhanced_parser()
    return parser.analyze_with_gpt(text)

# ================================
# INTÉGRATION AVEC FLASK/FASTAPI
# ================================

def enhance_existing_api():
    """
    Guide d'intégration avec l'API existante
    
    1. Dans gpt_parser.py, remplacer :
       from parse_fdp_gpt import analyze_with_gpt
       
       Par :
       from enhanced_cv_parser import enhanced_analyze_with_gpt as analyze_with_gpt
    
    2. Ou modifier parse_fdp_gpt.py pour utiliser cette classe
    """
    return {
        "integration_steps": [
            "1. Backup du parser existant",
            "2. Remplacer analyze_with_gpt() par enhanced_analyze_with_gpt()",
            "3. Tester avec quelques CVs",
            "4. Mesurer l'amélioration de qualité",
            "5. Déployer en production"
        ]
    }

# ================================
# TESTS D'INTÉGRATION
# ================================

def test_integration_with_real_cv(cv_file_path: str) -> Dict[str, Any]:
    """Teste l'intégration avec un vrai CV"""
    
    parser = create_enhanced_parser()
    
    # Simuler l'extraction de texte (comme fait dans ton système)
    with open(cv_file_path, 'r', encoding='utf-8') as f:
        cv_text = f.read()
    
    start_time = time.time()
    
    try:
        # Parser avec le système amélioré
        result = parser.analyze_with_gpt(cv_text)
        processing_time = time.time() - start_time
        
        return {
            "test_success": True,
            "processing_time": processing_time,
            "quality_score": result.get("quality_score", 0),
            "api_compatible": "data" in result,
            "result": result
        }
        
    except Exception as e:
        return {
            "test_success": False,
            "error": str(e),
            "processing_time": time.time() - start_time
        }

if __name__ == "__main__":
    print("🚀 === ENHANCED CV PARSER - INTÉGRATION RÉELLE ===")
    print("Parser optimisé compatible avec l'architecture Commitment- existante")
    print()
    
    # Test de base
    parser = create_enhanced_parser()
    
    cv_test = """
    Jean MARTIN
    Développeur Full-Stack
    jean.martin@email.com
    06 12 34 56 78
    
    EXPÉRIENCE:
    2020-2024: Développeur Senior - TechCorp
    2018-2020: Développeur Python - StartupXYZ
    
    COMPÉTENCES:
    - Python, Django, Flask
    - React, JavaScript
    - Docker, PostgreSQL
    """
    
    print("🧪 Test avec CV exemple...")
    result = parser.analyze_with_gpt(cv_test)
    
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📊 Qualité: {result.get('quality_score', 0):.1f}%")
    print(f"🎯 Compatible API: {'data' in result}")
    
    print("\n💡 === INTÉGRATION ===")
    print("Pour intégrer dans ton système existant :")
    print("1. Copier ce fichier dans backend/")
    print("2. Dans gpt_parser.py, remplacer l'import analyze_with_gpt")
    print("3. Tester avec tes CVs réels")
    print("4. Mesurer l'amélioration vs 54.5% baseline")
