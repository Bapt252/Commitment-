"""
Module pour l'intégration de l'API GPT dans le système de parsing

Ce module permet d'utiliser les modèles GPT pour extraire des informations 
à partir de documents (CV, offres d'emploi, etc.) de manière plus précise et contextuelle.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import openai
from dotenv import load_dotenv

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4")


class GPTParser:
    """
    Parser utilisant l'API GPT pour extraire des informations structurées 
    à partir de textes non structurés.
    """
    
    def __init__(self, model: str = None):
        """
        Initialise le parser GPT.
        
        Args:
            model: Modèle GPT à utiliser (par défaut: celui défini dans .env)
        """
        self.model = model or GPT_MODEL
        
        if not openai.api_key:
            logger.warning("Clé API OpenAI non définie. Veuillez définir OPENAI_API_KEY dans le fichier .env")
        
        # Vérifier que le modèle est supporté
        self._check_model()
        
        logger.info(f"GPTParser initialisé avec le modèle: {self.model}")
    
    def _check_model(self):
        """Vérifie que le modèle spécifié est valide et disponible."""
        valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        if self.model not in valid_models:
            logger.warning(f"Modèle {self.model} non reconnu. Utilisation de gpt-4 par défaut.")
            self.model = "gpt-4"
    
    def parse_cv(self, text: str) -> Dict[str, Any]:
        """
        Parse un CV en utilisant GPT pour extraire les informations structurées.
        
        Args:
            text: Texte du CV
            
        Returns:
            Dict: Données structurées extraites du CV
        """
        prompt = self._create_cv_prompt(text)
        
        try:
            response = self._call_gpt_api(prompt)
            parsed_data = self._process_gpt_response(response)
            
            # Ajouter des scores de confiance
            confidence_scores = self._calculate_confidence_scores(parsed_data)
            
            return {
                "extracted_data": parsed_data,
                "confidence_scores": confidence_scores
            }
        except Exception as e:
            logger.error(f"Erreur lors du parsing du CV avec GPT: {e}")
            # Retourner un dictionnaire vide en cas d'erreur plutôt que de faire échouer
            return {"extracted_data": {}, "confidence_scores": {}}
    
    def parse_job_posting(self, text: str) -> Dict[str, Any]:
        """
        Parse une offre d'emploi en utilisant GPT pour extraire les informations structurées.
        
        Args:
            text: Texte de l'offre d'emploi
            
        Returns:
            Dict: Données structurées extraites de l'offre
        """
        prompt = self._create_job_prompt(text)
        
        try:
            response = self._call_gpt_api(prompt)
            parsed_data = self._process_gpt_response(response)
            
            # Ajouter des scores de confiance
            confidence_scores = self._calculate_confidence_scores(parsed_data)
            
            return {
                "extracted_data": parsed_data,
                "confidence_scores": confidence_scores
            }
        except Exception as e:
            logger.error(f"Erreur lors du parsing de l'offre d'emploi avec GPT: {e}")
            return {"extracted_data": {}, "confidence_scores": {}}
    
    def parse_company_questionnaire(self, text: str) -> Dict[str, Any]:
        """
        Parse un questionnaire d'entreprise en utilisant GPT.
        
        Args:
            text: Texte du questionnaire
            
        Returns:
            Dict: Données structurées extraites du questionnaire
        """
        prompt = self._create_questionnaire_prompt(text)
        
        try:
            response = self._call_gpt_api(prompt)
            parsed_data = self._process_gpt_response(response)
            
            # Ajouter des scores de confiance
            confidence_scores = self._calculate_confidence_scores(parsed_data)
            
            return {
                "extracted_data": parsed_data,
                "confidence_scores": confidence_scores
            }
        except Exception as e:
            logger.error(f"Erreur lors du parsing du questionnaire avec GPT: {e}")
            return {"extracted_data": {}, "confidence_scores": {}}
    
    def extract_work_preferences(self, cv_text: str) -> Dict[str, Any]:
        """
        Extrait les préférences de travail d'un candidat à partir de son CV.
        
        Args:
            cv_text: Texte du CV
            
        Returns:
            Dict: Préférences de travail extraites
        """
        prompt = self._create_preferences_prompt(cv_text)
        
        try:
            response = self._call_gpt_api(prompt)
            preferences = self._process_gpt_response(response)
            
            # Calculer des scores de confiance
            confidence_scores = {
                "environment_preferences": 0.85,  # GPT est généralement bon pour ce type d'analyse
                "work_style_preferences": 0.80
            }
            
            return {
                "environment_preferences": preferences.get("environment_preferences", {}),
                "work_style_preferences": preferences.get("work_style_preferences", {}),
                "confidence_scores": confidence_scores
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des préférences avec GPT: {e}")
            return {
                "environment_preferences": {},
                "work_style_preferences": {},
                "confidence_scores": {"environment_preferences": 0, "work_style_preferences": 0}
            }
    
    def _call_gpt_api(self, prompt: str) -> str:
        """
        Appelle l'API GPT avec un prompt donné.
        
        Args:
            prompt: Texte du prompt
            
        Returns:
            str: Réponse de l'API
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant spécialisé dans l'analyse de texte et l'extraction d'informations structurées. Tu dois extraire les informations demandées et les formater en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Réduire la température pour des réponses plus précises et cohérentes
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API GPT: {e}")
            raise
    
    def _process_gpt_response(self, response: str) -> Dict[str, Any]:
        """
        Traite la réponse de GPT pour extraire les données JSON.
        
        Args:
            response: Texte de la réponse de GPT
            
        Returns:
            Dict: Données structurées
        """
        try:
            # Extraction du JSON si la réponse contient d'autres éléments
            json_pattern = r'```json\n(.*?)\n```'
            import re
            
            # Chercher un pattern de bloc de code JSON
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                # Sinon, essayer de trouver des accolades JSON
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                else:
                    # Si aucun JSON n'est trouvé, logger une erreur et retourner un dict vide
                    logger.error(f"Aucun JSON trouvé dans la réponse GPT: {response}")
                    return {}
            
            # Parser le JSON
            parsed_data = json.loads(json_str)
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing de la réponse JSON de GPT: {e}\nRéponse: {response}")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la réponse GPT: {e}")
            return {}
    
    def _calculate_confidence_scores(self, parsed_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule des scores de confiance pour les données extraites.
        
        Args:
            parsed_data: Données extraites
            
        Returns:
            Dict: Scores de confiance par section
        """
        confidence_scores = {}
        
        # Logique de base pour attribuer des scores de confiance
        for key in parsed_data:
            if isinstance(parsed_data[key], dict) and parsed_data[key]:
                confidence_scores[key] = 0.9  # Haute confiance pour les sections détaillées
            elif isinstance(parsed_data[key], list) and parsed_data[key]:
                confidence_scores[key] = 0.85  # Confiance légèrement plus basse pour les listes
            elif parsed_data[key]:
                confidence_scores[key] = 0.8   # Confiance standard pour les champs simples
            else:
                confidence_scores[key] = 0.0   # Aucune confiance pour les champs vides
        
        return confidence_scores
    
    def _create_cv_prompt(self, text: str) -> str:
        """
        Crée un prompt pour l'analyse d'un CV.
        
        Args:
            text: Texte du CV
            
        Returns:
            str: Prompt formaté
        """
        return f"""Analyse ce CV et extrait les informations suivantes dans un format JSON structuré:

1. Informations personnelles (nom, prénom, email, téléphone, adresse, etc.)
2. Formation et éducation (diplômes, établissements, années, etc.)
3. Expériences professionnelles (entreprises, postes, durées, responsabilités, etc.)
4. Compétences techniques (langages, outils, technologies, etc.)
5. Compétences linguistiques (langues et niveaux)
6. Certifications et formations complémentaires
7. Intérêts et loisirs

Retourne uniquement un objet JSON sans commentaires additionnels. Si une information n'est pas présente, mets une valeur vide.

Voici le CV à analyser:
{text}"""
    
    def _create_job_prompt(self, text: str) -> str:
        """
        Crée un prompt pour l'analyse d'une offre d'emploi.
        
        Args:
            text: Texte de l'offre d'emploi
            
        Returns:
            str: Prompt formaté
        """
        return f"""Analyse cette offre d'emploi et extrait les informations suivantes dans un format JSON structuré:

1. Titre du poste
2. Entreprise
3. Localisation (ville, pays)
4. Type de contrat (CDI, CDD, freelance, etc.)
5. Mode de travail (sur site, télétravail, hybride)
6. Salaire ou fourchette de rémunération
7. Compétences requises (techniques et soft skills)
8. Expérience requise (en années ou niveau)
9. Formation requise (diplômes, certifications)
10. Responsabilités principales du poste
11. Avantages proposés
12. Date de publication ou deadline de candidature

Retourne uniquement un objet JSON sans commentaires additionnels. Si une information n'est pas présente, mets une valeur vide.

Voici l'offre d'emploi à analyser:
{text}"""
    
    def _create_questionnaire_prompt(self, text: str) -> str:
        """
        Crée un prompt pour l'analyse d'un questionnaire d'entreprise.
        
        Args:
            text: Texte du questionnaire
            
        Returns:
            str: Prompt formaté
        """
        return f"""Analyse ce questionnaire d'entreprise et extrait les informations suivantes dans un format JSON structuré:

1. Questions posées (liste des questions)
2. Thèmes abordés (catégorisation des questions)
3. Type de réponses attendues (choix multiples, texte libre, échelle, etc.)
4. Objectifs apparents du questionnaire
5. Informations sur l'entreprise mentionnées

Retourne uniquement un objet JSON sans commentaires additionnels. Si une information n'est pas présente, mets une valeur vide.

Voici le questionnaire à analyser:
{text}"""
    
    def _create_preferences_prompt(self, text: str) -> str:
        """
        Crée un prompt pour l'extraction des préférences de travail.
        
        Args:
            text: Texte du CV
            
        Returns:
            str: Prompt formaté
        """
        return f"""Analyse ce CV et déduis les préférences d'environnement de travail et de style de travail du candidat. 
Retourne les résultats au format JSON structuré avec les clés suivantes:

1. environment_preferences:
   - remote_work: Préférence pour le télétravail (0-10)
   - startup_environment: Affinité pour l'environnement startup (0-10)
   - corporate_environment: Affinité pour l'environnement corporate (0-10)
   - international_environment: Affinité pour l'environnement international (0-10)
   - preferred_company_size: Taille d'entreprise préférée ("small", "medium", "large")
   - travel_willingness: Disposition à voyager (0-10)
   
2. work_style_preferences:
   - team_orientation: Préférence pour le travail en équipe vs individuel (0-10, 10=très orienté équipe)
   - leadership_orientation: Orientation vers le leadership (0-10)
   - autonomy_preference: Préférence pour l'autonomie (0-10)
   - innovation_orientation: Orientation vers l'innovation (0-10)
   - work_life_balance: Importance accordée à l'équilibre vie pro/perso (0-10)

Infère ces préférences à partir d'indices dans le CV comme les expériences passées, les intérêts, les réalisations, etc.
Retourne uniquement un objet JSON sans commentaires additionnels.

Voici le CV à analyser:
{text}"""


# Fonctions d'interface pour utilisation dans enhanced_parsing_system.py

def parse_document_with_gpt(text: str, doc_type: str) -> Dict[str, Any]:
    """
    Parse un document avec GPT selon son type.
    
    Args:
        text: Texte du document
        doc_type: Type de document ('cv', 'job_posting', 'company_questionnaire')
        
    Returns:
        Dict: Données extraites
    """
    parser = GPTParser()
    
    if doc_type == "cv":
        return parser.parse_cv(text)
    elif doc_type == "job_posting":
        return parser.parse_job_posting(text)
    elif doc_type == "company_questionnaire":
        return parser.parse_company_questionnaire(text)
    else:
        logger.warning(f"Type de document non pris en charge par GPTParser: {doc_type}")
        return {"extracted_data": {}, "confidence_scores": {}}

def extract_work_preferences_with_gpt(cv_text: str) -> Dict[str, Any]:
    """
    Extrait les préférences de travail d'un CV avec GPT.
    
    Args:
        cv_text: Texte du CV
        
    Returns:
        Dict: Préférences extraites
    """
    parser = GPTParser()
    return parser.extract_work_preferences(cv_text)
