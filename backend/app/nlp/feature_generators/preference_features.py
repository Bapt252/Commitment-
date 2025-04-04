"""
Générateur de features basées sur les préférences professionnelles.
"""

import logging
import re
from pathlib import Path
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PreferenceFeatureGenerator:
    """
    Générateur de features pour les préférences professionnelles et les attentes.
    """
    
    def __init__(self):
        """
        Initialise le générateur de features de préférences.
        """
        self.logger = logging.getLogger(__name__)
        
        # Cartographie des types de contrats
        self.contract_types = {
            "cdi": ["cdi", "contrat à durée indéterminée", "permanent", "unlimited", "long-term"],
            "cdd": ["cdd", "contrat à durée déterminée", "temporary", "fixed-term", "short-term"],
            "interim": ["interim", "intérim", "temp", "temporary work", "mission"],
            "freelance": ["freelance", "independent", "contractor", "self-employed", "consultant"],
            "alternance": ["alternance", "apprenticeship", "apprentissage", "work-study", "dual training"],
            "stage": ["stage", "internship", "trainee", "training"]
        }
        
        # Cartographie des modes de travail
        self.work_modes = {
            "remote": ["remote", "télétravail", "teletravail", "à distance", "remote work", "work from home", "home-based"],
            "onsite": ["onsite", "on-site", "présentiel", "presentiel", "on site", "office", "bureau"],
            "hybrid": ["hybrid", "hybride", "mixed", "mixte", "partial remote", "flexible", "remote and office"]
        }
        
        # Cartographie des tailles d'entreprise
        self.company_sizes = {
            "startup": ["startup", "start-up", "small company", "petite entreprise", "early-stage", "<10", "<20"],
            "sme": ["sme", "pme", "medium", "moyenne entreprise", "mid-size", "growing", "<250", "<500"],
            "large": ["large", "grande entreprise", "big company", "entreprise importante", "corporate", ">500", ">1000"],
            "multinational": ["multinational", "international", "global", "worldwide", "group", "groupe", "enterprise"]
        }
        
        # Cartographie des types d'industries
        self.industry_types = self._load_industry_types()
    
    def _load_industry_types(self):
        """
        Charge la taxonomie des secteurs d'activité.
        
        Returns:
            Dict: Taxonomie des secteurs
        """
        # Structure de base pour les industries
        default_industries = {
            "tech": ["technologie", "technology", "it", "informatique", "software", "logiciel", "digital", "numérique", "web", "internet"],
            "finance": ["finance", "banking", "banque", "investment", "investissement", "insurance", "assurance", "fintech"],
            "healthcare": ["healthcare", "santé", "médical", "medical", "pharmaceutical", "pharmaceutique", "biotech", "health", "hospital", "hôpital"],
            "retail": ["retail", "commerce", "retail", "vente", "e-commerce", "distribution", "magasin", "store", "consumer goods"],
            "manufacturing": ["manufacturing", "industrie", "production", "fabrication", "usine", "factory", "industrial"],
            "energy": ["energy", "énergie", "oil", "gas", "pétrole", "renewables", "renewable energy", "énergie renouvelable"],
            "education": ["education", "éducation", "teaching", "enseignement", "academic", "académique", "school", "université", "university"],
            "consulting": ["consulting", "conseil", "consultancy", "professional services", "services professionnels"],
            "media": ["media", "médias", "entertainment", "divertissement", "publishing", "édition", "news", "actualités"],
            "telecom": ["telecom", "télécommunications", "telecommunications", "network", "réseau"]
        }
        
        # Essayer de charger une taxonomie plus détaillée si disponible
        try:
            taxonomy_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "industry_sectors.json"
            if taxonomy_path.exists():
                with open(taxonomy_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Impossible de charger la taxonomie des secteurs: {e}")
        
        return default_industries
    
    def generate_preference_features(self, candidate_profile, job_profile):
        """
        Génère les features basées sur les préférences et attentes.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Features de préférences
        """
        features = {}
        
        # 1. Correspondance de localisation
        features["location_match"] = self.calculate_location_match(
            self._extract_preferred_location(candidate_profile),
            self._extract_job_location(job_profile)
        )
        
        # 2. Correspondance de type de contrat
        features["contract_type_match"] = self.calculate_contract_type_match(
            self._extract_preferred_contract(candidate_profile),
            self._extract_job_contract(job_profile)
        )
        
        # 3. Correspondance de mode de travail (remote/onsite/hybrid)
        features["work_mode_match"] = self.calculate_work_mode_match(
            self._extract_preferred_work_mode(candidate_profile),
            self._extract_job_work_mode(job_profile)
        )
        
        # 4. Correspondance de salaire
        features["salary_match"] = self.calculate_salary_match(
            self._extract_expected_salary(candidate_profile),
            self._extract_job_salary(job_profile)
        )
        
        # 5. Correspondance de taille d'entreprise
        features["company_size_match"] = self.calculate_company_size_match(
            self._extract_preferred_company_size(candidate_profile),
            self._extract_company_size(job_profile)
        )
        
        # 6. Correspondance d'industrie/secteur
        features["industry_match"] = self.calculate_industry_match(
            self._extract_preferred_industries(candidate_profile),
            self._extract_job_industry(job_profile)
        )
        
        # 7. Correspondance d'horaires de travail
        features["work_hours_match"] = self.calculate_work_hours_match(
            self._extract_preferred_work_hours(candidate_profile),
            self._extract_job_work_hours(job_profile)
        )
        
        # 8. Correspondance de durée de trajet
        features["commute_time_match"] = self.calculate_commute_time_match(
            self._extract_max_commute_time(candidate_profile),
            candidate_profile.get("address", ""),
            job_profile.get("location", "")
        )
        
        return features
    
    def _extract_preferred_location(self, candidate_profile):
        """
        Extrait la localisation préférée du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Localisation préférée
        """
        if not candidate_profile:
            return ""
        
        # Chemins possibles pour la localisation
        location_fields = [
            "preferred_location", "desired_location", "location_preference",
            "mobility.preferred_location", "work_preferences.location",
            "address", "location"
        ]
        
        for field in location_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, str) and current.strip():
                return current.strip()
        
        return ""
    
    def _extract_job_location(self, job_profile):
        """
        Extrait la localisation du poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Localisation du poste
        """
        if not job_profile:
            return ""
        
        # Chemins possibles pour la localisation
        location_fields = [
            "location", "job_location", "workplace", "address",
            "company_location", "office_location"
        ]
        
        for field in location_fields:
            if field in job_profile:
                value = job_profile[field]
                if isinstance(value, str) and value.strip():
                    return value.strip()
        
        return ""
    
    def calculate_location_match(self, candidate_location, job_location):
        """
        Calcule la correspondance entre la localisation préférée et celle du poste.
        
        Args:
            candidate_location: Localisation préférée du candidat
            job_location: Localisation du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_location or not job_location:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Normaliser les localisations
        candidate_location = candidate_location.lower()
        job_location = job_location.lower()
        
        # Correspondance exacte
        if candidate_location == job_location:
            return 1.0
        
        # Correspondance partielle (une ville contenue dans l'autre)
        if candidate_location in job_location or job_location in candidate_location:
            return 0.8
        
        # Extraction de la ville et du code postal/département
        candidate_city, candidate_region = self._extract_city_region(candidate_location)
        job_city, job_region = self._extract_city_region(job_location)
        
        # Correspondance de ville
        if candidate_city and job_city and (candidate_city == job_city):
            return 0.9
        
        # Correspondance de région/département
        if candidate_region and job_region and (candidate_region == job_region):
            return 0.7
        
        # Séparation des mots et recherche de chevauchement
        candidate_tokens = set(re.findall(r'\b\w+\b', candidate_location))
        job_tokens = set(re.findall(r'\b\w+\b', job_location))
        
        common_tokens = candidate_tokens.intersection(job_tokens)
        
        if common_tokens:
            # Calculer un score basé sur la proportion de mots communs
            similarity = len(common_tokens) / max(len(candidate_tokens), len(job_tokens))
            return max(0.3, similarity)  # Minimum 0.3 s'il y a au moins un mot commun
        
        # Aucune correspondance
        return 0.1
    
    def _extract_city_region(self, location):
        """
        Extrait la ville et la région/département d'une localisation.
        
        Args:
            location: Chaîne de localisation
            
        Returns:
            Tuple: (ville, région/département)
        """
        # Extraction de code postal français
        postal_match = re.search(r'\b\d{5}\b', location)
        postal_code = postal_match.group(0) if postal_match else None
        
        # Extraction de département français (à partir du code postal)
        department = postal_code[:2] if postal_code else None
        
        # Essayer d'extraire la ville (mot avant ou après le code postal, ou premier mot)
        city = None
        
        if postal_match:
            # Chercher le mot avant le code postal
            before_match = re.search(r'\b(\w+)\s+\d{5}\b', location)
            if before_match:
                city = before_match.group(1).lower()
            else:
                # Chercher le mot après le code postal
                after_match = re.search(r'\b\d{5}\s+(\w+)\b', location)
                if after_match:
                    city = after_match.group(1).lower()
        
        # Si aucune ville n'a été trouvée, prendre le premier "mot" (potentiellement la ville)
        if not city:
            words = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', location)
            if words:
                city = words[0].lower()
        
        return city, department
    
    def _extract_preferred_contract(self, candidate_profile):
        """
        Extrait le type de contrat préféré par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Type de contrat préféré
        """
        if not candidate_profile:
            return ""
        
        # Chemins possibles pour le type de contrat
        contract_fields = [
            "preferred_contract", "contract_preference", "desired_contract_type",
            "work_preferences.contract_type", "job_preferences.contract_type"
        ]
        
        for field in contract_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, str) and current.strip():
                return current.strip().lower()
        
        # Recherche dans d'autres champs textuels
        text_fields = ["about_me", "job_preferences", "work_preferences"]
        
        combined_text = ""
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                combined_text += " " + candidate_profile[field].lower()
        
        # Recherche des types de contrat dans le texte
        for contract_type, keywords in self.contract_types.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return contract_type
        
        return ""
    
    def _extract_job_contract(self, job_profile):
        """
        Extrait le type de contrat du poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Type de contrat
        """
        if not job_profile:
            return ""
        
        # Chemins possibles pour le type de contrat
        contract_fields = [
            "contract_type", "job_type", "employment_type", "type_de_contrat"
        ]
        
        for field in contract_fields:
            if field in job_profile:
                value = job_profile[field]
                if isinstance(value, str) and value.strip():
                    contract_value = value.strip().lower()
                    
                    # Correspondance directe avec un type connu
                    for contract_type, keywords in self.contract_types.items():
                        if any(keyword in contract_value for keyword in keywords):
                            return contract_type
                    
                    # Retourner la valeur telle quelle
                    return contract_value
        
        # Recherche dans la description ou d'autres champs
        text_fields = ["description", "job_description", "details"]
        
        combined_text = ""
        for field in text_fields:
            if field in job_profile and isinstance(job_profile[field], str):
                combined_text += " " + job_profile[field].lower()
        
        # Recherche des types de contrat dans le texte
        for contract_type, keywords in self.contract_types.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return contract_type
        
        return ""
    
    def calculate_contract_type_match(self, candidate_contract, job_contract):
        """
        Calcule la correspondance entre les types de contrat.
        
        Args:
            candidate_contract: Type de contrat préféré par le candidat
            job_contract: Type de contrat du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_contract or not job_contract:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Normaliser les types de contrat
        candidate_contract = candidate_contract.lower()
        job_contract = job_contract.lower()
        
        # Correspondance exacte
        if candidate_contract == job_contract:
            return 1.0
        
        # Matrice de compatibilité entre types de contrat
        compatibility = {
            "cdi": {"cdi": 1.0, "cdd": 0.7, "interim": 0.4, "freelance": 0.5, "alternance": 0.6, "stage": 0.3},
            "cdd": {"cdi": 0.8, "cdd": 1.0, "interim": 0.7, "freelance": 0.6, "alternance": 0.5, "stage": 0.4},
            "interim": {"cdi": 0.5, "cdd": 0.7, "interim": 1.0, "freelance": 0.8, "alternance": 0.3, "stage": 0.2},
            "freelance": {"cdi": 0.4, "cdd": 0.5, "interim": 0.7, "freelance": 1.0, "alternance": 0.2, "stage": 0.2},
            "alternance": {"cdi": 0.6, "cdd": 0.5, "interim": 0.3, "freelance": 0.2, "alternance": 1.0, "stage": 0.7},
            "stage": {"cdi": 0.3, "cdd": 0.4, "interim": 0.2, "freelance": 0.2, "alternance": 0.7, "stage": 1.0}
        }
        
        if candidate_contract in compatibility and job_contract in compatibility[candidate_contract]:
            return compatibility[candidate_contract][job_contract]
        
        # Correspondance partielle basée sur les mots-clés
        candidate_type = None
        job_type = None
        
        for contract_type, keywords in self.contract_types.items():
            for keyword in keywords:
                if keyword in candidate_contract:
                    candidate_type = contract_type
                if keyword in job_contract:
                    job_type = contract_type
        
        if candidate_type and job_type and candidate_type in compatibility and job_type in compatibility[candidate_type]:
            return compatibility[candidate_type][job_type]
        
        # Si l'un n'est pas reconnu, on applique une heuristique simple
        if candidate_type in compatibility and job_type is None:
            # Si le type du candidat est CDI, attribuer 0.7 (potentiellement compatible)
            if candidate_type == "cdi":
                return 0.7
            # Sinon attribuer 0.5 (neutre)
            return 0.5
        
        # Valeur par défaut
        return 0.5
    
    def _extract_preferred_work_mode(self, candidate_profile):
        """
        Extrait le mode de travail préféré par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Mode de travail préféré
        """
        if not candidate_profile:
            return ""
        
        # Chemins possibles pour le mode de travail
        mode_fields = [
            "preferred_work_mode", "work_mode_preference", "remote_preference",
            "work_preferences.work_mode", "work_preferences.remote"
        ]
        
        for field in mode_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, str) and current.strip():
                    value = current.strip().lower()
                    
                    # Correspondance avec un mode connu
                    for mode_type, keywords in self.work_modes.items():
                        if any(keyword in value for keyword in keywords):
                            return mode_type
                    
                    # Valeurs booléennes
                    if value in ["yes", "true", "1", "oui"]:
                        return "remote"
                    elif value in ["no", "false", "0", "non"]:
                        return "onsite"
                    
                    return value
                elif isinstance(current, bool):
                    return "remote" if current else "onsite"
                elif isinstance(current, (int, float)):
                    # Interprétation comme pourcentage de télétravail
                    if current == 0:
                        return "onsite"
                    elif current >= 80:
                        return "remote"
                    else:
                        return "hybrid"
        
        # Recherche dans d'autres champs textuels
        text_fields = ["about_me", "job_preferences", "work_preferences"]
        
        combined_text = ""
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                combined_text += " " + candidate_profile[field].lower()
        
        # Recherche des modes de travail dans le texte
        for mode_type, keywords in self.work_modes.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return mode_type
        
        return ""
    
    def _extract_job_work_mode(self, job_profile):
        """
        Extrait le mode de travail du poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Mode de travail
        """
        if not job_profile:
            return ""
        
        # Chemins possibles pour le mode de travail
        mode_fields = [
            "work_mode", "remote", "remote_work", "work_type",
            "workplace_type", "workplace.type"
        ]
        
        for field in mode_fields:
            parts = field.split('.')
            current = job_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, str) and current.strip():
                    value = current.strip().lower()
                    
                    # Correspondance avec un mode connu
                    for mode_type, keywords in self.work_modes.items():
                        if any(keyword in value for keyword in keywords):
                            return mode_type
                    
                    # Valeurs booléennes
                    if value in ["yes", "true", "1", "oui"]:
                        return "remote"
                    elif value in ["no", "false", "0", "non"]:
                        return "onsite"
                    
                    return value
                elif isinstance(current, bool):
                    return "remote" if current else "onsite"
                elif isinstance(current, (int, float)):
                    # Interprétation comme pourcentage de télétravail
                    if current == 0:
                        return "onsite"
                    elif current >= 80:
                        return "remote"
                    else:
                        return "hybrid"
        
        # Recherche dans la description ou d'autres champs
        text_fields = ["description", "job_description", "details"]
        
        combined_text = ""
        for field in text_fields:
            if field in job_profile and isinstance(job_profile[field], str):
                combined_text += " " + job_profile[field].lower()
        
        # Recherche des modes de travail dans le texte
        for mode_type, keywords in self.work_modes.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return mode_type
        
        return ""
    
    def calculate_work_mode_match(self, candidate_mode, job_mode):
        """
        Calcule la correspondance entre les modes de travail.
        
        Args:
            candidate_mode: Mode de travail préféré par le candidat
            job_mode: Mode de travail du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_mode or not job_mode:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Normaliser les modes de travail
        candidate_mode = candidate_mode.lower()
        job_mode = job_mode.lower()
        
        # Correspondance exacte
        if candidate_mode == job_mode:
            return 1.0
        
        # Matrice de compatibilité entre modes de travail
        compatibility = {
            "remote": {"remote": 1.0, "hybrid": 0.7, "onsite": 0.2},
            "hybrid": {"remote": 0.8, "hybrid": 1.0, "onsite": 0.7},
            "onsite": {"remote": 0.3, "hybrid": 0.7, "onsite": 1.0}
        }
        
        if candidate_mode in compatibility and job_mode in compatibility[candidate_mode]:
            return compatibility[candidate_mode][job_mode]
        
        # Valeur par défaut
        return 0.5
    
    def _extract_expected_salary(self, candidate_profile):
        """
        Extrait les attentes salariales du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            Dict: Attentes salariales {min, max, currency}
        """
        if not candidate_profile:
            return {}
        
        salary_info = {}
        
        # Chemins possibles pour les attentes salariales
        salary_fields = [
            "expected_salary", "salary_expectation", "desired_salary",
            "salary_requirements", "compensation.expected"
        ]
        
        for field in salary_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, dict):
                    # Structure de salaire avec min/max/exact
                    if "min" in current:
                        salary_info["min"] = self._parse_salary_value(current["min"])
                    if "max" in current:
                        salary_info["max"] = self._parse_salary_value(current["max"])
                    if "expected" in current:
                        salary_info["expected"] = self._parse_salary_value(current["expected"])
                    if "currency" in current:
                        salary_info["currency"] = current["currency"]
                    
                    break
                elif isinstance(current, (int, float)):
                    # Valeur numérique directe
                    salary_info["expected"] = current
                    break
                elif isinstance(current, str) and current.strip():
                    # Essayer d'extraire des valeurs numériques de la chaîne
                    parsed = self._parse_salary_string(current)
                    if parsed:
                        salary_info.update(parsed)
                        break
        
        # Si aucune information n'a été trouvée, chercher dans d'autres champs textuels
        if not salary_info:
            text_fields = ["about_me", "job_preferences", "work_preferences"]
            
            for field in text_fields:
                if field in candidate_profile and isinstance(candidate_profile[field], str):
                    text = candidate_profile[field]
                    
                    # Recherche de patterns de salaire
                    parsed = self._parse_salary_string(text)
                    if parsed:
                        salary_info.update(parsed)
                        break
        
        return salary_info
    
    def _extract_job_salary(self, job_profile):
        """
        Extrait les informations salariales du poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Informations salariales {min, max, currency}
        """
        if not job_profile:
            return {}
        
        salary_info = {}
        
        # Chemins possibles pour les informations salariales
        salary_fields = [
            "salary", "compensation", "salary_range",
            "remuneration", "package"
        ]
        
        for field in salary_fields:
            if field in job_profile:
                current = job_profile[field]
                
                if isinstance(current, dict):
                    # Structure de salaire avec min/max
                    if "min" in current:
                        salary_info["min"] = self._parse_salary_value(current["min"])
                    if "max" in current:
                        salary_info["max"] = self._parse_salary_value(current["max"])
                    if "currency" in current:
                        salary_info["currency"] = current["currency"]
                    
                    break
                elif isinstance(current, (int, float)):
                    # Valeur numérique directe
                    salary_info["min"] = current
                    salary_info["max"] = current
                    break
                elif isinstance(current, str) and current.strip():
                    # Essayer d'extraire des valeurs numériques de la chaîne
                    parsed = self._parse_salary_string(current)
                    if parsed:
                        salary_info.update(parsed)
                        break
        
        # Si aucune information n'a été trouvée, chercher dans la description
        if not salary_info and "description" in job_profile:
            description = job_profile["description"]
            if isinstance(description, str):
                # Recherche de patterns de salaire
                parsed = self._parse_salary_string(description)
                if parsed:
                    salary_info.update(parsed)
        
        return salary_info
    
    def _parse_salary_value(self, value):
        """
        Convertit une valeur salariale en nombre.
        
        Args:
            value: Valeur à convertir
            
        Returns:
            float: Valeur salariale normalisée
        """
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Supprimer les caractères non numériques, sauf les points et virgules
            numeric_str = re.sub(r'[^\d\.,]', '', value)
            
            # Remplacer les virgules par des points
            numeric_str = numeric_str.replace(',', '.')
            
            # Essayer de convertir en nombre
            try:
                return float(numeric_str)
            except:
                pass
        
        return 0.0
    
    def _parse_salary_string(self, text):
        """
        Extrait les informations salariales d'une chaîne de texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Informations salariales extraites
        """
        if not text:
            return {}
        
        salary_info = {}
        text = text.lower()
        
        # Détection de la devise
        currencies = {
            "€": "EUR",
            "euros": "EUR",
            "eur": "EUR",
            "$": "USD",
            "usd": "USD",
            "dollars": "USD",
            "£": "GBP",
            "gbp": "GBP",
            "livres": "GBP",
            "pounds": "GBP",
            "chf": "CHF",
            "francs": "CHF"
        }
        
        for symbol, code in currencies.items():
            if symbol in text:
                salary_info["currency"] = code
                break
        
        # Détection du rythme (annuel, mensuel, journalier, horaire)
        rhythm_multipliers = {
            "annuel": 1,
            "annual": 1,
            "an": 1,
            "année": 1,
            "year": 1,
            "yearly": 1,
            "mensuel": 12,
            "monthly": 12,
            "mois": 12,
            "month": 12,
            "jour": 220,  # Environ 220 jours travaillés par an
            "journalier": 220,
            "daily": 220,
            "day": 220,
            "heure": 1750,  # Environ 1750 heures travaillées par an
            "horaire": 1750,
            "hourly": 1750,
            "hour": 1750
        }
        
        rhythm_multiplier = 1  # Par défaut, supposer annuel
        
        for rhythm, multiplier in rhythm_multipliers.items():
            if rhythm in text:
                rhythm_multiplier = multiplier
                break
        
        # Détection de la fourchette salariale avec pattern matching
        # Format: XX-YY, XX à YY, XX to YY, entre XX et YY, from XX to YY
        range_patterns = [
            r'(\d+[\d\s.,]*)\s*[-–—]\s*(\d+[\d\s.,]*)',           # XX-YY
            r'(\d+[\d\s.,]*)\s*à\s*(\d+[\d\s.,]*)',              # XX à YY
            r'(\d+[\d\s.,]*)\s*to\s*(\d+[\d\s.,]*)',             # XX to YY
            r'entre\s*(\d+[\d\s.,]*)\s*et\s*(\d+[\d\s.,]*)',     # entre XX et YY
            r'from\s*(\d+[\d\s.,]*)\s*to\s*(\d+[\d\s.,]*)'       # from XX to YY
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, text)
            if match:
                min_value = self._normalize_number(match.group(1))
                max_value = self._normalize_number(match.group(2))
                
                if min_value and max_value:
                    # Convert to annual rate if needed
                    if rhythm_multiplier > 1:
                        min_value *= rhythm_multiplier
                        max_value *= rhythm_multiplier
                    
                    salary_info["min"] = min_value
                    salary_info["max"] = max_value
                    return salary_info
        
        # Si aucune fourchette n'est trouvée, chercher une valeur unique
        # Format: XX, XX K, XX,XXX, etc.
        single_patterns = [
            r'(\d+[\d\s.,]*k)',                        # 50k, 50 k
            r'(\d+[\d\s.,]*)\s*k€',                    # 50k€
            r'(\d+[\d\s.,]*)\s*k\$',                   # 50k$
            r'(\d+[\d\s.,]*)\s*k£',                    # 50k£
            r'(\d+[\d\s.,]*)\s*mille',                 # 50 mille
            r'(\d+[\d\s.,]*)\s*thousand',              # 50 thousand
            r'(\d+[\d\s.,]*)[\s€£$]*'                  # Nombre simple avec ou sans symbole
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, text)
            if match:
                value = self._normalize_number(match.group(1))
                
                if 'k' in match.group(1).lower():
                    value *= 1000
                
                if value:
                    # Convert to annual rate if needed
                    if rhythm_multiplier > 1:
                        value *= rhythm_multiplier
                    
                    # Déduire min/max (±10%)
                    salary_info["min"] = value * 0.9
                    salary_info["max"] = value * 1.1
                    salary_info["expected"] = value
                    return salary_info
        
        return salary_info
    
    def _normalize_number(self, text):
        """
        Normalise une chaîne numérique en un nombre.
        
        Args:
            text: Chaîne à normaliser
            
        Returns:
            float: Nombre normalisé
        """
        if not text:
            return 0.0
        
        # Supprimer les caractères non numériques, sauf les points et virgules
        numeric_str = re.sub(r'[^\d\.,]', '', text)
        
        # Remplacer les virgules par des points
        numeric_str = numeric_str.replace(',', '.')
        
        # Essayer de convertir en nombre
        try:
            return float(numeric_str)
        except:
            return 0.0
    
    def calculate_salary_match(self, candidate_salary, job_salary):
        """
        Calcule la correspondance entre les attentes salariales et l'offre.
        
        Args:
            candidate_salary: Attentes salariales du candidat
            job_salary: Informations salariales du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_salary or not job_salary:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Extraire les valeurs min/max pour les deux côtés
        candidate_min = candidate_salary.get("min", 0)
        candidate_max = candidate_salary.get("max", 0)
        candidate_expected = candidate_salary.get("expected", 0)
        
        job_min = job_salary.get("min", 0)
        job_max = job_salary.get("max", 0)
        
        # Si le candidat a seulement une valeur attendue
        if candidate_min == 0 and candidate_max == 0 and candidate_expected > 0:
            candidate_min = candidate_expected * 0.9
            candidate_max = candidate_expected * 1.1
        
        # Si l'offre a seulement une valeur minimale
        if job_min > 0 and job_max == 0:
            job_max = job_min * 1.2  # Estimer un maximum à +20%
        
        # Si le candidat a seulement une valeur minimale
        if candidate_min > 0 and candidate_max == 0:
            candidate_max = candidate_min * 1.3  # Estimer un maximum à +30%
        
        # Vérifier les devises
        candidate_currency = candidate_salary.get("currency", "EUR")
        job_currency = job_salary.get("currency", "EUR")
        
        # Si les devises sont différentes, appliquer une conversion approximative
        if candidate_currency != job_currency:
            # Conversion simplifiée (à remplacer par une vraie API de conversion)
            exchange_rates = {
                "EUR_USD": 1.1,  # 1 EUR = 1.1 USD
                "USD_EUR": 0.9,  # 1 USD = 0.9 EUR
                "GBP_EUR": 1.2,  # 1 GBP = 1.2 EUR
                "EUR_GBP": 0.85  # 1 EUR = 0.85 GBP
            }
            
            conversion_key = f"{candidate_currency}_{job_currency}"
            inverse_key = f"{job_currency}_{candidate_currency}"
            
            if conversion_key in exchange_rates:
                candidate_min *= exchange_rates[conversion_key]
                candidate_max *= exchange_rates[conversion_key]
                candidate_expected *= exchange_rates[conversion_key]
            elif inverse_key in exchange_rates:
                candidate_min /= exchange_rates[inverse_key]
                candidate_max /= exchange_rates[inverse_key]
                candidate_expected /= exchange_rates[inverse_key]
        
        # Calculer le chevauchement des fourchettes
        if candidate_min == 0 or job_min == 0:
            # Si les données sont incomplètes
            if candidate_expected > 0 and job_min > 0 and job_max > 0:
                # Voir si le salaire attendu est dans la fourchette du poste
                if job_min <= candidate_expected <= job_max:
                    return 1.0
                elif candidate_expected < job_min:
                    # Candidat demande moins que l'offre (bon pour l'employeur)
                    return 0.9
                else:
                    # Candidat demande plus que le maximum
                    ratio = job_max / candidate_expected
                    return max(0.0, min(0.8, ratio))
            else:
                return 0.5  # Valeur neutre si les données sont trop incomplètes
        
        # Calculer le chevauchement des fourchettes
        overlap_min = max(candidate_min, job_min)
        overlap_max = min(candidate_max, job_max)
        
        if overlap_max < overlap_min:
            # Aucun chevauchement
            if candidate_max < job_min:
                # Le candidat demande moins que le minimum offert
                ratio = candidate_max / job_min
                return min(1.0, 0.7 + ratio * 0.3)  # Max 1.0, min 0.7
            else:
                # Le candidat demande plus que le maximum offert
                ratio = job_max / candidate_min
                return max(0.0, ratio * 0.8)  # Max 0.8, min 0.0
        else:
            # Chevauchement des fourchettes
            overlap_size = overlap_max - overlap_min
            candidate_range = candidate_max - candidate_min
            job_range = job_max - job_min
            
            # Calculer le ratio de chevauchement par rapport aux deux fourchettes
            candidate_overlap_ratio = overlap_size / candidate_range if candidate_range > 0 else 0
            job_overlap_ratio = overlap_size / job_range if job_range > 0 else 0
            
            # Moyenne pondérée des ratios
            weighted_ratio = (candidate_overlap_ratio * 0.7) + (job_overlap_ratio * 0.3)
            
            return min(1.0, weighted_ratio)
    
    def _extract_preferred_company_size(self, candidate_profile):
        """
        Extrait la taille d'entreprise préférée par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Taille d'entreprise préférée
        """
        if not candidate_profile:
            return ""
        
        # Chemins possibles pour la taille d'entreprise
        size_fields = [
            "preferred_company_size", "company_size_preference",
            "work_preferences.company_size", "preferred_employer.size"
        ]
        
        for field in size_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, str) and current.strip():
                value = current.strip().lower()
                
                # Correspondance avec une taille connue
                for size_type, keywords in self.company_sizes.items():
                    if any(keyword in value for keyword in keywords):
                        return size_type
                
                return value
        
        # Recherche dans d'autres champs textuels
        text_fields = ["about_me", "job_preferences", "work_preferences"]
        
        combined_text = ""
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                combined_text += " " + candidate_profile[field].lower()
        
        # Recherche des tailles d'entreprise dans le texte
        for size_type, keywords in self.company_sizes.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return size_type
        
        return ""
    
    def _extract_company_size(self, job_profile):
        """
        Extrait la taille de l'entreprise proposant le poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Taille de l'entreprise
        """
        if not job_profile:
            return ""
        
        # Chemins possibles pour la taille d'entreprise
        size_fields = [
            "company_size", "company.size", "employer_size",
            "organization_size", "workforce"
        ]
        
        for field in size_fields:
            parts = field.split('.')
            current = job_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, str) and current.strip():
                    value = current.strip().lower()
                    
                    # Correspondance avec une taille connue
                    for size_type, keywords in self.company_sizes.items():
                        if any(keyword in value for keyword in keywords):
                            return size_type
                    
                    # Analyse numérique
                    if re.search(r'\d+', value):
                        numbers = re.findall(r'\d+', value)
                        if numbers:
                            num = int(numbers[0])
                            
                            if num < 20:
                                return "startup"
                            elif num < 250:
                                return "sme"
                            elif num < 1000:
                                return "large"
                            else:
                                return "multinational"
                    
                    return value
                elif isinstance(current, (int, float)):
                    # Interprétation numérique directe
                    num = int(current)
                    
                    if num < 20:
                        return "startup"
                    elif num < 250:
                        return "sme"
                    elif num < 1000:
                        return "large"
                    else:
                        return "multinational"
        
        # Recherche dans la description ou le nom de l'entreprise
        text_fields = ["company_description", "about_company", "company_name"]
        
        combined_text = ""
        for field in text_fields:
            if field in job_profile and isinstance(job_profile[field], str):
                combined_text += " " + job_profile[field].lower()
        
        # Recherche des indices de taille dans le texte
        for size_type, keywords in self.company_sizes.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return size_type
        
        # Cas des grands groupes connus
        if "company_name" in job_profile and isinstance(job_profile["company_name"], str):
            company_name = job_profile["company_name"].lower()
            
            # Liste indicative de grands groupes
            large_companies = ["google", "amazon", "microsoft", "apple", "facebook", "meta", 
                             "ibm", "oracle", "sap", "accenture", "capgemini", "atos",
                             "orange", "edf", "total", "bnp", "société générale", "axa"]
            
            for large_company in large_companies:
                if large_company in company_name:
                    return "multinational"
        
        return ""
    
    def calculate_company_size_match(self, candidate_preference, company_size):
        """
        Calcule la correspondance entre les tailles d'entreprise.
        
        Args:
            candidate_preference: Taille préférée par le candidat
            company_size: Taille de l'entreprise
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_preference or not company_size:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Normaliser les tailles
        candidate_preference = candidate_preference.lower()
        company_size = company_size.lower()
        
        # Correspondance exacte
        if candidate_preference == company_size:
            return 1.0
        
        # Matrice de compatibilité entre tailles d'entreprise
        compatibility = {
            "startup": {"startup": 1.0, "sme": 0.8, "large": 0.4, "multinational": 0.2},
            "sme": {"startup": 0.7, "sme": 1.0, "large": 0.7, "multinational": 0.5},
            "large": {"startup": 0.3, "sme": 0.7, "large": 1.0, "multinational": 0.8},
            "multinational": {"startup": 0.2, "sme": 0.5, "large": 0.8, "multinational": 1.0}
        }
        
        if candidate_preference in compatibility and company_size in compatibility[candidate_preference]:
            return compatibility[candidate_preference][company_size]
        
        # Valeur par défaut
        return 0.5
    
    def _extract_preferred_industries(self, candidate_profile):
        """
        Extrait les secteurs d'activité préférés par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            List: Secteurs préférés
        """
        if not candidate_profile:
            return []
        
        industries = []
        
        # Chemins possibles pour les secteurs préférés
        industry_fields = [
            "preferred_industries", "preferred_sectors", "industry_preference",
            "work_preferences.industries", "desired_industries"
        ]
        
        for field in industry_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, list):
                    for item in current:
                        if isinstance(item, str) and item.strip():
                            industries.append(item.strip().lower())
                elif isinstance(current, str) and current.strip():
                    for industry in current.split(','):
                        if industry.strip():
                            industries.append(industry.strip().lower())
        
        # Si aucune préférence explicite n'est trouvée, déduire des expériences passées
        if not industries and "experience" in candidate_profile:
            experiences = candidate_profile["experience"]
            
            if isinstance(experiences, list):
                for exp in experiences:
                    if isinstance(exp, dict) and "industry" in exp:
                        industry = exp["industry"]
                        if isinstance(industry, str) and industry.strip():
                            industries.append(industry.strip().lower())
        
        # Enlever les doublons
        return list(set(industries))
    
    def _extract_job_industry(self, job_profile):
        """
        Extrait le secteur d'activité du poste/de l'entreprise.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Secteur d'activité
        """
        if not job_profile:
            return ""
        
        # Chemins possibles pour le secteur d'activité
        industry_fields = [
            "industry", "sector", "company_industry",
            "company.industry", "business_sector"
        ]
        
        for field in industry_fields:
            parts = field.split('.')
            current = job_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, str) and current.strip():
                return current.strip().lower()
        
        # Recherche dans d'autres champs
        text_fields = ["company_description", "about_company", "job_description"]
        
        for field in text_fields:
            if field in job_profile and isinstance(job_profile[field], str):
                # Essayer de détecter le secteur dans le texte
                text = job_profile[field].lower()
                
                for industry_type, keywords in self.industry_types.items():
                    for keyword in keywords:
                        if keyword in text:
                            return industry_type
        
        return ""
    
    def calculate_industry_match(self, candidate_industries, job_industry):
        """
        Calcule la correspondance entre les secteurs d'activité.
        
        Args:
            candidate_industries: Secteurs préférés par le candidat
            job_industry: Secteur du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_industries or not job_industry:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Si correspondance directe
        if job_industry in candidate_industries:
            return 1.0
        
        # Vérifier les correspondances partielles
        for candidate_industry in candidate_industries:
            # Correspondance textuelle partielle
            if candidate_industry in job_industry or job_industry in candidate_industry:
                return 0.9
            
            # Vérifier via la taxonomie des industries
            for industry_type, keywords in self.industry_types.items():
                if industry_type == job_industry or job_industry in keywords:
                    # L'industrie du poste correspond à cette catégorie
                    if industry_type == candidate_industry or candidate_industry in keywords:
                        # Le candidat préfère cette même catégorie
                        return 0.9
        
        # Si aucune correspondance n'est trouvée mais le candidat a plusieurs préférences
        if len(candidate_industries) > 2:
            return 0.4  # Le candidat semble flexible sur l'industrie
        
        # Faible correspondance
        return 0.2
    
    def _extract_preferred_work_hours(self, candidate_profile):
        """
        Extrait les préférences d'horaires de travail du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            Dict: Préférences d'horaires {type, min_hours, max_hours}
        """
        if not candidate_profile:
            return {}
        
        hours_info = {}
        
        # Chemins possibles pour les préférences d'horaires
        hours_fields = [
            "preferred_work_hours", "work_hours_preference",
            "work_preferences.hours", "work_time_preference"
        ]
        
        for field in hours_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, dict):
                    # Structure détaillée
                    for key, value in current.items():
                        hours_info[key] = value
                    break
                elif isinstance(current, str) and current.strip():
                    # Analyse textuelle
                    text = current.strip().lower()
                    
                    # Détecter le type (temps plein, partiel, etc.)
                    if "plein" in text or "full" in text:
                        hours_info["type"] = "full_time"
                    elif "partiel" in text or "part" in text:
                        hours_info["type"] = "part_time"
                    elif "flexible" in text:
                        hours_info["type"] = "flexible"
                    
                    # Essayer d'extraire les heures
                    hours_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*(?:h|hour|heure)', text)
                    if hours_match:
                        if hours_match.group(2):  # Fourchette d'heures
                            hours_info["min_hours"] = int(hours_match.group(1))
                            hours_info["max_hours"] = int(hours_match.group(2))
                        else:  # Valeur unique
                            hours_value = int(hours_match.group(1))
                            if hours_value < 30:
                                hours_info["type"] = "part_time"
                                hours_info["hours"] = hours_value
                            else:
                                hours_info["type"] = "full_time"
                                hours_info["hours"] = hours_value
                    
                    break
        
        # Si aucune information spécifique n'est trouvée, chercher dans d'autres champs
        if not hours_info:
            text_fields = ["about_me", "job_preferences", "work_preferences"]
            
            combined_text = ""
            for field in text_fields:
                if field in candidate_profile and isinstance(candidate_profile[field], str):
                    combined_text += " " + candidate_profile[field].lower()
            
            # Analyse simplifiée du texte combiné
            if "temps plein" in combined_text or "full time" in combined_text:
                hours_info["type"] = "full_time"
            elif "temps partiel" in combined_text or "part time" in combined_text:
                hours_info["type"] = "part_time"
            elif "flexible" in combined_text:
                hours_info["type"] = "flexible"
        
        return hours_info
    
    def _extract_job_work_hours(self, job_profile):
        """
        Extrait les horaires de travail du poste.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Horaires de travail {type, hours, min_hours, max_hours}
        """
        if not job_profile:
            return {}
        
        hours_info = {}
        
        # Chemins possibles pour les horaires
        hours_fields = [
            "work_hours", "hours", "working_hours",
            "job_type", "employment_type"
        ]
        
        for field in hours_fields:
            if field in job_profile:
                value = job_profile[field]
                
                if isinstance(value, dict):
                    # Structure détaillée
                    for key, val in value.items():
                        hours_info[key] = val
                    break
                elif isinstance(value, str) and value.strip():
                    # Analyse textuelle
                    text = value.strip().lower()
                    
                    # Détecter le type (temps plein, partiel, etc.)
                    if "plein" in text or "full" in text or "cdi" in text:
                        hours_info["type"] = "full_time"
                    elif "partiel" in text or "part" in text:
                        hours_info["type"] = "part_time"
                    elif "flexible" in text:
                        hours_info["type"] = "flexible"
                    elif "stage" in text or "internship" in text:
                        hours_info["type"] = "full_time"  # Supposer temps plein pour les stages
                    
                    # Essayer d'extraire les heures
                    hours_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*(?:h|hour|heure)', text)
                    if hours_match:
                        if hours_match.group(2):  # Fourchette d'heures
                            hours_info["min_hours"] = int(hours_match.group(1))
                            hours_info["max_hours"] = int(hours_match.group(2))
                        else:  # Valeur unique
                            hours_value = int(hours_match.group(1))
                            if hours_value < 35:
                                hours_info["type"] = "part_time"
                                hours_info["hours"] = hours_value
                            else:
                                hours_info["type"] = "full_time"
                                hours_info["hours"] = hours_value
                    
                    break
        
        # Si aucune information spécifique n'est trouvée, chercher dans la description
        if not hours_info and "description" in job_profile:
            description = job_profile["description"]
            if isinstance(description, str):
                text = description.lower()
                
                # Analyse simplifiée du texte
                if "temps plein" in text or "full time" in text or "cdi" in text:
                    hours_info["type"] = "full_time"
                elif "temps partiel" in text or "part time" in text:
                    hours_info["type"] = "part_time"
                elif "flexible" in text:
                    hours_info["type"] = "flexible"
                
                # Chercher les heures spécifiques
                hours_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*(?:h|hour|heure)', text)
                if hours_match:
                    if hours_match.group(2):  # Fourchette d'heures
                        hours_info["min_hours"] = int(hours_match.group(1))
                        hours_info["max_hours"] = int(hours_match.group(2))
                    else:  # Valeur unique
                        hours_value = int(hours_match.group(1))
                        hours_info["hours"] = hours_value
        
        # Valeur par défaut si rien n'est trouvé
        if not hours_info:
            hours_info["type"] = "full_time"  # Supposer temps plein par défaut
        
        return hours_info
    
    def calculate_work_hours_match(self, candidate_hours, job_hours):
        """
        Calcule la correspondance entre les préférences d'horaires.
        
        Args:
            candidate_hours: Préférences d'horaires du candidat
            job_hours: Horaires du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not candidate_hours or not job_hours:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Extraction des types d'horaires
        candidate_type = candidate_hours.get("type", "")
        job_type = job_hours.get("type", "")
        
        # Correspondance exacte des types
        if candidate_type and job_type and candidate_type == job_type:
            return 1.0
        
        # Matrice de compatibilité des types d'horaires
        compatibility = {
            "full_time": {"full_time": 1.0, "part_time": 0.3, "flexible": 0.8},
            "part_time": {"full_time": 0.2, "part_time": 1.0, "flexible": 0.8},
            "flexible": {"full_time": 0.7, "part_time": 0.8, "flexible": 1.0}
        }
        
        if candidate_type in compatibility and job_type in compatibility[candidate_type]:
            type_score = compatibility[candidate_type][job_type]
        else:
            type_score = 0.5  # Valeur neutre si les types ne sont pas reconnus
        
        # Vérification des heures spécifiques
        hours_score = 0.5  # Valeur par défaut
        
        candidate_hours_value = candidate_hours.get("hours", 0)
        job_hours_value = job_hours.get("hours", 0)
        
        candidate_min = candidate_hours.get("min_hours", 0)
        candidate_max = candidate_hours.get("max_hours", 0)
        
        job_min = job_hours.get("min_hours", 0)
        job_max = job_hours.get("max_hours", 0)
        
        # Si les deux ont des valeurs d'heures spécifiques
        if candidate_hours_value > 0 and job_hours_value > 0:
            # Calculer la proximité
            diff = abs(candidate_hours_value - job_hours_value)
            if diff == 0:
                hours_score = 1.0
            elif diff <= 5:
                hours_score = 0.9
            elif diff <= 10:
                hours_score = 0.7
            else:
                hours_score = 0.5
        
        # Si les deux ont des fourchettes d'heures
        elif candidate_min > 0 and candidate_max > 0 and job_min > 0 and job_max > 0:
            # Calculer le chevauchement
            overlap_min = max(candidate_min, job_min)
            overlap_max = min(candidate_max, job_max)
            
            if overlap_max >= overlap_min:
                # Il y a chevauchement
                overlap_size = overlap_max - overlap_min
                candidate_range = candidate_max - candidate_min
                job_range = job_max - job_min
                
                overlap_ratio = overlap_size / min(candidate_range, job_range)
                hours_score = overlap_ratio
            else:
                # Pas de chevauchement, calcul de proximité
                if candidate_max < job_min:
                    diff = job_min - candidate_max
                else:
                    diff = candidate_min - job_max
                
                if diff <= 5:
                    hours_score = 0.5
                elif diff <= 10:
                    hours_score = 0.3
                else:
                    hours_score = 0.1
        
        # Combinaison des scores de type et d'heures
        if hours_score == 0.5:  # Si pas d'information spécifique sur les heures
            return type_score
        else:
            # Pondération : 60% type, 40% heures
            return (type_score * 0.6) + (hours_score * 0.4)
    
    def _extract_max_commute_time(self, candidate_profile):
        """
        Extrait le temps de trajet maximal accepté par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            int: Temps de trajet maximal en minutes
        """
        if not candidate_profile:
            return 0
        
        # Chemins possibles pour le temps de trajet
        commute_fields = [
            "max_commute_time", "commute_preference", "commute_max",
            "work_preferences.commute_time", "mobility.max_commute"
        ]
        
        for field in commute_fields:
            parts = field.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, (int, float)):
                    return int(current)
                elif isinstance(current, str):
                    # Essayer d'extraire un nombre
                    match = re.search(r'(\d+)', current)
                    if match:
                        value = int(match.group(1))
                        
                        # Convertir en minutes si nécessaire
                        if "h" in current.lower() or "hour" in current.lower() or "heure" in current.lower():
                            value *= 60
                        
                        return value
        
        # Recherche dans d'autres champs textuels
        text_fields = ["about_me", "job_preferences", "work_preferences"]
        
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                text = candidate_profile[field].lower()
                
                # Chercher des patterns comme "30 min max", "maximum 1h", etc.
                hour_match = re.search(r'(?:max|maximum|moins de|jusqu\'à)\s*(\d+)\s*(?:h|hour|heure)', text)
                if hour_match:
                    return int(hour_match.group(1)) * 60
                
                min_match = re.search(r'(?:max|maximum|moins de|jusqu\'à)\s*(\d+)\s*(?:min|minute)', text)
                if min_match:
                    return int(min_match.group(1))
        
        # Valeur par défaut (60 minutes, une heure de trajet)
        return 60
    
    def calculate_commute_time_match(self, max_commute_time, candidate_address, job_location):
        """
        Estime la correspondance de temps de trajet.
        Note: Dans un système réel, on utiliserait une API de calcul de temps de trajet.
        
        Args:
            max_commute_time: Temps de trajet maximal accepté (minutes)
            candidate_address: Adresse du candidat
            job_location: Localisation du poste
            
        Returns:
            float: Score de correspondance (0.0 - 1.0)
        """
        if not max_commute_time or not candidate_address or not job_location:
            return 0.5  # Valeur neutre si l'information est manquante
        
        # Simplification: vérifier si les villes correspondent directement
        candidate_city, _ = self._extract_city_region(candidate_address)
        job_city, _ = self._extract_city_region(job_location)
        
        if candidate_city and job_city and candidate_city == job_city:
            # Même ville, très bonne correspondance
            return 1.0
        
        # Simplification: estimation du temps de trajet basée sur une heuristique
        # (Dans un vrai système, utiliser Google Maps Distance Matrix API)
        
        # Supposer un temps de trajet de 30min si même département, 90min sinon
        _, candidate_dept = self._extract_city_region(candidate_address)
        _, job_dept = self._extract_city_region(job_location)
        
        estimated_commute_time = 30 if candidate_dept and job_dept and candidate_dept == job_dept else 90
        
        # Calculer le ratio par rapport au temps maximal accepté
        if estimated_commute_time <= max_commute_time:
            # Le trajet estimé est acceptable
            ratio = 1 - (estimated_commute_time / max_commute_time)
            return 0.7 + (ratio * 0.3)  # Score entre 0.7 et 1.0
        else:
            # Le trajet estimé dépasse le maximum accepté
            overage = estimated_commute_time / max_commute_time
            if overage <= 1.5:
                # Dépassement modéré (jusqu'à 50% de plus)
                return 0.5 - ((overage - 1) * 0.6)  # Score entre 0.2 et 0.5
            else:
                # Dépassement important
                return 0.2
