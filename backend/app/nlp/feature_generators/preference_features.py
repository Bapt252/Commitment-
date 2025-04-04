"""
Générateur de features basées sur les préférences professionnelles.
Ce module analyse les préférences des candidats (lieu, rémunération, 
mode de travail, etc.) et leur compatibilité avec les offres d'emploi.
"""

import logging
import re
import json
from pathlib import Path
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

try:
    from geopy.geocoders import Nominatim
    GEOCODING_AVAILABLE = True
except ImportError:
    GEOCODING_AVAILABLE = False


class PreferenceFeatureGenerator:
    """
    Générateur de features pour les préférences professionnelles.
    """
    
    def __init__(self, geo_timeout=5):
        """
        Initialise le générateur de features de préférences.
        
        Args:
            geo_timeout: Timeout pour les requêtes de géocodage (en secondes)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialiser le géocodeur si disponible
        self.geocoder = None
        if GEOCODING_AVAILABLE:
            try:
                self.geocoder = Nominatim(user_agent="commitment_matcher", timeout=geo_timeout)
            except Exception as e:
                self.logger.warning(f"Impossible d'initialiser le géocodeur: {e}")
        
        # Charger les données d'équivalence des salaires
        self.salary_ranges = self._load_salary_ranges()
        
        # Dictionnaires pour la normalisation des préférences
        self.work_mode_mapping = {
            # Télétravail
            "remote": ["télétravail", "remote", "à distance", "home office", "work from home", "wfh", "distanciel"],
            # Présentiel
            "office": ["présentiel", "sur site", "sur place", "on-site", "office"],
            # Hybride
            "hybrid": ["hybride", "hybrid", "mixte", "flexible"]
        }
        
        self.contract_type_mapping = {
            # CDI
            "permanent": ["cdi", "permanent", "indéterminée", "indeterminee", "cdi", "full-time", "full time"],
            # CDD
            "temporary": ["cdd", "temporary", "déterminée", "determinee", "fixed term", "fixed-term"],
            # Freelance
            "freelance": ["freelance", "indépendant", "independant", "auto-entrepreneur", "consultant"],
            # Stage
            "internship": ["stage", "internship", "intern", "stagiaire"],
            # Alternance
            "apprenticeship": ["alternance", "apprentissage", "apprenticeship", "contrat pro", "professionnalisation"],
            # Temps partiel
            "part_time": ["temps partiel", "part time", "part-time"],
            # Intérim
            "interim": ["intérim", "interim", "temporaire", "temporary"]
        }
        
        self.company_size_mapping = {
            "startup": ["startup", "start-up", "early stage", "seed", "série a", "serie a", "series a"],
            "small": ["petite", "small", "tpe", "< 50", "moins de 50", "<50", "10-50"],
            "medium": ["moyenne", "medium", "pme", "eti", "50-250", "50 à 250", "50-500", "50 à 500"],
            "large": ["grande", "large", "grand groupe", "big company", "entreprise", "> 250", "plus de 250", ">250"]
        }
        
        self.work_environment_mapping = {
            "pace": {
                "fast": ["rapide", "fast-paced", "intense", "dynamique", "challenging"],
                "balanced": ["équilibré", "balanced", "normal", "modéré", "stable"],
                "relaxed": ["calme", "relaxed", "détendu", "tranquille", "quiet"]
            },
            "formality": {
                "formal": ["formel", "formal", "corporate", "structuré", "strict"],
                "casual": ["décontracté", "casual", "informel", "relaxed", "cool", "startup"]
            },
            "hierarchy": {
                "flat": ["plate", "flat", "horizontale", "collaborative", "agile"],
                "hierarchical": ["hiérarchique", "hierarchical", "structurée", "traditional"]
            },
            "management": {
                "directive": ["directif", "directive", "structuré", "structured", "strict"],
                "participative": ["participatif", "participative", "collaboratif", "inclusive"],
                "delegative": ["délégatif", "delegative", "autonome", "autonomous", "trust"]
            }
        }
        
        self.industry_mapping = self._load_industry_mapping()
    
    def _load_salary_ranges(self):
        """
        Charge les tranches salariales typiques par poste et expérience.
        """
        # Valeurs par défaut si aucun fichier n'est disponible
        default_ranges = {
            "junior": {
                "tech": {"min": 35000, "max": 45000},
                "marketing": {"min": 30000, "max": 40000},
                "sales": {"min": 30000, "max": 45000},
                "finance": {"min": 35000, "max": 45000},
                "hr": {"min": 30000, "max": 40000},
                "default": {"min": 30000, "max": 40000}
            },
            "mid": {
                "tech": {"min": 45000, "max": 65000},
                "marketing": {"min": 40000, "max": 60000},
                "sales": {"min": 45000, "max": 70000},
                "finance": {"min": 45000, "max": 70000},
                "hr": {"min": 40000, "max": 60000},
                "default": {"min": 40000, "max": 60000}
            },
            "senior": {
                "tech": {"min": 65000, "max": 95000},
                "marketing": {"min": 60000, "max": 90000},
                "sales": {"min": 70000, "max": 120000},
                "finance": {"min": 70000, "max": 110000},
                "hr": {"min": 60000, "max": 90000},
                "default": {"min": 65000, "max": 90000}
            },
            "executive": {
                "tech": {"min": 95000, "max": 200000},
                "marketing": {"min": 90000, "max": 180000},
                "sales": {"min": 100000, "max": 200000},
                "finance": {"min": 100000, "max": 200000},
                "hr": {"min": 90000, "max": 160000},
                "default": {"min": 90000, "max": 180000}
            }
        }
        
        try:
            # Chemin vers le fichier de configuration salariale
            salary_path = Path(__file__).resolve().parent.parent.parent / "data" / "salary_ranges.json"
            
            if salary_path.exists():
                with open(salary_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Fichier de tranches salariales non trouvé. Utilisation des valeurs par défaut.")
                return default_ranges
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des tranches salariales: {e}")
            return default_ranges

    def _load_industry_mapping(self):
        """
        Charge la classification des secteurs d'activité.
        """
        # Dictionnaire par défaut des secteurs d'activité
        default_mapping = {
            "tech": [
                "technologie", "informatique", "tech", "it", "digital", "logiciel", "software",
                "développement", "development", "programmation", "web", "mobile", "data",
                "ia", "ai", "intelligence artificielle", "artificial intelligence", "cloud"
            ],
            "finance": [
                "finance", "banque", "bank", "assurance", "insurance", "investissement", 
                "investment", "comptabilité", "accounting", "fintech"
            ],
            "healthcare": [
                "santé", "health", "médical", "medical", "pharmaceutique", "pharmaceutical",
                "hôpital", "hospital", "clinique", "clinic", "biotech"
            ],
            "education": [
                "éducation", "education", "enseignement", "teaching", "formation", "training",
                "académique", "academic", "école", "school", "université", "university"
            ],
            "media": [
                "média", "media", "presse", "press", "journalisme", "journalism",
                "édition", "publishing", "audiovisuel", "audiovisual", "cinéma", "cinema"
            ],
            "retail": [
                "commerce", "retail", "e-commerce", "ecommerce", "distribution", "vente",
                "sales", "consommation", "consumer"
            ],
            "manufacturing": [
                "industrie", "manufacturing", "production", "usine", "factory",
                "automobile", "automotive", "aéronautique", "aerospace"
            ],
            "energy": [
                "énergie", "energy", "pétrole", "oil", "gaz", "gas", "électricité",
                "electricity", "renouvelable", "renewable"
            ],
            "consulting": [
                "conseil", "consulting", "consultant", "audit", "stratégie", "strategy"
            ],
            "services": [
                "service", "services", "btp", "construction", "immobilier", "real estate",
                "transport", "logistique", "logistics", "tourisme", "tourism", "restauration"
            ],
            "public": [
                "public", "gouvernement", "government", "administration", "collectivité",
                "état", "state", "service public"
            ],
            "nonprofit": [
                "association", "nonprofit", "non-profit", "ong", "ngo", "humanitaire",
                "humanitarian", "social", "solidarité", "solidarity"
            ]
        }
        
        try:
            # Chemin vers le fichier de mapping des secteurs
            industry_path = Path(__file__).resolve().parent.parent.parent / "data" / "industry_mapping.json"
            
            if industry_path.exists():
                with open(industry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Fichier de mapping des secteurs non trouvé. Utilisation des valeurs par défaut.")
                return default_mapping
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du mapping des secteurs: {e}")
            return default_mapping
    
    def generate_preference_features(self, candidate_profile, job_profile):
        """
        Génère les features de compatibilité entre les préférences du candidat
        et les caractéristiques du poste.
        
        Args:
            candidate_profile: Dictionnaire contenant les informations du candidat
            job_profile: Dictionnaire contenant les informations du poste
            
        Returns:
            Dict: Features de compatibilité des préférences
        """
        features = {}
        
        # Location match
        features["location_match"] = self.calculate_location_match(
            self._extract_location(candidate_profile, "preferred"),
            self._extract_location(job_profile, "job")
        )
        
        # Salary match
        features["salary_match"] = self.calculate_salary_match(
            self._extract_salary(candidate_profile, "expected"),
            self._extract_salary(job_profile, "offered"),
            self._extract_job_category(job_profile),
            self._extract_experience_level(candidate_profile)
        )
        
        # Work mode match (remote, on-site, hybrid)
        features["work_mode_match"] = self.calculate_work_mode_match(
            self._extract_work_mode(candidate_profile, "preferred"),
            self._extract_work_mode(job_profile, "offered")
        )
        
        # Contract type match
        features["contract_type_match"] = self.calculate_contract_type_match(
            self._extract_contract_type(candidate_profile, "preferred"),
            self._extract_contract_type(job_profile, "offered")
        )
        
        # Company size match
        features["company_size_match"] = self.calculate_company_size_match(
            self._extract_company_size(candidate_profile, "preferred"),
            self._extract_company_size(job_profile, "actual")
        )
        
        # Work environment match (pace, formality, hierarchy, management)
        for env_type in self.work_environment_mapping.keys():
            features[f"work_env_{env_type}_match"] = self.calculate_work_environment_match(
                self._extract_work_environment(candidate_profile, env_type, "preferred"),
                self._extract_work_environment(job_profile, env_type, "actual")
            )
        
        # Industry match
        features["industry_match"] = self.calculate_industry_match(
            self._extract_industry(candidate_profile, "preferred"),
            self._extract_industry(job_profile, "company")
        )
        
        # Travel willingness match
        features["travel_match"] = self.calculate_travel_match(
            self._extract_travel_willingness(candidate_profile),
            self._extract_travel_requirements(job_profile)
        )
        
        return features
    
    def _extract_location(self, profile, location_type):
        """
        Extrait l'information de localisation du profil.
        
        Args:
            profile: Dictionnaire contenant les informations
            location_type: Type de localisation à extraire (preferred, job, etc.)
            
        Returns:
            str: Localisation extraite
        """
        if not profile:
            return None
        
        location = None
        
        if location_type == "preferred":
            # Chercher dans différents champs possibles pour la préférence de localisation
            for field in ["preferred_location", "location_preference", "desired_location"]:
                if field in profile and profile[field]:
                    location = profile[field]
                    break
            
            # Si pas trouvé, chercher dans d'autres champs possibles
            if not location:
                if "location" in profile:
                    location = profile["location"]
                elif "address" in profile:
                    location = profile["address"]
        
        elif location_type == "job":
            # Chercher dans différents champs possibles pour la localisation du poste
            for field in ["location", "job_location", "workplace", "address", "city"]:
                if field in profile and profile[field]:
                    location = profile[field]
                    break
        
        return location.strip().lower() if isinstance(location, str) else None
    
    def calculate_location_match(self, candidate_location, job_location):
        """
        Calcule la compatibilité entre la localisation souhaitée et celle du poste.
        
        Args:
            candidate_location: Localisation souhaitée par le candidat
            job_location: Localisation du poste
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_location or not job_location:
            return 0.5  # Valeur neutre par défaut
        
        # Si les locations sont exactement identiques
        if candidate_location.lower() == job_location.lower():
            return 1.0
            
        # Si l'une contient l'autre
        if candidate_location.lower() in job_location.lower() or job_location.lower() in candidate_location.lower():
            return 0.9
        
        # Vérifier les mots communs
        candidate_tokens = set(re.findall(r'\w+', candidate_location.lower()))
        job_tokens = set(re.findall(r'\w+', job_location.lower()))
        
        common_tokens = candidate_tokens.intersection(job_tokens)
        if common_tokens:
            # Plus il y a de mots en commun, plus le score est élevé
            return min(0.8, len(common_tokens) / max(len(candidate_tokens), len(job_tokens)) * 0.9)
        
        # Si le géocodage est disponible, essayer de calculer la distance
        if self.geocoder:
            try:
                candidate_coords = self._geocode(candidate_location)
                job_coords = self._geocode(job_location)
                
                if candidate_coords and job_coords:
                    # Calculer la distance en km
                    distance = geodesic(candidate_coords, job_coords).kilometers
                    
                    # Convertir la distance en score (plus proche = meilleur score)
                    if distance < 10:  # Même ville ou très proche
                        return 0.9
                    elif distance < 30:  # Même agglomération
                        return 0.7
                    elif distance < 100:  # Même région proche
                        return 0.5
                    elif distance < 300:  # Même grande région
                        return 0.3
                    else:  # Trop loin
                        return 0.1
            except Exception as e:
                self.logger.warning(f"Erreur lors du géocodage: {e}")
        
        # Si aucune correspondance n'est trouvée ou si le géocodage échoue
        return 0.1
    
    def _geocode(self, location):
        """
        Géocode une adresse en coordonnées (latitude, longitude).
        
        Args:
            location: Adresse à géocoder
            
        Returns:
            tuple: (latitude, longitude) ou None en cas d'échec
        """
        if not self.geocoder or not location:
            return None
        
        try:
            geocode_result = self.geocoder.geocode(location, exactly_one=True)
            if geocode_result:
                return (geocode_result.latitude, geocode_result.longitude)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            self.logger.warning(f"Erreur de géocodage pour '{location}': {e}")
        except Exception as e:
            self.logger.warning(f"Erreur inattendue lors du géocodage: {e}")
        
        return None
    
    def _extract_salary(self, profile, salary_type):
        """
        Extrait les informations de salaire du profil.
        
        Args:
            profile: Dictionnaire contenant les informations
            salary_type: Type de salaire à extraire (expected, offered, etc.)
            
        Returns:
            dict: Informations de salaire (min, max, currency)
        """
        if not profile:
            return None
        
        salary_info = None
        
        # Champs possibles selon le type de salaire
        if salary_type == "expected":
            fields = ["expected_salary", "salary_expectation", "desired_salary", "salary"]
        else:  # offered
            fields = ["salary", "salary_range", "compensation", "remuneration"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                salary = profile[field]
                if isinstance(salary, dict):
                    # Si le salaire est déjà structuré
                    return {
                        "min": salary.get("min", salary.get("minimum", salary.get("from"))),
                        "max": salary.get("max", salary.get("maximum", salary.get("to"))),
                        "currency": salary.get("currency", "EUR"),
                        "period": salary.get("period", "annual")
                    }
                elif isinstance(salary, str):
                    # Tenter d'extraire les informations de salaire à partir du texte
                    return self._parse_salary_string(salary)
        
        # Si aucune information de salaire n'est trouvée
        return None
    
    def _parse_salary_string(self, salary_str):
        """
        Analyse une chaîne de caractères contenant des informations de salaire.
        
        Args:
            salary_str: Chaîne contenant des informations de salaire
            
        Returns:
            dict: Informations de salaire extraites
        """
        if not salary_str:
            return None
        
        salary_info = {"min": None, "max": None, "currency": "EUR", "period": "annual"}
        
        # Détecter la devise
        currency_patterns = {
            "EUR": [r'€', r'eur', r'euro', r'euros'],
            "USD": [r'\$', r'usd', r'dollar', r'dollars'],
            "GBP": [r'£', r'gbp', r'pound', r'pounds', r'livre', r'livres'],
            "CHF": [r'chf', r'franc', r'francs']
        }
        
        for currency, patterns in currency_patterns.items():
            if any(re.search(pattern, salary_str.lower()) for pattern in patterns):
                salary_info["currency"] = currency
                break
        
        # Détecter la période
        period_patterns = {
            "annual": [r'an', r'année', r'annual', r'annuel', r'par an', r'par année', r'/an', r'/a', r'/year', r'/y', r'year', r'yearly'],
            "monthly": [r'mois', r'month', r'mensuel', r'par mois', r'/mois', r'/m', r'/month', r'monthly'],
            "daily": [r'jour', r'day', r'journalier', r'par jour', r'/jour', r'/j', r'/day', r'daily'],
            "hourly": [r'heure', r'hour', r'horaire', r'par heure', r'/heure', r'/h', r'/hour', r'hourly']
        }
        
        for period, patterns in period_patterns.items():
            if any(re.search(pattern, salary_str.lower()) for pattern in patterns):
                salary_info["period"] = period
                break
        
        # Extraire les montants
        numbers = re.findall(r'(\d+[.,]?\d*)', salary_str.replace(' ', ''))
        if len(numbers) >= 2:
            # Supposer que les deux premiers nombres sont min et max
            salary_info["min"] = float(numbers[0].replace(',', '.'))
            salary_info["max"] = float(numbers[1].replace(',', '.'))
            
            # Vérifier si les valeurs sont en milliers ou en k
            if salary_info["min"] < 1000 and ("k" in salary_str.lower() or "k€" in salary_str or "k$" in salary_str):
                salary_info["min"] *= 1000
                salary_info["max"] *= 1000
        elif len(numbers) == 1:
            # S'il n'y a qu'un seul nombre, l'utiliser comme valeur min et max
            value = float(numbers[0].replace(',', '.'))
            
            # Vérifier si la valeur est en milliers ou en k
            if value < 1000 and ("k" in salary_str.lower() or "k€" in salary_str or "k$" in salary_str):
                value *= 1000
                
            salary_info["min"] = value
            salary_info["max"] = value
        
        # Normaliser à une base annuelle pour les comparaisons
        if salary_info["min"] is not None and salary_info["max"] is not None:
            if salary_info["period"] == "monthly":
                salary_info["min"] *= 12
                salary_info["max"] *= 12
            elif salary_info["period"] == "daily":
                salary_info["min"] *= 220  # environ 220 jours travaillés par an
                salary_info["max"] *= 220
            elif salary_info["period"] == "hourly":
                salary_info["min"] *= 1600  # environ 1600 heures par an
                salary_info["max"] *= 1600
            
            # Conversion en euros si nécessaire (taux approximatifs)
            if salary_info["currency"] == "USD":
                salary_info["min"] *= 0.85
                salary_info["max"] *= 0.85
            elif salary_info["currency"] == "GBP":
                salary_info["min"] *= 1.15
                salary_info["max"] *= 1.15
            elif salary_info["currency"] == "CHF":
                salary_info["min"] *= 0.95
                salary_info["max"] *= 0.95
            
            # Normaliser la devise en EUR pour la comparaison
            salary_info["currency"] = "EUR"
            salary_info["period"] = "annual"
            
            return salary_info
        
        return None
    
    def _extract_job_category(self, job_profile):
        """
        Détermine la catégorie de poste (tech, marketing, etc.).
        
        Args:
            job_profile: Profil du poste
            
        Returns:
            str: Catégorie du poste
        """
        if not job_profile:
            return "default"
        
        # Catégories et mots-clés associés
        categories = {
            "tech": ["développeur", "developer", "ingénieur", "engineer", "programmeur", "programmer", 
                    "informatique", "it ", "frontend", "front-end", "backend", "back-end", "fullstack", 
                    "data", "devops", "sre", "système", "system", "réseau", "network", "cloud", "web",
                    "mobile", "software", "logiciel", "tech", "technical", "cybersecurity"],
            
            "marketing": ["marketing", "communication", "digital", "seo", "sea", "sem", "content",
                         "contenu", "social media", "réseaux sociaux", "brand", "marque", "growth",
                         "acquisition", "crm", "marketing", "commercial", "adwords", "analytics"],
            
            "sales": ["commercial", "sales", "vente", "account", "business", "développement", 
                     "développeur d'affaires", "business developer", "commercial", "account manager", 
                     "client", "customer", "adc", "bdr", "sdr"],
            
            "finance": ["finance", "comptable", "comptabilité", "accounting", "financial", "financier",
                      "contrôleur", "controller", "trésorier", "treasurer", "audit", "auditeur", "auditor"],
            
            "hr": ["rh", "hr", "ressources humaines", "human resources", "recrutement", "recruitment",
                 "talent", "paie", "payroll", "formation", "training", "développement rh"]
        }
        
        # Construire un texte avec les champs importants
        job_text = ""
        for field in ["title", "description", "requirements", "skills", "department"]:
            if field in job_profile and isinstance(job_profile[field], str):
                job_text += " " + job_profile[field].lower()
            elif field in job_profile and isinstance(job_profile[field], list):
                job_text += " " + " ".join([str(item) for item in job_profile[field]])
        
        # Détecter la catégorie
        best_category = "default"
        best_score = 0
        
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', job_text.lower()))
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def _extract_experience_level(self, profile):
        """
        Détermine le niveau d'expérience du candidat.
        
        Args:
            profile: Profil du candidat
            
        Returns:
            str: Niveau d'expérience (junior, mid, senior, executive)
        """
        if not profile:
            return "mid"  # Valeur par défaut
        
        # Essayer d'extraire les années d'expérience
        experience_years = None
        for field in ["years_of_experience", "experience_years", "years_experience", "experience"]:
            if field in profile:
                value = profile[field]
                if isinstance(value, (int, float)):
                    experience_years = value
                elif isinstance(value, str) and re.search(r'\d+', value):
                    # Extraire le premier nombre trouvé
                    match = re.search(r'(\d+)', value)
                    if match:
                        experience_years = int(match.group(1))
                break
        
        # Si nous avons trouvé les années d'expérience
        if experience_years is not None:
            if experience_years < 3:
                return "junior"
            elif experience_years < 7:
                return "mid"
            elif experience_years < 15:
                return "senior"
            else:
                return "executive"
        
        # Sinon, chercher des mots-clés dans le titre ou l'expérience
        text = ""
        for field in ["title", "current_position", "experience", "profile"]:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    text += " " + value.lower()
                elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                    text += " " + " ".join(value).lower()
                elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    for item in value:
                        for k, v in item.items():
                            if isinstance(v, str):
                                text += " " + v.lower()
        
        # Vérifier les mots-clés
        if any(kw in text for kw in ["junior", "débutant", "stagiaire", "stage", "intern", "entry level", "entry-level"]):
            return "junior"
        elif any(kw in text for kw in ["senior", "lead", "principal", "chef", "responsable", "head"]):
            return "senior"
        elif any(kw in text for kw in ["directeur", "director", "executive", "vp", "chief", "cto", "ceo", "cfo", "coo"]):
            return "executive"
        
        # Par défaut, retourner un niveau intermédiaire
        return "mid"
    
    def calculate_salary_match(self, candidate_salary, job_salary, job_category, experience_level):
        """
        Calcule la compatibilité entre le salaire souhaité et le salaire proposé.
        
        Args:
            candidate_salary: Informations sur le salaire souhaité
            job_salary: Informations sur le salaire proposé
            job_category: Catégorie du poste
            experience_level: Niveau d'expérience du candidat
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        # Si l'une des informations est manquante, utiliser des estimations basées sur la catégorie et l'expérience
        if not candidate_salary and not job_salary:
            return 0.5  # Valeur neutre
        
        # Si l'un des deux est manquant, utiliser les fourchettes typiques
        salary_ranges = self.salary_ranges.get(experience_level, self.salary_ranges["mid"])
        category_ranges = salary_ranges.get(job_category, salary_ranges["default"])
        
        if not candidate_salary:
            candidate_min = category_ranges["min"]
            candidate_max = category_ranges["max"]
        else:
            candidate_min = candidate_salary.get("min", category_ranges["min"])
            candidate_max = candidate_salary.get("max", candidate_salary.get("min", category_ranges["max"]))
        
        if not job_salary:
            job_min = category_ranges["min"]
            job_max = category_ranges["max"]
        else:
            job_min = job_salary.get("min", category_ranges["min"])
            job_max = job_salary.get("max", job_salary.get("min", category_ranges["max"]))
        
        # Calculer le chevauchement des fourchettes de salaire
        # Si les intervalles ne se chevauchent pas
        if candidate_min > job_max:
            # Le candidat veut plus que ce que l'entreprise propose (max)
            return max(0.1, 1 - min(1, (candidate_min - job_max) / job_max))
        elif job_min > candidate_max:
            # L'entreprise offre plus que ce que le candidat demande (max)
            return 0.9  # Bon pour le candidat
        else:
            # Les intervalles se chevauchent
            overlap_min = max(candidate_min, job_min)
            overlap_max = min(candidate_max, job_max)
            overlap_size = overlap_max - overlap_min
            
            candidate_range = candidate_max - candidate_min
            job_range = job_max - job_min
            
            # Si l'une des plages est de taille nulle (valeur unique)
            if candidate_range == 0:
                candidate_range = 0.01 * candidate_min
            if job_range == 0:
                job_range = 0.01 * job_min
                
            # Calculer le pourcentage de chevauchement
            overlap_ratio = overlap_size / max(candidate_range, job_range)
            
            # Si le salaire du candidat est dans la fourchette du poste
            if candidate_min >= job_min and candidate_max <= job_max:
                return min(1.0, 0.7 + 0.3 * overlap_ratio)
            # Si le salaire du poste est dans la fourchette du candidat
            elif job_min >= candidate_min and job_max <= candidate_max:
                return min(1.0, 0.7 + 0.3 * overlap_ratio)
            # Si le salaire du candidat est partiellement dans la fourchette
            else:
                return min(0.9, 0.5 + 0.4 * overlap_ratio)
    
    def _extract_work_mode(self, profile, mode_type):
        """
        Extrait le mode de travail (présentiel, télétravail, hybride).
        
        Args:
            profile: Dictionnaire contenant les informations
            mode_type: Type de mode à extraire (preferred, offered)
            
        Returns:
            str: Mode de travail
        """
        if not profile:
            return None
        
        # Champs possibles selon le type
        if mode_type == "preferred":
            fields = ["preferred_work_mode", "work_mode", "work_type", "work_preference"]
        else:  # offered
            fields = ["work_mode", "location_type", "work_type", "remote_policy"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    return self._normalize_work_mode(value)
        
        # Rechercher dans d'autres champs
        text = ""
        search_fields = ["description", "benefits", "perks"] if mode_type == "offered" else ["about", "preferences"]
        
        for field in search_fields:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_work_mode_from_text(text)
        
        return None
    
    def _normalize_work_mode(self, mode):
        """
        Normalise le mode de travail dans un format standard.
        
        Args:
            mode: Chaîne décrivant le mode de travail
            
        Returns:
            str: Mode de travail normalisé ('remote', 'hybrid', 'office')
        """
        if not mode:
            return None
            
        mode_lower = mode.lower()
        
        for standard_mode, keywords in self.work_mode_mapping.items():
            if any(kw in mode_lower for kw in keywords):
                return standard_mode
        
        return None
    
    def _extract_work_mode_from_text(self, text):
        """
        Extrait le mode de travail à partir d'un texte.
        
        Args:
            text: Texte décrivant le poste ou les préférences
            
        Returns:
            str: Mode de travail
        """
        # Compter les occurrences de chaque catégorie
        scores = {mode: 0 for mode in self.work_mode_mapping}
        
        for mode, keywords in self.work_mode_mapping.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text.lower()):
                    scores[mode] += 1
        
        # Identifier le mode avec le score le plus élevé
        best_mode = max(scores.items(), key=lambda x: x[1])
        
        # Retourner le mode s'il y a des correspondances
        if best_mode[1] > 0:
            return best_mode[0]
        
        return None
    
    def calculate_work_mode_match(self, candidate_mode, job_mode):
        """
        Calcule la compatibilité entre les modes de travail.
        
        Args:
            candidate_mode: Mode de travail préféré du candidat
            job_mode: Mode de travail proposé par le poste
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_mode or not job_mode:
            return 0.5  # Valeur neutre
        
        # Créer une matrice de compatibilité
        compatibility = {
            "remote": {"remote": 1.0, "hybrid": 0.7, "office": 0.2},
            "hybrid": {"remote": 0.7, "hybrid": 1.0, "office": 0.7},
            "office": {"office": 1.0, "hybrid": 0.7, "remote": 0.2}
        }
        
        # Récupérer le score de compatibilité
        if candidate_mode in compatibility and job_mode in compatibility[candidate_mode]:
            return compatibility[candidate_mode][job_mode]
        
        return 0.5  # Valeur par défaut
    
    def _extract_contract_type(self, profile, type_name):
        """
        Extrait le type de contrat (CDI, CDD, etc.).
        
        Args:
            profile: Dictionnaire contenant les informations
            type_name: Type de contrat à extraire (preferred, offered)
            
        Returns:
            str: Type de contrat normalisé
        """
        if not profile:
            return None
            
        # Champs possibles selon le type
        if type_name == "preferred":
            fields = ["preferred_contract", "contract_type", "employment_type"]
        else:  # offered
            fields = ["contract_type", "employment_type", "contract"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    return self._normalize_contract_type(value)
        
        # Rechercher dans d'autres champs
        text = ""
        search_fields = ["description", "details"] if type_name == "offered" else ["about", "preferences"]
        
        for field in search_fields:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_contract_type_from_text(text)
        
        return None
    
    def _normalize_contract_type(self, contract_type):
        """
        Normalise le type de contrat dans un format standard.
        
        Args:
            contract_type: Chaîne décrivant le type de contrat
            
        Returns:
            str: Type de contrat normalisé
        """
        if not contract_type:
            return None
            
        contract_lower = contract_type.lower()
        
        for standard_type, keywords in self.contract_type_mapping.items():
            if any(kw in contract_lower for kw in keywords):
                return standard_type
        
        return None
    
    def _extract_contract_type_from_text(self, text):
        """
        Extrait le type de contrat à partir d'un texte.
        
        Args:
            text: Texte décrivant le poste ou les préférences
            
        Returns:
            str: Type de contrat
        """
        # Compter les occurrences de chaque type
        scores = {contract_type: 0 for contract_type in self.contract_type_mapping}
        
        for contract_type, keywords in self.contract_type_mapping.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text.lower()):
                    scores[contract_type] += 1
        
        # Identifier le type avec le score le plus élevé
        best_type = max(scores.items(), key=lambda x: x[1])
        
        # Retourner le type s'il y a des correspondances
        if best_type[1] > 0:
            return best_type[0]
        
        return None
    
    def calculate_contract_type_match(self, candidate_type, job_type):
        """
        Calcule la compatibilité entre les types de contrat.
        
        Args:
            candidate_type: Type de contrat préféré par le candidat
            job_type: Type de contrat proposé par le poste
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_type or not job_type:
            return 0.5  # Valeur neutre
        
        # Matrice de compatibilité
        compatibility = {
            "permanent": {"permanent": 1.0, "temporary": 0.3, "freelance": 0.2, "internship": 0.1, "apprenticeship": 0.2, "part_time": 0.4, "interim": 0.2},
            "temporary": {"permanent": 0.7, "temporary": 1.0, "freelance": 0.5, "internship": 0.3, "apprenticeship": 0.3, "part_time": 0.6, "interim": 0.7},
            "freelance": {"permanent": 0.4, "temporary": 0.5, "freelance": 1.0, "internship": 0.1, "apprenticeship": 0.1, "part_time": 0.7, "interim": 0.6},
            "internship": {"permanent": 0.6, "temporary": 0.6, "freelance": 0.2, "internship": 1.0, "apprenticeship": 0.8, "part_time": 0.5, "interim": 0.3},
            "apprenticeship": {"permanent": 0.6, "temporary": 0.5, "freelance": 0.2, "internship": 0.7, "apprenticeship": 1.0, "part_time": 0.5, "interim": 0.3},
            "part_time": {"permanent": 0.5, "temporary": 0.6, "freelance": 0.7, "internship": 0.5, "apprenticeship": 0.5, "part_time": 1.0, "interim": 0.7},
            "interim": {"permanent": 0.3, "temporary": 0.7, "freelance": 0.6, "internship": 0.3, "apprenticeship": 0.3, "part_time": 0.7, "interim": 1.0}
        }
        
        # Récupérer le score de compatibilité
        if candidate_type in compatibility and job_type in compatibility[candidate_type]:
            return compatibility[candidate_type][job_type]
        
        return 0.5  # Valeur par défaut
    
    def _extract_company_size(self, profile, size_type):
        """
        Extrait la taille d'entreprise préférée ou réelle.
        
        Args:
            profile: Dictionnaire contenant les informations
            size_type: Type de taille à extraire (preferred, actual)
            
        Returns:
            str: Taille d'entreprise normalisée
        """
        if not profile:
            return None
            
        # Champs possibles selon le type
        if size_type == "preferred":
            fields = ["preferred_company_size", "company_size", "desired_company_size"]
        else:  # actual
            fields = ["company_size", "size", "employees"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    return self._normalize_company_size(value)
                elif isinstance(value, (int, float)):
                    return self._normalize_company_size_from_number(value)
        
        # Rechercher dans d'autres champs
        text = ""
        search_fields = ["company_description", "about_company"] if size_type == "actual" else ["preferences", "about"]
        
        for field in search_fields:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_company_size_from_text(text)
        
        return None
    
    def _normalize_company_size(self, size):
        """
        Normalise la taille de l'entreprise dans un format standard.
        
        Args:
            size: Chaîne décrivant la taille de l'entreprise
            
        Returns:
            str: Taille normalisée ('startup', 'small', 'medium', 'large')
        """
        if not size:
            return None
            
        size_lower = size.lower()
        
        # Vérifier les correspondances directes
        for standard_size, keywords in self.company_size_mapping.items():
            if any(kw in size_lower for kw in keywords):
                return standard_size
        
        # Essayer d'extraire un nombre
        match = re.search(r'(\d+)[\s-]*(\d*)', size_lower)
        if match:
            min_size = int(match.group(1))
            max_size = int(match.group(2)) if match.group(2) else min_size
            
            # Utiliser la moyenne si une plage est fournie
            avg_size = (min_size + max_size) / 2
            return self._normalize_company_size_from_number(avg_size)
        
        return None
    
    def _normalize_company_size_from_number(self, num_employees):
        """
        Normalise la taille de l'entreprise en fonction du nombre d'employés.
        
        Args:
            num_employees: Nombre d'employés
            
        Returns:
            str: Taille normalisée ('startup', 'small', 'medium', 'large')
        """
        if num_employees < 20:
            return "startup"
        elif num_employees < 100:
            return "small"
        elif num_employees < 1000:
            return "medium"
        else:
            return "large"
    
    def _extract_company_size_from_text(self, text):
        """
        Extrait la taille de l'entreprise à partir d'un texte.
        
        Args:
            text: Texte décrivant l'entreprise ou les préférences
            
        Returns:
            str: Taille de l'entreprise
        """
        # Compter les occurrences de chaque type
        scores = {size: 0 for size in self.company_size_mapping}
        
        for size, keywords in self.company_size_mapping.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text.lower()):
                    scores[size] += 1
        
        # Identifier le type avec le score le plus élevé
        best_size = max(scores.items(), key=lambda x: x[1])
        
        # Retourner le type s'il y a des correspondances
        if best_size[1] > 0:
            return best_size[0]
        
        # Chercher des nombres d'employés
        for match in re.finditer(r'(\d+)[\s\-]*(\d*)\s*(personnes|salariés|employés|collaborateurs|employees|staff|people)', text.lower()):
            min_size = int(match.group(1))
            max_size = int(match.group(2)) if match.group(2) else min_size
            avg_size = (min_size + max_size) / 2
            return self._normalize_company_size_from_number(avg_size)
        
        return None
    
    def calculate_company_size_match(self, candidate_size, company_size):
        """
        Calcule la compatibilité entre les tailles d'entreprise.
        
        Args:
            candidate_size: Taille d'entreprise préférée par le candidat
            company_size: Taille réelle de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_size or not company_size:
            return 0.5  # Valeur neutre
        
        # Matrice de compatibilité
        compatibility = {
            "startup": {"startup": 1.0, "small": 0.8, "medium": 0.4, "large": 0.2},
            "small": {"startup": 0.7, "small": 1.0, "medium": 0.7, "large": 0.3},
            "medium": {"startup": 0.3, "medium": 1.0, "small": 0.7, "large": 0.7},
            "large": {"startup": 0.2, "small": 0.3, "medium": 0.7, "large": 1.0}
        }
        
        # Récupérer le score de compatibilité
        if candidate_size in compatibility and company_size in compatibility[candidate_size]:
            return compatibility[candidate_size][company_size]
        
        return 0.5  # Valeur par défaut
        
    def _extract_work_environment(self, profile, env_type, type_name):
        """
        Extrait les préférences d'environnement de travail.
        
        Args:
            profile: Dictionnaire contenant les informations
            env_type: Type d'environnement (pace, formality, hierarchy, management)
            type_name: Type de préférence (preferred ou actual)
            
        Returns:
            str: Préférence d'environnement normalisée
        """
        if not profile or not env_type or env_type not in self.work_environment_mapping:
            return None
            
        # Champs possibles selon le type
        if type_name == "preferred":
            fields = ["preferred_environment", "work_preferences", "environment_preferences"]
        else:  # actual
            fields = ["work_environment", "environment", "culture", "company_culture"]
        
        # Vérifier d'abord les structures imbriquées
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, dict) and env_type in value:
                    return self._normalize_work_environment(value[env_type], env_type)
        
        # Chercher dans les champs généraux
        text = ""
        for field in fields + ["description", "about"]:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_work_environment_from_text(text, env_type)
        
        return None
    
    def _normalize_work_environment(self, value, env_type):
        """
        Normalise une valeur d'environnement de travail.
        
        Args:
            value: Valeur à normaliser
            env_type: Type d'environnement
            
        Returns:
            str: Valeur normalisée
        """
        if not value or not env_type or env_type not in self.work_environment_mapping:
            return None
            
        value_lower = value.lower()
        
        # Vérifier les correspondances directes
        for standard_value, keywords in self.work_environment_mapping[env_type].items():
            if any(kw in value_lower for kw in keywords):
                return standard_value
        
        return None
    
    def _extract_work_environment_from_text(self, text, env_type):
        """
        Extrait une préférence d'environnement de travail à partir d'un texte.
        
        Args:
            text: Texte décrivant l'environnement ou les préférences
            env_type: Type d'environnement
            
        Returns:
            str: Valeur d'environnement
        """
        if not text or not env_type or env_type not in self.work_environment_mapping:
            return None
            
        # Compter les occurrences de chaque valeur
        scores = {value: 0 for value in self.work_environment_mapping[env_type]}
        
        for value, keywords in self.work_environment_mapping[env_type].items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text.lower()):
                    scores[value] += 1
        
        # Identifier la valeur avec le score le plus élevé
        best_value = max(scores.items(), key=lambda x: x[1])
        
        # Retourner la valeur s'il y a des correspondances
        if best_value[1] > 0:
            return best_value[0]
        
        return None
    
    def calculate_work_environment_match(self, candidate_pref, company_env):
        """
        Calcule la compatibilité entre les préférences d'environnement de travail.
        
        Args:
            candidate_pref: Préférence d'environnement du candidat
            company_env: Environnement de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_pref or not company_env:
            return 0.5  # Valeur neutre
        
        # Compatibilité simple: 1.0 si identique, 0.5 sinon
        if candidate_pref == company_env:
            return 1.0
        else:
            # Pour certaines combinaisons, la compatibilité peut être moyenne
            if (candidate_pref in ["balanced", "medium"] or 
                company_env in ["balanced", "medium"]):
                return 0.7
            
            return 0.3
    
    def _extract_industry(self, profile, type_name):
        """
        Extrait le secteur d'activité préféré ou réel.
        
        Args:
            profile: Dictionnaire contenant les informations
            type_name: Type (preferred, company)
            
        Returns:
            str ou list: Secteur(s) d'activité
        """
        if not profile:
            return None
            
        # Champs possibles selon le type
        if type_name == "preferred":
            fields = ["preferred_industry", "industry_preference", "sectors"]
        else:  # company
            fields = ["industry", "sector", "business_sector", "domain"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    return self._normalize_industry(value)
                elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                    return [self._normalize_industry(item) for item in value if self._normalize_industry(item)]
        
        # Rechercher dans d'autres champs
        text = ""
        search_fields = ["description", "about", "company_description"] if type_name == "company" else ["preferences", "about"]
        
        for field in search_fields:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_industry_from_text(text)
        
        return None
    
    def _normalize_industry(self, industry):
        """
        Normalise un secteur d'activité.
        
        Args:
            industry: Chaîne décrivant le secteur
            
        Returns:
            str: Secteur normalisé
        """
        if not industry:
            return None
            
        industry_lower = industry.lower()
        
        for standard_industry, keywords in self.industry_mapping.items():
            if any(kw in industry_lower for kw in keywords):
                return standard_industry
        
        return None
    
    def _extract_industry_from_text(self, text):
        """
        Extrait les secteurs d'activité à partir d'un texte.
        
        Args:
            text: Texte décrivant l'entreprise ou les préférences
            
        Returns:
            list: Liste des secteurs identifiés
        """
        if not text:
            return None
            
        # Compter les occurrences de chaque secteur
        scores = {industry: 0 for industry in self.industry_mapping}
        
        for industry, keywords in self.industry_mapping.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text.lower())
                scores[industry] += len(matches)
        
        # Filtrer les secteurs avec des correspondances
        found_industries = [industry for industry, score in scores.items() if score > 0]
        
        if found_industries:
            return found_industries
        
        return None
    
    def calculate_industry_match(self, candidate_industries, company_industries):
        """
        Calcule la compatibilité entre les secteurs d'activité.
        
        Args:
            candidate_industries: Secteurs préférés du candidat
            company_industries: Secteurs de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_industries or not company_industries:
            return 0.5  # Valeur neutre
        
        # Normaliser en listes
        if isinstance(candidate_industries, str):
            candidate_industries = [candidate_industries]
        if isinstance(company_industries, str):
            company_industries = [company_industries]
        
        # Compter les correspondances
        matches = sum(1 for ind in candidate_industries if ind in company_industries)
        
        if not matches:
            return 0.2  # Pas de correspondance
        
        # Calculer le score en fonction du nombre de correspondances
        max_possible = min(len(candidate_industries), len(company_industries))
        return min(1.0, 0.5 + (matches / max_possible) * 0.5)
    
    def _extract_travel_willingness(self, profile):
        """
        Extrait la volonté de déplacement du candidat.
        
        Args:
            profile: Profil du candidat
            
        Returns:
            str: Niveau de volonté de déplacement
        """
        if not profile:
            return None
            
        # Champs possibles
        fields = ["travel_willingness", "willing_to_travel", "travel_preference", "mobility"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str):
                    return self._normalize_travel_willingness(value)
                elif isinstance(value, (int, float)):
                    # Si c'est un pourcentage
                    return self._normalize_travel_percentage(value)
        
        # Rechercher dans d'autres champs
        text = ""
        for field in ["about", "preferences", "mobility"]:
            if field in profile and isinstance(profile[field], str):
                text += profile[field].lower() + " "
        
        if text:
            return self._extract_travel_willingness_from_text(text)
        
        return None
    
    def _normalize_travel_willingness(self, willingness):
        """
        Normalise la volonté de déplacement.
        
        Args:
            willingness: Chaîne décrivant la volonté de déplacement
            
        Returns:
            str: Niveau normalisé (none, low, medium, high)
        """
        if not willingness:
            return None
            
        willingness_lower = willingness.lower()
        
        # Chercher des mots-clés
        if any(kw in willingness_lower for kw in ["no", "non", "aucun", "pas", "jamais", "0%"]):
            return "none"
        elif any(kw in willingness_lower for kw in ["peu", "faible", "minimal", "occasionnel", "rare", "low", "little", "<25%", "< 25%", "moins de 25%"]):
            return "low"
        elif any(kw in willingness_lower for kw in ["moyen", "medium", "modéré", "occasionnel", "25-50%", "25%-50%", "25 à 50%"]):
            return "medium"
        elif any(kw in willingness_lower for kw in ["élevé", "high", "fréquent", "frequent", "souvent", "often", ">50%", "> 50%", "plus de 50%"]):
            return "high"
        
        # Chercher un pourcentage
        match = re.search(r'(\d+)%', willingness_lower)
        if match:
            percentage = int(match.group(1))
            return self._normalize_travel_percentage(percentage)
        
        return None
    
    def _normalize_travel_percentage(self, percentage):
        """
        Normalise un pourcentage de déplacement.
        
        Args:
            percentage: Pourcentage de déplacement
            
        Returns:
            str: Niveau normalisé (none, low, medium, high)
        """
        if percentage == 0:
            return "none"
        elif percentage < 25:
            return "low"
        elif percentage < 50:
            return "medium"
        else:
            return "high"
    
    def _extract_travel_willingness_from_text(self, text):
        """
        Extrait la volonté de déplacement à partir d'un texte.
        
        Args:
            text: Texte décrivant les préférences
            
        Returns:
            str: Niveau de volonté de déplacement
        """
        if not text:
            return None
            
        # Chercher des mots-clés
        if re.search(r'\b(pas de (déplacement|voyage)|aucun (déplacement|voyage)|no travel|sans (déplacement|voyage))\b', text.lower()):
            return "none"
        elif re.search(r'\b(peu( de)? (déplacement|voyage)|occasionnel|rare|low travel|déplacement rare)\b', text.lower()):
            return "low"
        elif re.search(r'\b(déplacement|voyage)s?\s+(occasionnel|modéré|moyen|ponctuel|régulier)\b', text.lower()) or re.search(r'\b(medium|moderate) travel\b', text.lower()):
            return "medium"
        elif re.search(r'\b((beaucoup|nombreux|fréquent)s? (déplacement|voyage)s?|voyager (souvent|beaucoup|fréquemment)|high travel|frequent travel)\b', text.lower()):
            return "high"
        
        # Chercher un pourcentage
        match = re.search(r'(\d+)%\s*(de|du temps)?\s*(voyage|déplacement|travel)', text.lower())
        if match:
            percentage = int(match.group(1))
            return self._normalize_travel_percentage(percentage)
        
        return None
    
    def _extract_travel_requirements(self, job_profile):
        """
        Extrait les exigences de déplacement d'un poste.
        
        Args:
            job_profile: Profil du poste
            
        Returns:
            str: Niveau d'exigence de déplacement
        """
        if not job_profile:
            return None
            
        # Champs possibles
        fields = ["travel", "travel_requirements", "deplacements", "mobility"]
        
        # Chercher dans les champs appropriés
        for field in fields:
            if field in job_profile:
                value = job_profile[field]
                if isinstance(value, str):
                    return self._normalize_travel_willingness(value)
                elif isinstance(value, (int, float)):
                    return self._normalize_travel_percentage(value)
        
        # Rechercher dans d'autres champs
        text = ""
        for field in ["description", "job_description", "requirements"]:
            if field in job_profile and isinstance(job_profile[field], str):
                text += job_profile[field].lower() + " "
        
        if text:
            return self._extract_travel_willingness_from_text(text)
        
        return None
    
    def calculate_travel_match(self, candidate_willingness, job_requirement):
        """
        Calcule la compatibilité entre la volonté de déplacement et les exigences.
        
        Args:
            candidate_willingness: Volonté de déplacement du candidat
            job_requirement: Exigences de déplacement du poste
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_willingness or not job_requirement:
            return 0.5  # Valeur neutre
        
        # Matrice de compatibilité
        compatibility = {
            "none": {"none": 1.0, "low": 0.5, "medium": 0.1, "high": 0.0},
            "low": {"none": 1.0, "low": 1.0, "medium": 0.6, "high": 0.2},
            "medium": {"none": 1.0, "low": 1.0, "medium": 1.0, "high": 0.7},
            "high": {"none": 1.0, "low": 1.0, "medium": 1.0, "high": 1.0}
        }
        
        # Récupérer le score de compatibilité
        if candidate_willingness in compatibility and job_requirement in compatibility[candidate_willingness]:
            return compatibility[candidate_willingness][job_requirement]
        
        return 0.5  # Valeur par défaut
