"""
Générateur de features d'alignement culturel et de valeurs.
"""

import json
import logging
import re
from pathlib import Path
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class CulturalAlignmentGenerator:
    """
    Générateur de features pour l'alignement culturel et des valeurs.
    """
    
    def __init__(self, values_taxonomy_path=None, embeddings_model="paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialise le générateur de features d'alignement culturel.
        
        Args:
            values_taxonomy_path: Chemin vers le fichier JSON de taxonomie des valeurs
            embeddings_model: Nom du modèle Sentence-BERT pour les embeddings
        """
        self.logger = logging.getLogger(__name__)
        
        # Chargement de la taxonomie des valeurs
        self.values_taxonomy = self._load_values_taxonomy(values_taxonomy_path)
        
        # Initialisation du vectoriseur TF-IDF
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85,
            stop_words=['french', 'english'],
            use_idf=True
        )
        
        # Initialisation du modèle d'embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer(embeddings_model)
                self.embeddings_available = True
            except Exception as e:
                self.logger.warning(f"Impossible de charger le modèle d'embeddings: {e}")
                self.embeddings_available = False
        else:
            self.logger.warning("Package sentence-transformers non disponible. Fonctionnalités d'embedding désactivées.")
            self.embeddings_available = False
        
        # Charger spaCy pour le traitement du texte
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except:
            self.logger.warning("Modèle fr_core_news_md non trouvé, chargement du modèle plus petit.")
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except:
                self.logger.error("Aucun modèle spaCy disponible.")
                self.nlp = None
    
    def _load_values_taxonomy(self, taxonomy_path):
        """
        Charge la taxonomie des valeurs d'entreprise et personnelles.
        
        Args:
            taxonomy_path: Chemin vers le fichier JSON de taxonomie
            
        Returns:
            Dict: Taxonomie des valeurs
        """
        # Chemin par défaut si non spécifié
        if not taxonomy_path:
            taxonomy_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "company_values_taxonomy.json"
        
        try:
            if Path(taxonomy_path).exists():
                with open(taxonomy_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Taxonomie de base si le fichier n'existe pas
                self.logger.warning(f"Fichier de taxonomie {taxonomy_path} non trouvé. Utilisation de la taxonomie par défaut.")
                return self._create_default_taxonomy(taxonomy_path)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la taxonomie: {e}")
            return {}
    
    def _create_default_taxonomy(self, taxonomy_path=None):
        """
        Crée une taxonomie de valeurs par défaut.
        
        Args:
            taxonomy_path: Chemin où sauvegarder la taxonomie par défaut
            
        Returns:
            Dict: Taxonomie par défaut
        """
        # Structure de base pour une taxonomie des valeurs
        default_taxonomy = {
            "innovation": {
                "synonyms": ["créativité", "originalité", "avant-garde", "disruption", "pionnier"],
                "related_terms": ["recherche", "développement", "progrès", "expérimentation", "idées"],
                "indicators": ["penser différemment", "créer", "inventer", "disrupter", "transformer"],
                "category": "growth"
            },
            "excellence": {
                "synonyms": ["qualité", "performance", "perfection", "rigueur"],
                "related_terms": ["standard élevé", "amélioration continue", "exigence", "précision"],
                "indicators": ["dépasser", "exceller", "améliorer", "optimiser", "perfectionner"],
                "category": "performance"
            },
            "collaboration": {
                "synonyms": ["coopération", "travail d'équipe", "synergie", "partenariat"],
                "related_terms": ["ensemble", "collectif", "partage", "entraide", "solidarité"],
                "indicators": ["travailler ensemble", "partager", "s'entraider", "coopérer", "unir"],
                "category": "relationships"
            },
            "intégrité": {
                "synonyms": ["honnêteté", "éthique", "transparence", "droiture", "loyauté"],
                "related_terms": ["confiance", "respect", "valeurs", "principes", "morale"],
                "indicators": ["agir avec éthique", "être transparent", "respecter", "être honnête"],
                "category": "ethics"
            },
            "responsabilité": {
                "synonyms": ["engagement", "devoir", "fiabilité", "imputabilité"],
                "related_terms": ["assumer", "obligation", "conséquence", "promesse"],
                "indicators": ["s'engager", "assumer", "prendre en charge", "répondre de", "garantir"],
                "category": "ethics"
            },
            "diversité": {
                "synonyms": ["inclusion", "pluralité", "variété", "multiculturalisme"],
                "related_terms": ["différence", "tolérance", "ouverture", "égalité", "accessibilité"],
                "indicators": ["inclure", "respecter les différences", "valoriser la diversité", "promouvoir l'égalité"],
                "category": "social"
            },
            "client": {
                "synonyms": ["service client", "orientation client", "satisfaction client"],
                "related_terms": ["expérience", "besoin", "attente", "relation", "fidélité"],
                "indicators": ["satisfaire", "écouter", "servir", "répondre aux besoins"],
                "category": "business"
            },
            "agilité": {
                "synonyms": ["flexibilité", "adaptabilité", "réactivité", "souplesse"],
                "related_terms": ["changement", "évolution", "adaptation", "transformation"],
                "indicators": ["s'adapter", "évoluer", "pivoter", "réagir rapidement"],
                "category": "growth"
            },
            "durabilité": {
                "synonyms": ["développement durable", "écologie", "responsabilité environnementale"],
                "related_terms": ["environnement", "écosystème", "impact", "planète", "futur"],
                "indicators": ["préserver", "recycler", "réduire l'impact", "protéger"],
                "category": "social"
            },
            "passion": {
                "synonyms": ["enthousiasme", "motivation", "énergie", "engagement"],
                "related_terms": ["dévouement", "ardeur", "zèle", "ferveur", "conviction"],
                "indicators": ["s'enthousiasmer", "se passionner", "s'investir", "être motivé"],
                "category": "personal"
            },
            "apprentissage": {
                "synonyms": ["développement", "formation", "croissance", "éducation"],
                "related_terms": ["compétence", "savoir", "connaissance", "progression", "curiosité"],
                "indicators": ["apprendre", "développer", "se former", "progresser", "grandir"],
                "category": "growth"
            },
            "leadership": {
                "synonyms": ["direction", "guidance", "influence", "vision"],
                "related_terms": ["inspiration", "motivation", "stratégie", "exemple", "autorité"],
                "indicators": ["guider", "diriger", "inspirer", "influencer", "motiver"],
                "category": "performance"
            },
            "sécurité": {
                "synonyms": ["protection", "sûreté", "prévention", "vigilance"],
                "related_terms": ["risque", "danger", "précaution", "prudence", "fiabilité"],
                "indicators": ["protéger", "sécuriser", "prévenir", "assurer", "veiller"],
                "category": "stability"
            },
            "autonomie": {
                "synonyms": ["indépendance", "liberté", "initiative", "autodétermination"],
                "related_terms": ["responsabilisation", "confiance", "décision", "choix"],
                "indicators": ["décider", "agir seul", "prendre des initiatives", "être indépendant"],
                "category": "personal"
            },
            "transparence": {
                "synonyms": ["ouverture", "clarté", "honnêteté", "visibilité"],
                "related_terms": ["communication", "information", "vérité", "partage"],
                "indicators": ["communiquer ouvertement", "partager l'information", "être clair"],
                "category": "ethics"
            },
            "ambition": {
                "synonyms": ["détermination", "aspiration", "objectif", "volonté"],
                "related_terms": ["challenge", "défi", "accomplissement", "réussite", "victoire"],
                "indicators": ["défier", "atteindre", "accomplir", "réussir", "gagner"],
                "category": "performance"
            },
            "bien-être": {
                "synonyms": ["santé", "équilibre", "qualité de vie", "harmonie"],
                "related_terms": ["épanouissement", "bonheur", "satisfaction", "confort"],
                "indicators": ["équilibrer", "se sentir bien", "s'épanouir", "prendre soin"],
                "category": "personal"
            },
            "simplicité": {
                "synonyms": ["clarté", "minimalisme", "efficience", "accessibilité"],
                "related_terms": ["facilité", "compréhension", "épuration", "essentiel"],
                "indicators": ["simplifier", "faciliter", "clarifier", "rendre accessible"],
                "category": "stability"
            },
            "respect": {
                "synonyms": ["considération", "estime", "égard", "reconnaissance"],
                "related_terms": ["dignité", "politesse", "courtoisie", "bienveillance"],
                "indicators": ["considérer", "estimer", "reconnaître", "valoriser", "traiter avec égard"],
                "category": "relationships"
            }
        }
        
        # Ajouter les catégories de valeurs
        default_taxonomy["_categories"] = {
            "ethics": "Valeurs éthiques et morales",
            "performance": "Performance et excellence",
            "relationships": "Relations humaines",
            "growth": "Croissance et développement",
            "social": "Impact social et environnemental",
            "business": "Orientation business",
            "personal": "Développement personnel",
            "stability": "Stabilité et sécurité"
        }
        
        # Ajouter les environnements de travail courants
        default_taxonomy["_work_environments"] = {
            "start-up": ["innovation", "agilité", "passion", "collaboration", "autonomie"],
            "corporate": ["excellence", "leadership", "responsabilité", "client", "performance"],
            "public": ["intégrité", "transparence", "service", "respect", "durabilité"],
            "non-profit": ["engagement", "impact", "passion", "communauté", "durabilité"],
            "agency": ["créativité", "réactivité", "client", "collaboration", "qualité"],
            "research": ["innovation", "apprentissage", "rigueur", "autonomie", "excellence"]
        }
        
        # Sauvegarder pour utilisation future si un chemin est spécifié
        if taxonomy_path:
            try:
                # S'assurer que le répertoire parent existe
                Path(taxonomy_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(taxonomy_path, 'w', encoding='utf-8') as f:
                    json.dump(default_taxonomy, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Taxonomie des valeurs par défaut sauvegardée à {taxonomy_path}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la sauvegarde de la taxonomie: {e}")
        
        return default_taxonomy
    
    def generate_cultural_features(self, candidate_profile, company_profile):
        """
        Génère les features d'alignement culturel entre un candidat et une entreprise.
        
        Args:
            candidate_profile: Profil du candidat
            company_profile: Profil de l'entreprise
            
        Returns:
            Dict: Features d'alignement culturel
        """
        features = {}
        
        # Extraction des valeurs explicites et des données culturelles
        candidate_values = self._extract_values(candidate_profile)
        company_values = self._extract_values(company_profile)
        
        candidate_culture_text = self._extract_culture_text(candidate_profile)
        company_culture_text = self._extract_culture_text(company_profile)
        
        # 1. Alignement des valeurs explicites
        features["values_explicit_match"] = self.calculate_values_alignment(
            candidate_values, company_values)
        
        # 2. Alignement par catégorie de valeurs
        value_categories = self._get_value_categories()
        for category in value_categories:
            features[f"values_{category}_match"] = self.calculate_category_alignment(
                candidate_values, company_values, candidate_culture_text, 
                company_culture_text, category)
        
        # 3. Alignement de valeurs implicites (analyse sémantique)
        features["values_implicit_match"] = self.extract_implicit_values_match(
            candidate_culture_text, company_culture_text)
        
        # 4. Style de management
        features["management_style_match"] = self.calculate_management_style_match(
            candidate_profile.get("preferred_management_style", ""),
            company_profile.get("management_style", ""))
        
        # 5. Dynamique d'équipe
        features["team_dynamics_match"] = self.calculate_team_dynamics_match(
            self._extract_team_preferences(candidate_profile),
            self._extract_team_dynamics(company_profile))
        
        # 6. Environnement de travail
        env_keys = ["pace", "formality", "innovation", "collaboration"]
        for key in env_keys:
            features[f"work_env_{key}_match"] = self.calculate_environment_match(
                self._extract_environment_preference(candidate_profile, key),
                self._extract_environment_value(company_profile, key))
        
        # 7. Compatibilité de culture d'entreprise globale
        features["overall_culture_match"] = self.calculate_overall_culture_match(
            candidate_profile, company_profile)
        
        return features
    
    def _extract_values(self, profile):
        """
        Extrait les valeurs explicites d'un profil.
        
        Args:
            profile: Profil de candidat ou d'entreprise
            
        Returns:
            List: Liste des valeurs
        """
        values = []
        
        if not profile:
            return values
        
        # Essayer plusieurs chemins possibles pour les valeurs
        value_paths = [
            "values", "explicit_values", "core_values", 
            "company_values", "personal_values"
        ]
        
        for path in value_paths:
            if path in profile:
                value_field = profile[path]
                
                if isinstance(value_field, list):
                    values.extend([v.lower().strip() for v in value_field if v])
                elif isinstance(value_field, dict):
                    if "values" in value_field:
                        if isinstance(value_field["values"], list):
                            values.extend([v.lower().strip() for v in value_field["values"] if v])
                    else:
                        values.extend([k.lower().strip() for k in value_field.keys()])
                elif isinstance(value_field, str):
                    # Diviser les valeurs séparées par des virgules ou des points-virgules
                    for val in re.split(r'[;,]', value_field):
                        val = val.lower().strip()
                        if val:
                            values.append(val)
        
        # Éliminer les doublons
        return list(set(values))
    
    def _extract_culture_text(self, profile):
        """
        Extrait le texte relatif à la culture à partir d'un profil.
        
        Args:
            profile: Profil de candidat ou d'entreprise
            
        Returns:
            str: Texte combiné relatif à la culture
        """
        if not profile:
            return ""
        
        text_parts = []
        
        # Champs relatifs à la culture pour les candidats
        candidate_fields = [
            "about_me", "career_goals", "work_philosophy",
            "preferred_culture", "preferred_work_environment"
        ]
        
        # Champs relatifs à la culture pour les entreprises
        company_fields = [
            "company_culture", "mission_statement", "vision", 
            "about_us", "work_environment", "company_description"
        ]
        
        # Chercher dans tous les champs possibles
        all_fields = candidate_fields + company_fields
        for field in all_fields:
            if field in profile and isinstance(profile[field], str):
                text_parts.append(profile[field])
            elif field in profile and isinstance(profile[field], list):
                text_parts.extend([item for item in profile[field] if isinstance(item, str)])
        
        # Combiner les textes
        return " ".join(text_parts)
    
    def _get_value_categories(self):
        """
        Obtient les catégories de valeurs depuis la taxonomie.
        
        Returns:
            List: Liste des catégories de valeurs
        """
        # Catégories par défaut si la taxonomie est vide ou incomplète
        default_categories = [
            "ethics", "performance", "relationships", "growth", 
            "social", "business", "personal", "stability"
        ]
        
        if not self.values_taxonomy or "_categories" not in self.values_taxonomy:
            return default_categories
        
        # Extraire les catégories de la taxonomie
        return list(self.values_taxonomy["_categories"].keys())
    
    def calculate_values_alignment(self, candidate_values, company_values):
        """
        Calcule l'alignement direct entre les valeurs du candidat et de l'entreprise.
        
        Args:
            candidate_values: Liste des valeurs du candidat
            company_values: Liste des valeurs de l'entreprise
            
        Returns:
            float: Score d'alignement des valeurs (0.0 - 1.0)
        """
        if not candidate_values or not company_values:
            return 0.5  # Valeur neutre en l'absence de données
        
        # Approche avec expansion de synonymes
        expanded_matches = 0
        
        for company_value in company_values:
            best_match = 0.0
            
            # Vérifier correspondance directe
            for candidate_value in candidate_values:
                # Correspondance exacte
                if company_value == candidate_value:
                    best_match = 1.0
                    break
                
                # Correspondance partielle
                if company_value in candidate_value or candidate_value in company_value:
                    match_score = min(len(company_value), len(candidate_value)) / max(len(company_value), len(candidate_value))
                    best_match = max(best_match, match_score)
                
                # Vérifier les synonymes et termes connexes dans la taxonomie
                if self.values_taxonomy:
                    best_match = max(best_match, self._check_taxonomy_match(company_value, candidate_value))
            
            expanded_matches += best_match
        
        # Calculer le score moyen
        return expanded_matches / len(company_values) if company_values else 0.0
    
    def _check_taxonomy_match(self, value1, value2):
        """
        Vérifie si deux valeurs sont liées dans la taxonomie (synonymes ou termes connexes).
        
        Args:
            value1: Première valeur
            value2: Deuxième valeur
            
        Returns:
            float: Score de correspondance taxonomique (0.0 - 1.0)
        """
        if not self.values_taxonomy:
            return 0.0
        
        # Rechercher la première valeur dans la taxonomie
        value1_entry = None
        for key, entry in self.values_taxonomy.items():
            if key.startswith("_"):  # Ignorer les entrées spéciales comme _categories
                continue
                
            if key.lower() == value1.lower():
                value1_entry = entry
                break
            
            # Vérifier dans les synonymes
            if isinstance(entry, dict) and "synonyms" in entry:
                if any(value1.lower() == syn.lower() for syn in entry["synonyms"]):
                    value1_entry = entry
                    break
        
        if not value1_entry:
            return 0.0
        
        # Vérifier si value2 est un synonyme de value1
        if "synonyms" in value1_entry and any(value2.lower() == syn.lower() for syn in value1_entry["synonyms"]):
            return 0.9  # Haute correspondance pour les synonymes
        
        # Vérifier si value2 est un terme connexe à value1
        if "related_terms" in value1_entry and any(value2.lower() == term.lower() for term in value1_entry["related_terms"]):
            return 0.7  # Correspondance moyenne pour les termes connexes
        
        # Faire la vérification inverse (value2 dans taxonomie, value1 comme synonyme/terme connexe)
        value2_entry = None
        for key, entry in self.values_taxonomy.items():
            if key.startswith("_"):
                continue
                
            if key.lower() == value2.lower():
                value2_entry = entry
                break
            
            if isinstance(entry, dict) and "synonyms" in entry:
                if any(value2.lower() == syn.lower() for syn in entry["synonyms"]):
                    value2_entry = entry
                    break
        
        if not value2_entry:
            return 0.0
        
        # Vérifier si value1 est un synonyme ou terme connexe de value2
        if "synonyms" in value2_entry and any(value1.lower() == syn.lower() for syn in value2_entry["synonyms"]):
            return 0.9
        
        if "related_terms" in value2_entry and any(value1.lower() == term.lower() for term in value2_entry["related_terms"]):
            return 0.7
        
        # Vérifier si les deux valeurs appartiennent à la même catégorie
        if "category" in value1_entry and "category" in value2_entry:
            if value1_entry["category"] == value2_entry["category"]:
                return 0.5  # Correspondance faible pour les valeurs de même catégorie
        
        return 0.0
    
    def calculate_category_alignment(self, candidate_values, company_values, 
                                     candidate_text, company_text, category):
        """
        Calcule l'alignement des valeurs pour une catégorie spécifique.
        
        Args:
            candidate_values: Liste des valeurs du candidat
            company_values: Liste des valeurs de l'entreprise
            candidate_text: Texte relatif à la culture du candidat
            company_text: Texte relatif à la culture de l'entreprise
            category: Catégorie de valeurs à évaluer
            
        Returns:
            float: Score d'alignement pour cette catégorie (0.0 - 1.0)
        """
        if not self.values_taxonomy:
            return 0.5
        
        # Filtrer les valeurs par catégorie
        candidate_category_values = self._filter_values_by_category(candidate_values, category)
        company_category_values = self._filter_values_by_category(company_values, category)
        
        # Si nous avons des valeurs explicites dans cette catégorie, calculer l'alignement direct
        if candidate_category_values and company_category_values:
            explicit_alignment = self.calculate_values_alignment(
                candidate_category_values, company_category_values)
            return explicit_alignment
        
        # Sinon, essayer d'extraire des valeurs implicites du texte
        if candidate_text and company_text:
            candidate_implicit_values = self._extract_category_values_from_text(candidate_text, category)
            company_implicit_values = self._extract_category_values_from_text(company_text, category)
            
            if candidate_implicit_values and company_implicit_values:
                implicit_alignment = self.calculate_values_alignment(
                    candidate_implicit_values, company_implicit_values)
                return implicit_alignment * 0.8  # Légère pénalité pour les valeurs implicites
        
        # Si aucune valeur n'est trouvée, retourner une valeur neutre
        return 0.5
    
    def _filter_values_by_category(self, values, category):
        """
        Filtre les valeurs appartenant à une catégorie spécifique.
        
        Args:
            values: Liste des valeurs
            category: Catégorie de valeurs
            
        Returns:
            List: Valeurs filtrées
        """
        category_values = []
        
        if not self.values_taxonomy or not values:
            return category_values
        
        for value in values:
            value_lower = value.lower()
            
            # Chercher la valeur dans la taxonomie
            for key, entry in self.values_taxonomy.items():
                if key.startswith("_"):
                    continue
                
                # Vérifier si la valeur correspond à une entrée et si elle est dans la bonne catégorie
                if (key.lower() == value_lower or 
                    (isinstance(entry, dict) and "synonyms" in entry and 
                     any(value_lower == syn.lower() for syn in entry["synonyms"]))):
                    
                    if isinstance(entry, dict) and "category" in entry and entry["category"] == category:
                        category_values.append(value_lower)
                        break
        
        return category_values
    
    def _extract_category_values_from_text(self, text, category):
        """
        Extrait les valeurs implicites d'une catégorie spécifique depuis un texte.
        
        Args:
            text: Texte à analyser
            category: Catégorie de valeurs
            
        Returns:
            List: Valeurs extraites
        """
        if not self.values_taxonomy or not text:
            return []
        
        extracted_values = []
        
        # Parcourir la taxonomie pour trouver les valeurs de cette catégorie
        for key, entry in self.values_taxonomy.items():
            if key.startswith("_") or not isinstance(entry, dict) or "category" not in entry:
                continue
            
            if entry["category"] == category:
                value_name = key.lower()
                indicators = []
                
                # Collecter les indicateurs pour cette valeur
                if "indicators" in entry:
                    indicators.extend(entry["indicators"])
                if "synonyms" in entry:
                    indicators.extend(entry["synonyms"])
                if "related_terms" in entry:
                    indicators.extend(entry["related_terms"])
                
                # Vérifier si les indicateurs sont présents dans le texte
                indicator_count = 0
                for indicator in indicators:
                    if indicator.lower() in text.lower():
                        indicator_count += 1
                
                # Si plusieurs indicateurs sont présents, ajouter la valeur
                if indicator_count >= 2:
                    extracted_values.append(value_name)
        
        return extracted_values
    
    def extract_implicit_values_match(self, candidate_text, company_text):
        """
        Calcule la correspondance des valeurs implicites extraites du texte.
        
        Args:
            candidate_text: Texte du candidat
            company_text: Texte de l'entreprise
            
        Returns:
            float: Score de correspondance des valeurs implicites (0.0 - 1.0)
        """
        if not candidate_text or not company_text:
            return 0.5
        
        # Si nous avons un modèle d'embeddings, utiliser la similarité sémantique
        if self.embeddings_available:
            try:
                # Calculer les embeddings
                candidate_embedding = self.embeddings_model.encode([candidate_text])[0]
                company_embedding = self.embeddings_model.encode([company_text])[0]
                
                # Calculer la similarité cosinus
                similarity = cosine_similarity(
                    [candidate_embedding],
                    [company_embedding]
                )[0][0]
                
                return float(similarity)
            except Exception as e:
                self.logger.error(f"Erreur lors du calcul de similarité sémantique: {e}")
        
        # Sinon, utiliser TF-IDF et similarité cosinus
        try:
            tfidf_matrix = self.vectorizer.fit_transform([candidate_text, company_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de similarité TF-IDF: {e}")
            
            # Méthode de repli: mots communs
            if self.nlp:
                try:
                    candidate_doc = self.nlp(candidate_text)
                    company_doc = self.nlp(company_text)
                    
                    candidate_keywords = set(token.lemma_.lower() for token in candidate_doc 
                                         if not token.is_stop and not token.is_punct and token.is_alpha)
                    company_keywords = set(token.lemma_.lower() for token in company_doc 
                                       if not token.is_stop and not token.is_punct and token.is_alpha)
                    
                    common_words = candidate_keywords.intersection(company_keywords)
                    total_words = candidate_keywords.union(company_keywords)
                    
                    if total_words:
                        return len(common_words) / len(total_words)
                except Exception:
                    pass
        
        return 0.5  # Valeur par défaut
    
    def calculate_management_style_match(self, candidate_preference, company_style):
        """
        Compare la compatibilité entre le style de management préféré et pratiqué.
        
        Args:
            candidate_preference: Style de management préféré par le candidat
            company_style: Style de management de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_preference or not company_style:
            return 0.5
        
        # Normaliser les styles
        styles = {
            "directif": ["directif", "autoritaire", "hiérarchique", "structuré", "formel"],
            "démocratique": ["démocratique", "participatif", "collaboratif", "consultatif"],
            "délégatif": ["délégatif", "autonome", "responsabilisant", "confiance"],
            "coaching": ["coaching", "mentor", "développement", "accompagnement", "soutien"],
            "situationnel": ["situationnel", "adaptable", "flexible", "mixte", "agile"]
        }
        
        # Identifier les styles
        candidate_style = None
        company_style_match = None
        
        for style_name, keywords in styles.items():
            for keyword in keywords:
                if keyword.lower() in candidate_preference.lower():
                    candidate_style = style_name
                if keyword.lower() in company_style.lower():
                    company_style_match = style_name
        
        # Si les deux styles sont identifiés
        if candidate_style and company_style_match:
            if candidate_style == company_style_match:
                return 1.0
            
            # Matrice de compatibilité entre styles
            compatibility = {
                "directif": {"directif": 1.0, "démocratique": 0.3, "délégatif": 0.2, "coaching": 0.5, "situationnel": 0.7},
                "démocratique": {"directif": 0.3, "démocratique": 1.0, "délégatif": 0.7, "coaching": 0.8, "situationnel": 0.8},
                "délégatif": {"directif": 0.2, "démocratique": 0.7, "délégatif": 1.0, "coaching": 0.6, "situationnel": 0.7},
                "coaching": {"directif": 0.5, "démocratique": 0.8, "délégatif": 0.6, "coaching": 1.0, "situationnel": 0.9},
                "situationnel": {"directif": 0.7, "démocratique": 0.8, "délégatif": 0.7, "coaching": 0.9, "situationnel": 1.0}
            }
            
            return compatibility.get(candidate_style, {}).get(company_style_match, 0.5)
        
        # Si l'un des styles n'est pas identifié, faire une analyse textuelle
        return self.extract_implicit_values_match(candidate_preference, company_style)
    
    def _extract_team_preferences(self, candidate_profile):
        """
        Extrait les préférences de dynamique d'équipe du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            Dict: Préférences de dynamique d'équipe
        """
        team_preferences = {}
        
        if not candidate_profile:
            return team_preferences
        
        # Chemins possibles pour les préférences d'équipe
        team_fields = [
            "team_preferences", "preferred_team", "work_preferences", 
            "team_environment", "collaboration_style"
        ]
        
        for field in team_fields:
            if field in candidate_profile:
                if isinstance(candidate_profile[field], dict):
                    team_preferences.update(candidate_profile[field])
                elif isinstance(candidate_profile[field], str):
                    # Extraction simple à partir de texte
                    text = candidate_profile[field].lower()
                    
                    # Taille d'équipe
                    if "petite équipe" in text or "small team" in text:
                        team_preferences["team_size"] = "small"
                    elif "grande équipe" in text or "large team" in text:
                        team_preferences["team_size"] = "large"
                    
                    # Collaboration
                    if "étroite collaboration" in text or "close collaboration" in text:
                        team_preferences["collaboration_level"] = "high"
                    elif "autonomie" in text or "indépendance" in text or "autonomy" in text:
                        team_preferences["collaboration_level"] = "low"
        
        return team_preferences
    
    def _extract_team_dynamics(self, company_profile):
        """
        Extrait les dynamiques d'équipe de l'entreprise.
        
        Args:
            company_profile: Profil de l'entreprise
            
        Returns:
            Dict: Dynamiques d'équipe
        """
        team_dynamics = {}
        
        if not company_profile:
            return team_dynamics
        
        # Chemins possibles pour les dynamiques d'équipe
        team_fields = [
            "team_dynamics", "teams", "work_environment", 
            "collaboration", "team_structure"
        ]
        
        for field in team_fields:
            if field in company_profile:
                if isinstance(company_profile[field], dict):
                    team_dynamics.update(company_profile[field])
                elif isinstance(company_profile[field], str):
                    # Extraction simple à partir de texte
                    text = company_profile[field].lower()
                    
                    # Taille d'équipe
                    if "petite équipe" in text or "small team" in text:
                        team_dynamics["team_size"] = "small"
                    elif "grande équipe" in text or "large team" in text:
                        team_dynamics["team_size"] = "large"
                    
                    # Collaboration
                    if "étroite collaboration" in text or "close collaboration" in text:
                        team_dynamics["collaboration_level"] = "high"
                    elif "autonomie" in text or "indépendance" in text or "autonomy" in text:
                        team_dynamics["collaboration_level"] = "low"
        
        return team_dynamics
    
    def calculate_team_dynamics_match(self, candidate_preferences, company_dynamics):
        """
        Calcule la compatibilité des dynamiques d'équipe.
        
        Args:
            candidate_preferences: Préférences d'équipe du candidat
            company_dynamics: Dynamiques d'équipe de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if not candidate_preferences or not company_dynamics:
            return 0.5
        
        match_points = 0
        max_points = 0
        
        # Correspondance de taille d'équipe
        if "team_size" in candidate_preferences and "team_size" in company_dynamics:
            max_points += 1
            if candidate_preferences["team_size"] == company_dynamics["team_size"]:
                match_points += 1
            elif (candidate_preferences["team_size"] == "medium" and 
                  company_dynamics["team_size"] in ["small", "large"]):
                match_points += 0.5
        
        # Correspondance de niveau de collaboration
        if "collaboration_level" in candidate_preferences and "collaboration_level" in company_dynamics:
            max_points += 1
            if candidate_preferences["collaboration_level"] == company_dynamics["collaboration_level"]:
                match_points += 1
            elif (candidate_preferences["collaboration_level"] == "medium" and 
                  company_dynamics["collaboration_level"] in ["low", "high"]):
                match_points += 0.5
        
        # Correspondance de structure d'équipe
        if "team_structure" in candidate_preferences and "team_structure" in company_dynamics:
            max_points += 1
            if candidate_preferences["team_structure"] == company_dynamics["team_structure"]:
                match_points += 1
        
        # Correspondance de fréquence de communication
        if "communication_frequency" in candidate_preferences and "communication_frequency" in company_dynamics:
            max_points += 1
            preferences = {"low": 1, "medium": 2, "high": 3}
            candidate_pref = preferences.get(candidate_preferences["communication_frequency"], 2)
            company_pref = preferences.get(company_dynamics["communication_frequency"], 2)
            
            if candidate_pref == company_pref:
                match_points += 1
            elif abs(candidate_pref - company_pref) == 1:
                match_points += 0.5
        
        # Si aucune caractéristique comparable n'est trouvée
        if max_points == 0:
            return 0.5
        
        return match_points / max_points
    
    def _extract_environment_preference(self, candidate_profile, key):
        """
        Extrait une préférence d'environnement spécifique du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            key: Clé de la préférence à extraire
            
        Returns:
            str: Valeur de la préférence
        """
        if not candidate_profile:
            return None
        
        # Chemins possibles pour les préférences d'environnement
        env_paths = [
            "work_preferences.environment", "work_preferences", 
            "preferred_environment", "environment_preferences"
        ]
        
        for path in env_paths:
            parts = path.split('.')
            current = candidate_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, dict) and key in current:
                return current[key]
        
        # Recherche dans le texte pour certaines préférences clés
        text_fields = [
            "about_me", "preferred_culture", "preferred_work_environment",
            "work_preferences", "career_goals"
        ]
        
        combined_text = ""
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                combined_text += " " + candidate_profile[field].lower()
        
        # Recherche de patterns selon la clé
        if key == "pace":
            if "rythme rapide" in combined_text or "fast-paced" in combined_text:
                return "fast"
            elif "équilibré" in combined_text or "balanced" in combined_text:
                return "balanced"
            elif "calme" in combined_text or "relaxed" in combined_text:
                return "relaxed"
        elif key == "formality":
            if "formel" in combined_text or "formal" in combined_text:
                return "formal"
            elif "décontracté" in combined_text or "casual" in combined_text:
                return "casual"
        elif key == "innovation":
            if "innovant" in combined_text or "innovative" in combined_text:
                return "high"
            elif "traditionnel" in combined_text or "traditional" in combined_text:
                return "low"
        elif key == "collaboration":
            if "collaboratif" in combined_text or "collaborative" in combined_text:
                return "high"
            elif "indépendant" in combined_text or "independent" in combined_text:
                return "low"
        
        return None
    
    def _extract_environment_value(self, company_profile, key):
        """
        Extrait une caractéristique d'environnement de l'entreprise.
        
        Args:
            company_profile: Profil de l'entreprise
            key: Clé de la caractéristique à extraire
            
        Returns:
            str: Valeur de la caractéristique
        """
        if not company_profile:
            return None
        
        # Chemins possibles pour l'environnement de travail
        env_paths = [
            "work_environment.culture", "work_environment", 
            "company_culture", "environment"
        ]
        
        for path in env_paths:
            parts = path.split('.')
            current = company_profile
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current and isinstance(current, dict) and key in current:
                return current[key]
        
        # Recherche dans le texte
        text_fields = [
            "company_culture", "about_us", "work_environment",
            "culture", "company_description"
        ]
        
        combined_text = ""
        for field in text_fields:
            if field in company_profile and isinstance(company_profile[field], str):
                combined_text += " " + company_profile[field].lower()
        
        # Recherche de patterns selon la clé
        if key == "pace":
            if "rythme rapide" in combined_text or "fast-paced" in combined_text:
                return "fast"
            elif "équilibré" in combined_text or "balanced" in combined_text:
                return "balanced"
            elif "calme" in combined_text or "relaxed" in combined_text:
                return "relaxed"
        elif key == "formality":
            if "formel" in combined_text or "formal" in combined_text:
                return "formal"
            elif "décontracté" in combined_text or "casual" in combined_text:
                return "casual"
        elif key == "innovation":
            if "innovant" in combined_text or "innovative" in combined_text:
                return "high"
            elif "traditionnel" in combined_text or "traditional" in combined_text:
                return "low"
        elif key == "collaboration":
            if "collaboratif" in combined_text or "collaborative" in combined_text:
                return "high"
            elif "indépendant" in combined_text or "independent" in combined_text:
                return "low"
        
        return None
    
    def calculate_environment_match(self, candidate_preference, company_value):
        """
        Calcule la compatibilité pour une caractéristique d'environnement.
        
        Args:
            candidate_preference: Préférence du candidat
            company_value: Valeur de l'entreprise
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if candidate_preference is None or company_value is None:
            return 0.5
        
        # Si les valeurs sont identiques
        if candidate_preference == company_value:
            return 1.0
        
        # Matrices de compatibilité pour différentes caractéristiques
        compatibility = {
            "pace": {
                "fast": {"fast": 1.0, "balanced": 0.6, "relaxed": 0.2},
                "balanced": {"fast": 0.6, "balanced": 1.0, "relaxed": 0.6},
                "relaxed": {"fast": 0.2, "balanced": 0.6, "relaxed": 1.0}
            },
            "formality": {
                "formal": {"formal": 1.0, "casual": 0.4},
                "casual": {"formal": 0.4, "casual": 1.0}
            },
            "innovation": {
                "high": {"high": 1.0, "medium": 0.7, "low": 0.3},
                "medium": {"high": 0.7, "medium": 1.0, "low": 0.7},
                "low": {"high": 0.3, "medium": 0.7, "low": 1.0}
            },
            "collaboration": {
                "high": {"high": 1.0, "medium": 0.6, "low": 0.2},
                "medium": {"high": 0.6, "medium": 1.0, "low": 0.6},
                "low": {"high": 0.2, "medium": 0.6, "low": 1.0}
            }
        }
        
        # Déterminer la caractéristique concernée
        for char_type, matrix in compatibility.items():
            if candidate_preference in matrix and company_value in matrix[candidate_preference]:
                return matrix[candidate_preference][company_value]
        
        # Par défaut, compatibilité moyenne
        return 0.5
    
    def calculate_overall_culture_match(self, candidate_profile, company_profile):
        """
        Calcule un score global de compatibilité culturelle.
        
        Args:
            candidate_profile: Profil du candidat
            company_profile: Profil de l'entreprise
            
        Returns:
            float: Score global de compatibilité culturelle (0.0 - 1.0)
        """
        if not candidate_profile or not company_profile:
            return 0.5
        
        # Extraire les textes culturels
        candidate_text = self._extract_culture_text(candidate_profile)
        company_text = self._extract_culture_text(company_profile)
        
        if not candidate_text or not company_text:
            return 0.5
        
        # Calculer la similarité sémantique
        semantic_similarity = self.extract_implicit_values_match(candidate_text, company_text)
        
        # Extraire et comparer les valeurs
        candidate_values = self._extract_values(candidate_profile)
        company_values = self._extract_values(company_profile)
        
        values_alignment = 0.5
        if candidate_values and company_values:
            values_alignment = self.calculate_values_alignment(candidate_values, company_values)
        
        # Détecter le type de culture d'entreprise
        company_type = self._detect_company_culture_type(company_profile)
        candidate_preference = self._detect_preferred_company_type(candidate_profile)
        
        type_compatibility = 0.5
        if company_type and candidate_preference:
            type_compatibility = self._calculate_company_type_compatibility(candidate_preference, company_type)
        
        # Pondérer les différents facteurs
        weights = {
            "semantic_similarity": 0.4,
            "values_alignment": 0.4,
            "type_compatibility": 0.2
        }
        
        # Calculer le score global pondéré
        overall_score = (
            semantic_similarity * weights["semantic_similarity"] +
            values_alignment * weights["values_alignment"] +
            type_compatibility * weights["type_compatibility"]
        )
        
        return overall_score
    
    def _detect_company_culture_type(self, company_profile):
        """
        Détecte le type de culture d'entreprise.
        
        Args:
            company_profile: Profil de l'entreprise
            
        Returns:
            str: Type de culture détecté
        """
        if not company_profile or not self.values_taxonomy:
            return None
        
        # Extraire les valeurs et le texte culturel
        company_values = self._extract_values(company_profile)
        company_text = self._extract_culture_text(company_profile)
        
        if not company_values and not company_text:
            return None
        
        # Vérifier les types d'environnement dans la taxonomie
        if "_work_environments" in self.values_taxonomy:
            environments = self.values_taxonomy["_work_environments"]
            
            # Calculer le score pour chaque type d'environnement
            env_scores = {}
            
            for env_type, env_values in environments.items():
                # Compter les valeurs correspondantes
                matching_values = sum(1 for v in company_values if v in env_values)
                
                # Compter les mentions dans le texte
                text_mentions = 0
                if company_text:
                    for v in env_values:
                        if v.lower() in company_text.lower():
                            text_mentions += 1
                
                # Calculer le score global
                env_scores[env_type] = (matching_values * 2 + text_mentions) / (len(env_values) * 2 + len(env_values))
            
            # Trouver le type d'environnement avec le score le plus élevé
            if env_scores:
                best_match = max(env_scores.items(), key=lambda x: x[1])
                if best_match[1] > 0.3:  # Seuil minimal
                    return best_match[0]
        
        # Méthode alternative: recherche de mots-clés
        if company_text:
            keywords = {
                "start-up": ["start-up", "startup", "innovation", "agile", "disruption", "flexible"],
                "corporate": ["corporate", "enterprise", "established", "multinational", "groupe"],
                "public": ["public", "government", "état", "service public", "administration"],
                "non-profit": ["non-profit", "ngo", "association", "social", "impact", "ong"],
                "agency": ["agency", "agence", "consulting", "conseil", "service", "creative"],
                "research": ["research", "recherche", "academic", "académique", "r&d", "scientifique"]
            }
            
            type_scores = {}
            for env_type, kw_list in keywords.items():
                mentions = sum(1 for kw in kw_list if kw.lower() in company_text.lower())
                type_scores[env_type] = mentions / len(kw_list)
            
            if type_scores:
                best_match = max(type_scores.items(), key=lambda x: x[1])
                if best_match[1] > 0.2:  # Seuil minimal
                    return best_match[0]
        
        return None
    
    def _detect_preferred_company_type(self, candidate_profile):
        """
        Détecte le type d'entreprise préféré par le candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Type d'entreprise préféré
        """
        if not candidate_profile:
            return None
        
        # Vérifier les préférences explicites
        preference_fields = [
            "preferred_company_type", "company_type_preference", 
            "preferred_employer", "preferred_workplace"
        ]
        
        for field in preference_fields:
            if field in candidate_profile:
                value = candidate_profile[field]
                if isinstance(value, str):
                    value_lower = value.lower()
                    
                    # Types d'entreprise courants
                    if "start" in value_lower:
                        return "start-up"
                    elif "corporate" in value_lower or "grande entreprise" in value_lower:
                        return "corporate"
                    elif "public" in value_lower or "gouvernement" in value_lower:
                        return "public"
                    elif "non-profit" in value_lower or "ong" in value_lower or "associatif" in value_lower:
                        return "non-profit"
                    elif "agence" in value_lower or "agency" in value_lower or "conseil" in value_lower:
                        return "agency"
                    elif "recherche" in value_lower or "research" in value_lower or "académique" in value_lower:
                        return "research"
        
        # Recherche dans le texte
        text_fields = [
            "about_me", "career_goals", "preferred_culture", 
            "work_preferences", "preferred_work_environment"
        ]
        
        combined_text = ""
        for field in text_fields:
            if field in candidate_profile and isinstance(candidate_profile[field], str):
                combined_text += " " + candidate_profile[field].lower()
        
        if combined_text:
            keywords = {
                "start-up": ["start-up", "startup", "innovation", "agile", "disruption", "flexible"],
                "corporate": ["corporate", "enterprise", "established", "multinational", "groupe"],
                "public": ["public", "government", "état", "service public", "administration"],
                "non-profit": ["non-profit", "ngo", "association", "social", "impact", "ong"],
                "agency": ["agency", "agence", "consulting", "conseil", "service", "creative"],
                "research": ["research", "recherche", "academic", "académique", "r&d", "scientifique"]
            }
            
            type_scores = {}
            for env_type, kw_list in keywords.items():
                mentions = sum(1 for kw in kw_list if kw.lower() in combined_text.lower())
                type_scores[env_type] = mentions / len(kw_list)
            
            if type_scores:
                best_match = max(type_scores.items(), key=lambda x: x[1])
                if best_match[1] > 0.2:  # Seuil minimal
                    return best_match[0]
        
        return None
    
    def _calculate_company_type_compatibility(self, candidate_preference, company_type):
        """
        Calcule la compatibilité entre le type d'entreprise préféré et réel.
        
        Args:
            candidate_preference: Type d'entreprise préféré
            company_type: Type d'entreprise réel
            
        Returns:
            float: Score de compatibilité (0.0 - 1.0)
        """
        if candidate_preference == company_type:
            return 1.0
        
        # Matrice de compatibilité entre types d'entreprise
        compatibility = {
            "start-up": {"start-up": 1.0, "agency": 0.8, "corporate": 0.4, "research": 0.7, "non-profit": 0.6, "public": 0.3},
            "corporate": {"start-up": 0.4, "agency": 0.6, "corporate": 1.0, "research": 0.5, "non-profit": 0.3, "public": 0.6},
            "public": {"start-up": 0.3, "agency": 0.5, "corporate": 0.6, "research": 0.6, "non-profit": 0.7, "public": 1.0},
            "non-profit": {"start-up": 0.6, "agency": 0.5, "corporate": 0.3, "research": 0.7, "non-profit": 1.0, "public": 0.7},
            "agency": {"start-up": 0.8, "agency": 1.0, "corporate": 0.6, "research": 0.5, "non-profit": 0.5, "public": 0.5},
            "research": {"start-up": 0.7, "agency": 0.5, "corporate": 0.5, "research": 1.0, "non-profit": 0.7, "public": 0.6}
        }
        
        if candidate_preference in compatibility and company_type in compatibility[candidate_preference]:
            return compatibility[candidate_preference][company_type]
        
        return 0.5  # Valeur par défaut
