"""
Générateur de features basées sur les compétences techniques.
"""

import json
import logging
import numpy as np
from pathlib import Path
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SkillsFeatureGenerator:
    """
    Générateur de features pour le matching technique de compétences.
    """
    
    def __init__(self, taxonomy_path=None, embeddings_model="paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialise le générateur de features de compétences.
        
        Args:
            taxonomy_path: Chemin vers le fichier JSON de taxonomie des compétences
            embeddings_model: Nom du modèle Sentence-BERT pour les embeddings
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialisation du vectoriseur TF-IDF
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85,
            stop_words=['french', 'english'],
            use_idf=True
        )
        
        # Chargement de la taxonomie des compétences
        self.skills_taxonomy = self._load_taxonomy(taxonomy_path)
        
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
    
    def _load_taxonomy(self, taxonomy_path):
        """
        Charge la taxonomie hiérarchique des compétences.
        
        Args:
            taxonomy_path: Chemin vers le fichier JSON de taxonomie
            
        Returns:
            Dict: Taxonomie des compétences
        """
        # Chemin par défaut si non spécifié
        if not taxonomy_path:
            taxonomy_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "skills_taxonomy.json"
        
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
        Crée une taxonomie de compétences par défaut.
        
        Args:
            taxonomy_path: Chemin où sauvegarder la taxonomie par défaut
            
        Returns:
            Dict: Taxonomie par défaut
        """
        # Structure de base pour une taxonomie simplifiée
        default_taxonomy = {
            "technical": {
                "programming_languages": {
                    "python": ["django", "flask", "pandas", "numpy", "scipy", "tensorflow", "pytorch"],
                    "javascript": ["react", "angular", "vue", "node.js", "express", "jquery"],
                    "java": ["spring", "hibernate", "maven", "junit", "jakarta ee"],
                    "c_cpp": ["c", "c++", "stl", "boost", "qt"],
                    "php": ["symfony", "laravel", "wordpress", "drupal"],
                    "ruby": ["rails", "sinatra", "rspec"],
                    "go": ["gin", "echo", "gorm"],
                    "swift": ["swiftui", "combine", "core data"],
                    "kotlin": ["android", "spring boot", "coroutines", "ktor"],
                    "typescript": ["angular", "react", "vue", "nest.js"]
                },
                "web_technologies": {
                    "frontend": ["html", "css", "javascript", "react", "angular", "vue"],
                    "backend": ["django", "flask", "express", "spring boot", "laravel"],
                    "database": ["sql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch"]
                },
                "data_science": {
                    "machine_learning": ["scikit-learn", "tensorflow", "pytorch", "xgboost", "regression", "classification"],
                    "data_analysis": ["pandas", "numpy", "r", "spss", "excel", "powerbi", "tableau"],
                    "big_data": ["hadoop", "spark", "kafka", "hive", "pig", "yarn"],
                    "natural_language_processing": ["nltk", "spacy", "gensim", "bert", "word2vec"]
                },
                "devops": {
                    "cloud": ["aws", "azure", "gcp", "kubernetes", "docker"],
                    "ci_cd": ["jenkins", "gitlab ci", "github actions", "travis ci", "circleci"],
                    "infrastructure": ["terraform", "ansible", "puppet", "chef"]
                },
                "security": {
                    "application_security": ["owasp", "pen testing", "authentication", "authorization"],
                    "network_security": ["firewall", "vpn", "ssl/tls", "encryption"],
                    "security_tools": ["nmap", "wireshark", "metasploit", "burp suite"]
                }
            },
            "soft_skills": {
                "communication": ["written", "verbal", "presentation", "listening", "negotiation"],
                "teamwork": ["collaboration", "conflict resolution", "leadership", "mentoring"],
                "problem_solving": ["analytical thinking", "critical thinking", "creativity", "research"],
                "adaptability": ["flexibility", "learning", "resilience", "change management"],
                "organization": ["time management", "planning", "prioritization", "project management"]
            },
            "domain_knowledge": {
                "finance": ["accounting", "trading", "investment banking", "risk assessment"],
                "healthcare": ["medical terminology", "healthcare regulations", "clinical workflows"],
                "retail": ["e-commerce", "inventory management", "crm", "pos systems"],
                "manufacturing": ["supply chain", "quality control", "production planning"],
                "education": ["curriculum development", "instructional design", "e-learning"]
            },
            "languages": {
                "english": ["native", "fluent", "professional", "intermediate", "basic"],
                "french": ["native", "fluent", "professional", "intermediate", "basic"],
                "german": ["native", "fluent", "professional", "intermediate", "basic"],
                "spanish": ["native", "fluent", "professional", "intermediate", "basic"],
                "chinese": ["native", "fluent", "professional", "intermediate", "basic"],
                "japanese": ["native", "fluent", "professional", "intermediate", "basic"]
            },
            "methodologies": {
                "agile": ["scrum", "kanban", "xp", "safe", "lean"],
                "project_management": ["pmp", "prince2", "waterfall", "itil", "pmbok"],
                "quality": ["six sigma", "iso 9001", "cmmi", "tqm"]
            }
        }
        
        # Sauvegarder pour utilisation future si un chemin est spécifié
        if taxonomy_path:
            try:
                # S'assurer que le répertoire parent existe
                Path(taxonomy_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(taxonomy_path, 'w', encoding='utf-8') as f:
                    json.dump(default_taxonomy, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Taxonomie par défaut sauvegardée à {taxonomy_path}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la sauvegarde de la taxonomie: {e}")
        
        return default_taxonomy
    
    def generate_skill_features(self, candidate_skills, job_skills):
        """
        Génère les features de matching de compétences entre un candidat et une offre.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            Dict: Features de matching des compétences
        """
        features = {}
        
        # Normalisation des listes de compétences
        candidate_skills = self._normalize_skill_list(candidate_skills)
        job_skills = self._normalize_skill_list(job_skills)
        
        if not candidate_skills or not job_skills:
            # Valeurs par défaut si les compétences sont manquantes
            return self._default_skill_features()
        
        # 1. Matching direct des compétences avec TF-IDF
        features["skills_exact_match"] = self.calculate_exact_matches(candidate_skills, job_skills)
        
        # 2. Couverture des compétences requises
        features["skills_coverage"] = self.calculate_skills_coverage(candidate_skills, job_skills)
        
        # 3. Matching sémantique avec embeddings (si disponible)
        if self.embeddings_available:
            features["skills_semantic_match"] = self.calculate_semantic_similarity(candidate_skills, job_skills)
        else:
            features["skills_semantic_match"] = features["skills_exact_match"]  # Fallback
        
        # 4. Matching taxonomique (hiérarchie de compétences)
        features["skills_taxonomy_match"] = self.calculate_taxonomy_match(candidate_skills, job_skills)
        
        # 5. Matching par catégorie de compétences
        skill_categories = self._get_skill_categories()
        for category in skill_categories:
            features[f"skills_{category}_match"] = self.calculate_category_match(
                candidate_skills, job_skills, category)
        
        return features
    
    def _normalize_skill_list(self, skills):
        """
        Normalise une liste de compétences pour le traitement.
        
        Args:
            skills: Liste de compétences (peut être une liste, un dict ou une chaîne)
            
        Returns:
            List: Liste normalisée de compétences
        """
        normalized_skills = []
        
        if not skills:
            return normalized_skills
        
        # Traiter différents formats d'entrée
        if isinstance(skills, list):
            # Si c'est déjà une liste
            for skill in skills:
                if isinstance(skill, str):
                    normalized_skills.append(skill.lower().strip())
                elif isinstance(skill, dict) and 'name' in skill:
                    normalized_skills.append(skill['name'].lower().strip())
        elif isinstance(skills, dict):
            # Si c'est un dictionnaire avec des clés 'skills'
            if 'skills' in skills and isinstance(skills['skills'], list):
                return self._normalize_skill_list(skills['skills'])
            # Sinon, prendre les clés comme noms de compétences
            for skill_name in skills.keys():
                normalized_skills.append(skill_name.lower().strip())
        elif isinstance(skills, str):
            # Si c'est une chaîne, la diviser (supposant qu'elle soit séparée par des virgules)
            normalized_skills = [s.lower().strip() for s in skills.split(',')]
        
        # Filtrer les valeurs vides
        return [s for s in normalized_skills if s]
    
    def _default_skill_features(self):
        """
        Retourne un ensemble de features par défaut lorsque les données sont insuffisantes.
        
        Returns:
            Dict: Features par défaut
        """
        skill_categories = self._get_skill_categories()
        
        features = {
            "skills_exact_match": 0.0,
            "skills_coverage": 0.0,
            "skills_semantic_match": 0.0,
            "skills_taxonomy_match": 0.0
        }
        
        # Ajouter les features par catégorie
        for category in skill_categories:
            features[f"skills_{category}_match"] = 0.0
        
        return features
    
    def _get_skill_categories(self):
        """
        Obtient les catégories principales de compétences depuis la taxonomie.
        
        Returns:
            List: Liste des catégories principales
        """
        # Catégories par défaut si la taxonomie est vide
        default_categories = ["technical", "soft_skills", "domain_knowledge", "languages", "methodologies"]
        
        if not self.skills_taxonomy:
            return default_categories
        
        # Sinon, extraire les catégories de premier niveau de la taxonomie
        return list(self.skills_taxonomy.keys())
    
    def calculate_exact_matches(self, candidate_skills, job_skills):
        """
        Calcule le matching exact entre deux listes de compétences.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            float: Score de matching exact (0.0 - 1.0)
        """
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Convertir en ensembles pour comparaison efficace
        candidate_set = set(candidate_skills)
        job_set = set(job_skills)
        
        # Nombre de correspondances exactes
        exact_matches = len(candidate_set.intersection(job_set))
        
        # Calculer le score normalisé (F1-score)
        precision = exact_matches / len(candidate_set) if candidate_set else 0
        recall = exact_matches / len(job_set) if job_set else 0
        
        if precision + recall == 0:
            return 0.0
        
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score
    
    def calculate_skills_coverage(self, candidate_skills, job_skills):
        """
        Calcule le pourcentage de compétences requises couvertes par le candidat.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            float: Couverture des compétences (0.0 - 1.0)
        """
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Compter les compétences requises couvertes
        covered_count = 0
        
        for job_skill in job_skills:
            covered = False
            
            # Vérifier correspondance exacte
            if job_skill in candidate_skills:
                covered = True
            else:
                # Vérifier correspondance partielle
                for candidate_skill in candidate_skills:
                    if (job_skill in candidate_skill) or (candidate_skill in job_skill):
                        covered = True
                        break
            
            if covered:
                covered_count += 1
        
        return covered_count / len(job_skills)
    
    def calculate_semantic_similarity(self, candidate_skills, job_skills):
        """
        Calcule la similarité sémantique entre deux ensembles de compétences
        en utilisant des embeddings de phrases.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            float: Score de similarité sémantique (0.0 - 1.0)
        """
        if not self.embeddings_available or not candidate_skills or not job_skills:
            return self.calculate_skills_coverage(candidate_skills, job_skills)
        
        try:
            # Joindre les compétences en chaînes
            candidate_text = ", ".join(candidate_skills)
            job_text = ", ".join(job_skills)
            
            # Calculer les embeddings
            candidate_embedding = self.embeddings_model.encode([candidate_text])[0]
            job_embedding = self.embeddings_model.encode([job_text])[0]
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity(
                [candidate_embedding],
                [job_embedding]
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de similarité sémantique: {e}")
            return self.calculate_skills_coverage(candidate_skills, job_skills)
    
    def calculate_taxonomy_match(self, candidate_skills, job_skills):
        """
        Calcule le matching basé sur la taxonomie hiérarchique des compétences.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            float: Score de matching taxonomique (0.0 - 1.0)
        """
        if not self.skills_taxonomy or not candidate_skills or not job_skills:
            return self.calculate_skills_coverage(candidate_skills, job_skills)
        
        try:
            # Trouver les chemins taxonomiques pour chaque compétence
            candidate_paths = self._find_skill_paths(candidate_skills)
            job_paths = self._find_skill_paths(job_skills)
            
            if not candidate_paths or not job_paths:
                return self.calculate_skills_coverage(candidate_skills, job_skills)
            
            # Calculer les distances taxonomiques
            total_similarity = 0.0
            match_count = 0
            
            for job_skill, job_path in job_paths.items():
                best_similarity = 0.0
                
                for candidate_skill, candidate_path in candidate_paths.items():
                    # Calculer la similarité des chemins
                    path_similarity = self._calculate_path_similarity(candidate_path, job_path)
                    best_similarity = max(best_similarity, path_similarity)
                
                if best_similarity > 0:
                    total_similarity += best_similarity
                    match_count += 1
            
            if match_count == 0:
                return 0.0
            
            return total_similarity / len(job_paths)
        
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de match taxonomique: {e}")
            return self.calculate_skills_coverage(candidate_skills, job_skills)
    
    def _find_skill_paths(self, skills):
        """
        Trouve les chemins taxonomiques pour chaque compétence.
        
        Args:
            skills: Liste des compétences
            
        Returns:
            Dict: Dictionnaire de chemins {compétence: chemin_taxonomique}
        """
        skill_paths = {}
        
        for skill in skills:
            skill_lower = skill.lower()
            paths = self._search_skill_in_taxonomy(self.skills_taxonomy, skill_lower, [])
            
            if paths:
                skill_paths[skill_lower] = paths[0]  # Prendre le premier chemin trouvé
        
        return skill_paths
    
    def _search_skill_in_taxonomy(self, taxonomy, skill, current_path):
        """
        Recherche récursivement une compétence dans la taxonomie.
        
        Args:
            taxonomy: Dictionnaire de taxonomie (ou sous-branche)
            skill: Compétence à rechercher
            current_path: Chemin actuel dans la taxonomie
            
        Returns:
            List: Liste des chemins trouvés
        """
        paths = []
        
        if isinstance(taxonomy, dict):
            # Parcourir les clés du dictionnaire
            for key, value in taxonomy.items():
                key_lower = key.lower()
                new_path = current_path + [key_lower]
                
                # Vérifier si la compétence correspond à cette clé
                if key_lower == skill or key_lower in skill or skill in key_lower:
                    paths.append(new_path)
                
                # Rechercher dans les sous-branches
                if isinstance(value, (dict, list)):
                    sub_paths = self._search_skill_in_taxonomy(value, skill, new_path)
                    paths.extend(sub_paths)
                
        elif isinstance(taxonomy, list):
            # Parcourir les éléments de la liste
            for item in taxonomy:
                if isinstance(item, (dict, list)):
                    # Récursion pour dictionnaires ou listes imbriqués
                    sub_paths = self._search_skill_in_taxonomy(item, skill, current_path)
                    paths.extend(sub_paths)
                elif isinstance(item, str):
                    # Vérifier si la compétence correspond à cet élément
                    item_lower = item.lower()
                    if item_lower == skill or item_lower in skill or skill in item_lower:
                        paths.append(current_path + [item_lower])
        
        return paths
    
    def _calculate_path_similarity(self, path1, path2):
        """
        Calcule la similarité entre deux chemins taxonomiques.
        
        Args:
            path1: Premier chemin taxonomique
            path2: Deuxième chemin taxonomique
            
        Returns:
            float: Score de similarité (0.0 - 1.0)
        """
        # Calculer la longueur du préfixe commun
        common_prefix_len = 0
        for i in range(min(len(path1), len(path2))):
            if path1[i] == path2[i]:
                common_prefix_len += 1
            else:
                break
        
        if common_prefix_len == 0:
            return 0.0
        
        # Calculer la similarité basée sur la longueur du préfixe commun
        # et la longueur totale des chemins
        max_path_len = max(len(path1), len(path2))
        return common_prefix_len / max_path_len
    
    def calculate_category_match(self, candidate_skills, job_skills, category):
        """
        Calcule le matching des compétences dans une catégorie spécifique.
        
        Args:
            candidate_skills: Liste des compétences du candidat
            job_skills: Liste des compétences requises pour le poste
            category: Catégorie de compétences à évaluer
            
        Returns:
            float: Score de matching pour cette catégorie (0.0 - 1.0)
        """
        if not self.skills_taxonomy or not candidate_skills or not job_skills:
            return 0.0
        
        # Filtrer les compétences par catégorie
        candidate_category_skills = self._filter_skills_by_category(candidate_skills, category)
        job_category_skills = self._filter_skills_by_category(job_skills, category)
        
        if not candidate_category_skills or not job_category_skills:
            return 0.0
        
        # Calculer la couverture dans cette catégorie
        return self.calculate_skills_coverage(candidate_category_skills, job_category_skills)
    
    def _filter_skills_by_category(self, skills, category):
        """
        Filtre les compétences appartenant à une catégorie spécifique.
        
        Args:
            skills: Liste des compétences
            category: Catégorie de compétences
            
        Returns:
            List: Compétences filtrées
        """
        category_skills = []
        
        if category not in self.skills_taxonomy:
            return category_skills
        
        for skill in skills:
            skill_lower = skill.lower()
            paths = self._search_skill_in_taxonomy(self.skills_taxonomy[category], skill_lower, [category])
            
            if paths:
                category_skills.append(skill_lower)
        
        return category_skills
