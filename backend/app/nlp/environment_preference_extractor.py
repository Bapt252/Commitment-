"""
Module pour extraire les préférences d'environnement et de mode de travail
des candidats à partir des CV et d'indices indirects.
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import os
import json
from pathlib import Path

# Importer les composants nécessaires
from app.nlp.advanced_nlp import BERTExtractor, has_advanced_nlp_capabilities

# Configuration du logging
logger = logging.getLogger(__name__)

class WorkPreferenceExtractor:
    """
    Classe qui extrait les préférences de travail et d'environnement
    à partir des CV et d'autres sources de données.
    """
    
    def __init__(self):
        """
        Initialise l'extracteur de préférences.
        """
        # Initialiser l'extracteur BERT si disponible
        self.has_bert = has_advanced_nlp_capabilities()
        if self.has_bert:
            self.bert_extractor = BERTExtractor()
            logger.info("Extracteur de préférences initialisé avec capacités BERT.")
        else:
            self.bert_extractor = None
            logger.info("Extracteur de préférences initialisé avec méthodes traditionnelles uniquement.")
        
        # Charger les taxonomies et patterns
        self.load_patterns()
    
    def load_patterns(self):
        """
        Charge les patterns et taxonomies pour l'extraction de préférences.
        """
        # Patterns pour les préférences d'environnement de travail
        self.environment_patterns = {
            "remote": [
                r'\btélétravail\b', r'\bremote\b', r'\bdistance\b', r'\bhome\s*office\b',
                r'\bdistanciel\b', r'\btravail\s*à\s*domicile\b'
            ],
            "office": [
                r'\bbureau\b', r'\bprésentiel\b', r'\bopen\s*space\b', r'\blocaux\b',
                r'\bprésentielle\b', r'\bsite\b', r'\bentreprise\b'
            ],
            "hybrid": [
                r'\bhybride\b', r'\bmixte\b', r'\bflexible\b', r'\bcombinai[ts]on\b',
                r'\balternance domicile bureau\b', r'\bhibrid\b'
            ],
            "startup": [
                r'\bstartup\b', r'\bjeune\s*pousse\b', r'\bentrepreneurial\b', r'\binnovation\b',
                r'\bagile\b', r'\brapide\b', r'\bamorçage\b', r'\bscale\s*-?\s*up\b'
            ],
            "large_company": [
                r'\bgrande\s*entreprise\b', r'\bmultinationale\b', r'\bgroupe\b', r'\bcorporate\b',
                r'\betablie\b', r'\bstructure\b', r'\bCAC\s*40\b', r'\bgrande\s*société\b'
            ],
            "international": [
                r'\binternational\b', r'\bmondial\b', r'\bglobal\b', r'\bétranger\b',
                r'\bmulticulturel\b', r'\bmulti\s*-?\s*pays\b', r'\bcross\s*-?\s*cultural\b'
            ]
        }
        
        # Patterns pour les préférences de mode de travail
        self.work_style_patterns = {
            "autonomy": [
                r'\bautonom[ei]\b', r'\bindépendan[ct]e?\b', r'\binitiative\b',
                r'\bresponsabilité\b', r'\blibre\b', r'\bdécision\b'
            ],
            "team_work": [
                r'\béquipe\b', r'\bcollaborat(i[fov]n?|eur)\b', r'\bcollecti[fv]\b',
                r'\btravail\s*d\'équipe\b', r'\ben\s*groupe\b', r'\bpartage\b'
            ],
            "structured": [
                r'\bstructur[eé]\b', r'\bméthodique\b', r'\borgani[sz][eé]\b',
                r'\brigoureux\b', r'\bprécis\b', r'\bcadr[eé]\b', r'\bprocess\b'
            ],
            "flexible": [
                r'\bflexible\b', r'\badaptable\b', r'\badaptabilité\b', r'\bpolyvalent\b',
                r'\bagile\b', r'\bchangement\b', r'\bévolution\b'
            ],
            "creative": [
                r'\bcréati[fv]\b', r'\binnov[ae]nt\b', r'\boriginal\b',
                r'\bidées\b', r'\bconception\b', r'\bdesign\b', r'\bmysterieux\b'
            ],
            "analytical": [
                r'\banalytique\b', r'\banalyse\b', r'\blogique\b', r'\bdata\b',
                r'\brésolution\s*de\s*problèmes\b', r'\brationnell?e?\b'
            ]
        }
        
        # Indices indirects basés sur l'expérience passée
        self.indirect_clues = {
            # Types d'entreprises qui suggèrent des préférences
            "startup_companies": [
                "startup", "tech", "digital", "innovation", "disrupt", 
                "scale-up", "incub", "lab", "acceler"
            ],
            "large_companies": [
                "group", "corp", "inc", "sa", "international", "multinational",
                "leader", "mondial"
            ],
            
            # Rôles qui suggèrent des préférences
            "autonomous_roles": [
                "freelance", "consultant", "indépendant", "entrepreneur", 
                "auto-entrepreneur", "fondateur", "gérant"
            ],
            "team_roles": [
                "chef d'équipe", "team lead", "scrum master", "chef de projet",
                "responsable", "manager", "coordinateur"
            ]
        }
        
        # Mots-clés positifs et négatifs pour l'analyse de sentiment des préférences
        self.sentiment_keywords = {
            "positive": [
                "aime", "préfère", "intéressé", "passionné", "motivé", "enthousiaste",
                "apprécié", "valorisé", "expérience enrichissante", "satisfaction"
            ],
            "negative": [
                "n'aime pas", "éviter", "difficile", "contrainte", "imposé", "pénible",
                "frustrant", "déception", "burnout", "stress", "épuisement"
            ]
        }
        
        # Tentative de chargement des taxonomies personnalisées si disponibles
        try:
            taxonomies_path = Path(__file__).resolve().parent.parent.parent / "data"
            preferences_taxonomy_path = taxonomies_path / "work_preferences_taxonomy.json"
            
            if preferences_taxonomy_path.exists():
                with open(preferences_taxonomy_path, 'r', encoding='utf-8') as f:
                    loaded_patterns = json.load(f)
                    
                    # Mise à jour des patterns avec ceux personnalisés
                    if "environment_patterns" in loaded_patterns:
                        self.environment_patterns.update(loaded_patterns["environment_patterns"])
                    
                    if "work_style_patterns" in loaded_patterns:
                        self.work_style_patterns.update(loaded_patterns["work_style_patterns"])
                    
                    if "indirect_clues" in loaded_patterns:
                        self.indirect_clues.update(loaded_patterns["indirect_clues"])
                    
                    logger.info("Taxonomie de préférences de travail personnalisée chargée.")
        except Exception as e:
            logger.warning(f"Impossible de charger la taxonomie personnalisée: {e}")
    
    def extract_preferences_from_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Extrait les préférences d'environnement et de mode de travail du CV.
        
        Args:
            cv_text: Texte du CV
            
        Returns:
            Dict: Préférences extraites avec scores de confiance
        """
        # Initialiser le résultat
        preferences = {
            "environment_preferences": {},
            "work_style_preferences": {},
            "confidence_scores": {}
        }
        
        # 1. Tentative d'extraction avec BERT si disponible (haute précision)
        if self.has_bert and self.bert_extractor:
            try:
                # Extraction des préférences d'environnement
                env_prefs = self.bert_extractor.infer_work_environment_preferences(cv_text)
                preferences["environment_preferences"] = env_prefs
                preferences["confidence_scores"]["environment"] = 0.8  # Score plus élevé car BERT est plus précis
                
                # Extraction des préférences de mode de travail
                style_prefs = self.bert_extractor.infer_work_style_preferences(cv_text)
                preferences["work_style_preferences"] = style_prefs
                preferences["confidence_scores"]["work_style"] = 0.8
                
                logger.info("Préférences extraites avec BERT avec succès.")
                return preferences
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction BERT: {e}")
                # Continuer avec les méthodes traditionnelles en cas d'échec
        
        # 2. Extraction basée sur des règles et patterns (repli)
        try:
            # Extraction des préférences d'environnement
            env_prefs, env_confidence = self._extract_environment_preferences_rule_based(cv_text)
            preferences["environment_preferences"] = env_prefs
            preferences["confidence_scores"]["environment"] = env_confidence
            
            # Extraction des préférences de mode de travail
            style_prefs, style_confidence = self._extract_work_style_preferences_rule_based(cv_text)
            preferences["work_style_preferences"] = style_prefs
            preferences["confidence_scores"]["work_style"] = style_confidence
            
            logger.info("Préférences extraites avec méthodes basées sur les règles.")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction basée sur les règles: {e}")
            preferences["confidence_scores"]["environment"] = 0.3
            preferences["confidence_scores"]["work_style"] = 0.3
        
        return preferences
    
    def _extract_environment_preferences_rule_based(self, text: str) -> Tuple[Dict[str, float], float]:
        """
        Extrait les préférences d'environnement avec des méthodes basées sur les règles.
        
        Args:
            text: Texte du CV
            
        Returns:
            Tuple: (préférences d'environnement, score de confiance)
        """
        # Initialiser les préférences
        preferences = {
            "remote": 0.0,
            "office": 0.0,
            "hybrid": 0.0,
            "startup": 0.0,
            "large_company": 0.0,
            "international": 0.0
        }
        
        # Réduire le texte en minuscules pour les correspondances
        text_lower = text.lower()
        
        # 1. Chercher des mentions explicites de préférences
        explicit_preference_patterns = [
            (r'préf[èe]re\s*(\w+)', 1.0),
            (r'à la recherche\s*d[e\']\s*(\w+)', 0.8),
            (r'intéressé par\s*(\w+)', 0.7),
            (r'souhaite\s*(\w+)', 0.8),
            (r'idéalement[^\.]*(\w+)', 0.7)
        ]
        
        # Score pour les préférences explicites
        for pattern, weight in explicit_preference_patterns:
            for key, key_patterns in self.environment_patterns.items():
                for key_pattern in key_patterns:
                    # Chercher des motifs comme "préfère travailler en remote"
                    explicit_pattern = pattern.replace('(\w+)', key_pattern)
                    if re.search(explicit_pattern, text_lower):
                        preferences[key] += weight
        
        # 2. Chercher des mentions d'environnements précédents avec sentiment positif
        # Paragraphes contenant des sentiments positifs
        positive_paragraphs = []
        paragraphs = re.split(r'\n{2,}', text)
        
        for para in paragraphs:
            para_lower = para.lower()
            if any(pos_word in para_lower for pos_word in self.sentiment_keywords["positive"]):
                positive_paragraphs.append(para_lower)
        
        # Chercher des patterns d'environnement dans ces paragraphes
        for para in positive_paragraphs:
            for key, patterns in self.environment_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, para):
                        preferences[key] += 0.5
        
        # 3. Analyser les expériences pour déduire des préférences
        # Chercher des mentions d'entreprises qui correspondraient à des types particuliers
        for clue_type, clues in self.indirect_clues.items():
            if clue_type == "startup_companies":
                for clue in clues:
                    count = len(re.findall(r'\b' + re.escape(clue) + r'\w*\b', text_lower))
                    if count > 0:
                        preferences["startup"] += min(0.5, count * 0.1)
            elif clue_type == "large_companies":
                for clue in clues:
                    count = len(re.findall(r'\b' + re.escape(clue) + r'\w*\b', text_lower))
                    if count > 0:
                        preferences["large_company"] += min(0.5, count * 0.1)
            elif clue_type == "autonomous_roles":
                for clue in clues:
                    if re.search(r'\b' + re.escape(clue) + r'\w*\b', text_lower):
                        preferences["remote"] += 0.2
        
        # 4. Chercher des mots-clés généraux
        for key, patterns in self.environment_patterns.items():
            for pattern in patterns:
                count = len(re.findall(pattern, text_lower))
                preferences[key] += min(0.4, count * 0.1)
        
        # Normaliser les scores entre 0 et 1
        for key in preferences:
            preferences[key] = min(1.0, preferences[key])
        
        # Calcul du score de confiance global
        # Plus la somme des préférences est élevée, plus nous sommes confiants
        total_preference = sum(preferences.values())
        confidence = min(0.75, 0.3 + (total_preference / len(preferences)) * 0.3)
        
        return preferences, confidence
    
    def _extract_work_style_preferences_rule_based(self, text: str) -> Tuple[Dict[str, float], float]:
        """
        Extrait les préférences de mode de travail avec des méthodes basées sur les règles.
        
        Args:
            text: Texte du CV
            
        Returns:
            Tuple: (préférences de mode de travail, score de confiance)
        """
        # Initialiser les préférences
        preferences = {
            "autonomy": 0.0,
            "team_work": 0.0,
            "structured": 0.0,
            "flexible": 0.0,
            "creative": 0.0,
            "analytical": 0.0
        }
        
        # Réduire le texte en minuscules pour les correspondances
        text_lower = text.lower()
        
        # 1. Chercher des mentions explicites de préférences
        explicit_preference_patterns = [
            (r'préf[èe]re\s*(.*?)(dans|avec|en)', 1.0),
            (r'travaille bien\s*(.*?)(dans|avec|en)', 0.8),
            (r'aptitude[s]? [àa]\s*(.*?)[,\.]', 0.7),
            (r'capable de\s*(.*?)[,\.]', 0.6),
            (r'aime\s*(.*?)(travailler|collaborer)', 0.8)
        ]
        
        # Score pour les préférences explicites
        for pattern, weight in explicit_preference_patterns:
            for key, key_patterns in self.work_style_patterns.items():
                for key_pattern in key_patterns:
                    # Chercher des motifs comme "préfère travailler en autonomie"
                    explicit_pattern = pattern.replace('(.*?)', '.*?' + key_pattern + '.*?')
                    if re.search(explicit_pattern, text_lower):
                        preferences[key] += weight
        
        # 2. Analyser la section compétences/aptitudes personnelles
        # Trouver une section pertinente
        skill_section_patterns = [
            r'(?:compétences|aptitudes|qualités)\s*personnelles(?:\s*:|\s*\n)(.*?)(?:\n\n|\n\w{3,}|\Z)',
            r'(?:profil|personnalité|soft skills)(?:\s*:|\s*\n)(.*?)(?:\n\n|\n\w{3,}|\Z)',
            r'(?:à propos de moi|présentation|summary)(?:\s*:|\s*\n)(.*?)(?:\n\n|\n\w{3,}|\Z)'
        ]
        
        skill_section = ""
        for pattern in skill_section_patterns:
            match = re.search(pattern, text_lower, re.DOTALL)
            if match:
                skill_section = match.group(1)
                break
        
        # Analyser les compétences personnelles déclarées
        if skill_section:
            for key, patterns in self.work_style_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, skill_section):
                        preferences[key] += 0.7
        
        # 3. Déduire des indices des expériences professionnelles
        # Chercher des rôles qui suggèrent certaines préférences
        team_lead_patterns = [
            r'chef d\'équipe', r'team lead', r'manager', r'responsable',
            r'coordinat(eur|rice)', r'supervis(eur|ion)', r'encadrement'
        ]
        
        solo_work_patterns = [
            r'seul', r'indépendamment', r'en autonomie',
            r'chargé de', r'mission indépendante'
        ]
        
        # Compter les occurrences des patterns
        team_lead_count = sum(len(re.findall(pattern, text_lower)) for pattern in team_lead_patterns)
        solo_work_count = sum(len(re.findall(pattern, text_lower)) for pattern in solo_work_patterns)
        
        # Ajuster les scores en fonction des résultats
        if team_lead_count > 0:
            preferences["team_work"] += min(0.6, team_lead_count * 0.15)
        
        if solo_work_count > 0:
            preferences["autonomy"] += min(0.6, solo_work_count * 0.15)
        
        # 4. Chercher des mots-clés généraux dans tout le texte
        for key, patterns in self.work_style_patterns.items():
            for pattern in patterns:
                count = len(re.findall(pattern, text_lower))
                preferences[key] += min(0.4, count * 0.1)
        
        # Normaliser les scores entre 0 et 1
        for key in preferences:
            preferences[key] = min(1.0, preferences[key])
        
        # Équilibrage des scores pour les dimensions opposées
        pairs = [
            ("autonomy", "team_work"),
            ("structured", "flexible"),
            ("creative", "analytical")
        ]
        
        for key1, key2 in pairs:
            # Si les deux scores sont élevés, légèrement équilibrer
            total = preferences[key1] + preferences[key2]
            if total > 1.2:  # Seuil arbitraire pour "élevé"
                # Réduire proportionnellement pour garder leur ratio mais limiter leur somme
                scale = 1.2 / total
                preferences[key1] *= scale
                preferences[key2] *= scale
        
        # Calcul du score de confiance global
        total_preference = sum(preferences.values())
        confidence = min(0.7, 0.3 + (total_preference / len(preferences)) * 0.25)
        
        return preferences, confidence
    
    def enrich_cv_data(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données de CV avec les préférences extraites.
        
        Args:
            cv_data: Données de CV existantes
            
        Returns:
            Dict: Données enrichies avec préférences
        """
        # Vérifier qu'il y a du contenu à traiter
        if not cv_data or "extracted_data" not in cv_data:
            logger.warning("Données de CV invalides pour enrichissement.")
            return cv_data
        
        try:
            # Reconstruire le texte du CV si nécessaire
            cv_text = ""
            if "original_text" in cv_data:
                cv_text = cv_data["original_text"]
            else:
                # Tenter de reconstruire à partir des données extraites
                extracted = cv_data["extracted_data"]
                
                # Ajouter les informations personnelles
                if "nom" in extracted:
                    cv_text += extracted["nom"] + "\n\n"
                
                if "titre" in extracted:
                    cv_text += extracted["titre"] + "\n\n"
                
                # Ajouter l'expérience
                if "experience" in extracted and isinstance(extracted["experience"], list):
                    cv_text += "EXPÉRIENCE\n"
                    for exp in extracted["experience"]:
                        cv_text += f"{exp.get('period', '')}: {exp.get('title', '')}\n"
                        if "description" in exp:
                            cv_text += exp["description"] + "\n"
                    cv_text += "\n"
                
                # Ajouter la formation
                if "formation" in extracted and isinstance(extracted["formation"], list):
                    cv_text += "FORMATION\n"
                    for edu in extracted["formation"]:
                        if isinstance(edu, dict):
                            cv_text += f"{edu.get('period', '')}: {edu.get('degree', '')}\n"
                    cv_text += "\n"
                
                # Ajouter les compétences
                if "competences" in extracted:
                    cv_text += "COMPÉTENCES\n"
                    if isinstance(extracted["competences"], list):
                        cv_text += "\n".join(extracted["competences"]) + "\n\n"
                    else:
                        cv_text += str(extracted["competences"]) + "\n\n"
            
            # Si texte disponible, extraire les préférences
            if cv_text:
                preferences = self.extract_preferences_from_cv(cv_text)
                
                # Ajouter les préférences aux données extraites
                if "extracted_data" not in cv_data:
                    cv_data["extracted_data"] = {}
                
                cv_data["extracted_data"]["preferences"] = {
                    "environment": preferences["environment_preferences"],
                    "work_style": preferences["work_style_preferences"]
                }
                
                # Ajouter les scores de confiance
                if "confidence_scores" not in cv_data:
                    cv_data["confidence_scores"] = {}
                
                cv_data["confidence_scores"]["preferences"] = preferences["confidence_scores"]
                
                logger.info("CV enrichi avec succès avec les préférences.")
            else:
                logger.warning("Impossible d'extraire le texte du CV pour enrichissement.")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement du CV: {e}")
        
        return cv_data


# Fonctions d'interface pour utilisation dans d'autres modules
def extract_work_preferences(cv_text: str) -> Dict[str, Any]:
    """
    Extrait les préférences de travail d'un CV.
    
    Args:
        cv_text: Texte du CV
        
    Returns:
        Dict: Préférences extraites
    """
    extractor = WorkPreferenceExtractor()
    return extractor.extract_preferences_from_cv(cv_text)

def enrich_cv_with_preferences(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrichit les données de CV avec les préférences extraites.
    
    Args:
        cv_data: Données de CV
        
    Returns:
        Dict: Données enrichies
    """
    extractor = WorkPreferenceExtractor()
    return extractor.enrich_cv_data(cv_data)