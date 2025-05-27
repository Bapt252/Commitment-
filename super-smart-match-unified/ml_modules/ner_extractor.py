"""
Extracteur NER pour SuperSmartMatch Unifié
Module optionnel pour l'extraction d'entités nommées
"""

import logging
import re
from typing import List, Dict, Set
try:
    import spacy
    from spacy.matcher import Matcher
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class NERExtractor:
    """
    Extracteur d'entités nommées spécialisé pour les compétences
    et informations RH
    """
    
    def __init__(self, model_name: str = "fr_core_news_sm"):
        if not NLP_AVAILABLE:
            raise ImportError("Dépendances NLP non disponibles. Installez : spacy")
        
        self.model_name = model_name
        self.nlp = None
        self.matcher = None
        self.skills_patterns = self._get_skills_patterns()
        self._load_model()
    
    def _load_model(self):
        """Chargement du modèle spaCy"""
        try:
            logger.info(f"Chargement du modèle NLP: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
            self._setup_matcher()
            logger.info("Modèle NLP chargé avec succès")
        except OSError:
            logger.warning(f"Modèle {self.model_name} non trouvé, utilisation de modèles alternatifs")
            try:
                # Essayer des modèles alternatifs
                for alt_model in ["fr_core_news_md", "en_core_web_sm", "xx_ent_wiki_sm"]:
                    try:
                        self.nlp = spacy.load(alt_model)
                        self.model_name = alt_model
                        self._setup_matcher()
                        logger.info(f"Modèle alternatif {alt_model} chargé")
                        break
                    except OSError:
                        continue
                else:
                    # Utilisation du modèle vide en dernier recours
                    self.nlp = spacy.blank("fr")
                    self._setup_matcher()
                    logger.warning("Utilisation du modèle vide, fonctionnalités limitées")
            except Exception as e:
                logger.error(f"Erreur chargement modèle NLP: {e}")
                raise
    
    def _setup_matcher(self):
        """Configuration du matcher pour les patterns de compétences"""
        if not self.nlp:
            return
            
        self.matcher = Matcher(self.nlp.vocab)
        
        # Ajout des patterns de compétences
        for skill_type, patterns in self.skills_patterns.items():
            for i, pattern in enumerate(patterns):
                pattern_name = f"{skill_type}_{i}"
                self.matcher.add(pattern_name, [pattern])
    
    def _get_skills_patterns(self) -> Dict[str, List[List[Dict]]]:
        """Patterns pour identifier les compétences"""
        return {
            "programming_languages": [
                [{"LOWER": {"IN": ["python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust", "scala"]}}],
                [{"LOWER": "typescript"}],
                [{"LOWER": "node"}, {"LOWER": "js", "OP": "?"}],
                [{"LOWER": "react"}, {"LOWER": {"IN": ["js", "native"]}, "OP": "?"}],
                [{"LOWER": "vue"}, {"LOWER": "js", "OP": "?"}],
                [{"LOWER": "angular"}]
            ],
            "databases": [
                [{"LOWER": {"IN": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite"]}}],
                [{"LOWER": "sql"}, {"LOWER": "server", "OP": "?"}],
                [{"LOWER": "oracle"}, {"LOWER": "db", "OP": "?"}]
            ],
            "frameworks": [
                [{"LOWER": {"IN": ["django", "flask", "fastapi", "spring", "express", "laravel"]}}],
                [{"LOWER": "nest"}, {"LOWER": "js", "OP": "?"}],
                [{"LOWER": ".net"}, {"LOWER": {"IN": ["core", "framework"]}, "OP": "?"}]
            ],
            "tools": [
                [{"LOWER": {"IN": ["docker", "kubernetes", "jenkins", "gitlab", "github", "jira", "confluence"]}}],
                [{"LOWER": "git"}, {"LOWER": {"IN": ["hub", "lab"]}, "OP": "?"}],
                [{"LOWER": "vs"}, {"LOWER": "code"}],
                [{"LOWER": "visual"}, {"LOWER": "studio"}]
            ],
            "cloud_platforms": [
                [{"LOWER": {"IN": ["aws", "azure", "gcp", "heroku", "digitalocean"]}}],
                [{"LOWER": "amazon"}, {"LOWER": "web"}, {"LOWER": "services"}],
                [{"LOWER": "google"}, {"LOWER": "cloud"}, {"LOWER": "platform", "OP": "?"}],
                [{"LOWER": "microsoft"}, {"LOWER": "azure"}]
            ],
            "methodologies": [
                [{"LOWER": {"IN": ["agile", "scrum", "kanban", "devops", "ci/cd", "tdd", "bdd"]}}],
                [{"LOWER": "test"}, {"LOWER": "driven"}, {"LOWER": "development"}],
                [{"LOWER": "behavior"}, {"LOWER": "driven"}, {"LOWER": "development"}]
            ],
            "soft_skills": [
                [{"LOWER": {"IN": ["leadership", "communication", "teamwork", "management", "organization"]}}],
                [{"LOWER": "problem"}, {"LOWER": "solving"}],
                [{"LOWER": "project"}, {"LOWER": "management"}],
                [{"LOWER": "time"}, {"LOWER": "management"}]
            ]
        }
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extrait les compétences d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste des compétences identifiées
        """
        if not self.nlp or not text:
            return []
        
        try:
            # Nettoyage du texte
            cleaned_text = self._clean_text(text)
            
            # Traitement avec spaCy
            doc = self.nlp(cleaned_text)
            
            extracted_skills = set()
            
            # Extraction via matcher de patterns
            if self.matcher:
                matches = self.matcher(doc)
                for match_id, start, end in matches:
                    skill = doc[start:end].text.strip()
                    if skill:
                        extracted_skills.add(skill.lower())
            
            # Extraction via entités nommées
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT", "TECH"]:
                    # Filtrer pour ne garder que les compétences techniques plausibles
                    if self._is_likely_skill(ent.text):
                        extracted_skills.add(ent.text.lower())
            
            # Extraction via patterns regex
            regex_skills = self._extract_with_regex(text)
            extracted_skills.update(regex_skills)
            
            return list(extracted_skills)
            
        except Exception as e:
            logger.error(f"Erreur extraction compétences: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Nettoyage du texte pour améliorer l'extraction"""
        # Supprimer les caractères spéciaux excessifs
        text = re.sub(r'[^\w\s\-\.\+\#]', ' ', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _is_likely_skill(self, text: str) -> bool:
        """Détermine si un texte est probablement une compétence"""
        text_lower = text.lower()
        
        # Mots-clés indicateurs de compétences
        skill_indicators = [
            "programming", "development", "framework", "library", "database",
            "language", "tool", "platform", "technology", "skill", "certification"
        ]
        
        # Longueur raisonnable
        if len(text) < 2 or len(text) > 50:
            return False
        
        # Éviter les mots trop génériques
        generic_words = ["company", "university", "school", "project", "team", "work"]
        if text_lower in generic_words:
            return False
        
        return True
    
    def _extract_with_regex(self, text: str) -> Set[str]:
        """Extraction complémentaire avec expressions régulières"""
        skills = set()
        
        # Patterns spécifiques
        patterns = {
            # Versions de technologies
            r'\b(python|java|node\.?js|react|vue|angular)\s*(?:v?\d+(?:\.\d+)*)\b': lambda m: m.group(1).lower(),
            
            # Certifications
            r'\b(aws|azure|gcp|google)\s+(certified|certification)\b': lambda m: f"{m.group(1).lower()} certification",
            
            # Technologies avec préfixes
            r'\b(micro)?services?\b': lambda m: "microservices" if m.group(1) else "services",
            
            # APIs et protocoles
            r'\b(rest|soap|graphql|api)\b': lambda m: m.group(1).lower(),
            
            # Bases de données
            r'\b(no)?sql\b': lambda m: "nosql" if m.group(1) else "sql",
        }
        
        for pattern, extractor in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    skill = extractor(match)
                    if skill:
                        skills.add(skill)
                except Exception:
                    continue
        
        return skills
    
    def extract_experience_duration(self, text: str) -> Dict[str, int]:
        """
        Extrait les durées d'expérience du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec les durées trouvées
        """
        experience_info = {
            "total_years": 0,
            "details": []
        }
        
        # Patterns pour détecter l'expérience
        patterns = [
            r'(\d+)\s+(?:ans?|années?)\s+(?:d\')?(?:expérience|exp)',
            r'(?:expérience|exp)\s+(?:de\s+)?(\d+)\s+(?:ans?|années?)',
            r'(\d+)\s*(?:-|à)\s*(\d+)\s+(?:ans?|années?)\s+(?:d\')?(?:expérience|exp)',
            r'depuis\s+(\d+)\s+(?:ans?|années?)',
            r'(\d+)\s+(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 1:
                        years = int(match.group(1))
                        experience_info["details"].append({
                            "years": years,
                            "context": match.group(0)
                        })
                        experience_info["total_years"] = max(experience_info["total_years"], years)
                    elif len(match.groups()) == 2:
                        # Plage d'années
                        min_years = int(match.group(1))
                        max_years = int(match.group(2))
                        avg_years = (min_years + max_years) // 2
                        experience_info["details"].append({
                            "years": avg_years,
                            "range": [min_years, max_years],
                            "context": match.group(0)
                        })
                        experience_info["total_years"] = max(experience_info["total_years"], avg_years)
                except (ValueError, IndexError):
                    continue
        
        return experience_info
    
    def extract_education_level(self, text: str) -> Dict[str, any]:
        """
        Extrait le niveau d'éducation du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Informations sur le niveau d'éducation
        """
        education_levels = {
            "bac": 1,
            "bac+2": 2, "dut": 2, "bts": 2,
            "bac+3": 3, "licence": 3, "bachelor": 3,
            "bac+4": 4, "maîtrise": 4, "master 1": 4, "m1": 4,
            "bac+5": 5, "master": 5, "master 2": 5, "m2": 5, "msc": 5,
            "bac+6": 6, "mastère": 6,
            "bac+8": 8, "doctorat": 8, "phd": 8, "thèse": 8
        }
        
        found_levels = []
        max_level = 0
        
        text_lower = text.lower()
        
        for education, level in education_levels.items():
            if education in text_lower:
                found_levels.append({
                    "degree": education,
                    "level": level
                })
                max_level = max(max_level, level)
        
        return {
            "max_level": max_level,
            "found_degrees": found_levels,
            "level_description": self._get_level_description(max_level)
        }
    
    def _get_level_description(self, level: int) -> str:
        """Description du niveau d'éducation"""
        descriptions = {
            0: "Non spécifié",
            1: "Baccalauréat",
            2: "Bac+2 (DUT/BTS)",
            3: "Bac+3 (Licence/Bachelor)",
            4: "Bac+4 (Maîtrise/Master 1)",
            5: "Bac+5 (Master/Ingénieur)",
            6: "Bac+6 (Mastère spécialisé)",
            8: "Bac+8 (Doctorat/PhD)"
        }
        return descriptions.get(level, f"Bac+{level}")
    
    def analyze_text_comprehensive(self, text: str) -> Dict:
        """
        Analyse complète d'un texte (CV ou fiche de poste)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Analyse complète avec compétences, expérience, formation
        """
        try:
            return {
                "skills": self.extract_skills_from_text(text),
                "experience": self.extract_experience_duration(text),
                "education": self.extract_education_level(text),
                "text_length": len(text),
                "processing_success": True
            }
        except Exception as e:
            logger.error(f"Erreur analyse complète: {e}")
            return {
                "skills": [],
                "experience": {"total_years": 0, "details": []},
                "education": {"max_level": 0, "found_degrees": []},
                "error": str(e),
                "processing_success": False
            }
    
    def get_model_info(self) -> Dict:
        """Informations sur le modèle NLP chargé"""
        return {
            "model_name": self.model_name,
            "model_loaded": self.nlp is not None,
            "nlp_available": NLP_AVAILABLE,
            "matcher_patterns": len(self.matcher) if self.matcher else 0,
            "supported_languages": ["fr", "en"] if self.nlp else []
        }
