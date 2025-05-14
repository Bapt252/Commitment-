"""Module d'analyse sémantique pour le système Nexten SmartMatch.
Ce module permet de calculer la similarité entre deux ensembles de compétences.
"""

import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SemanticAnalyzer")

class SemanticAnalyzer:
    """
    Classe pour analyser la similarité sémantique entre les compétences.
    """
    
    def __init__(self):
        """
        Initialise l'analyseur sémantique avec un dictionnaire de synonymes
        et d'équivalences pour les compétences techniques.
        """
        self.vectorizer = TfidfVectorizer()
        
        # Dictionnaire de synonymes et équivalences pour les compétences
        self.synonyms = {
            "javascript": ["js", "javascript", "ecmascript"],
            "python": ["python", "python3", "py"],
            "react": ["react", "reactjs", "react.js"],
            "node.js": ["node", "nodejs", "node.js"],
            "vue.js": ["vue", "vuejs", "vue.js"],
            "angular": ["angular", "angularjs", "angular.js"],
            "sql": ["sql", "mysql", "postgresql", "tsql", "database"],
            "machine learning": ["ml", "machine learning", "deep learning", "ai"],
            "devops": ["devops", "devsecops", "sre"],
            "docker": ["docker", "containerization", "containers"],
            "kubernetes": ["k8s", "kubernetes", "orchestration"],
            "aws": ["aws", "amazon web services", "cloud"],
            "frontend": ["frontend", "front-end", "client-side", "ui"],
            "backend": ["backend", "back-end", "server-side", "api"],
            "fullstack": ["full stack", "fullstack", "full-stack"],
            "web development": ["web dev", "web development", "web programming"],
            "api": ["api", "rest", "graphql", "web services"],
            "big data": ["big data", "hadoop", "spark", "data engineering"]
        }
        
        # Matrice de similarité prédéfinie pour certaines compétences
        self.similarity_matrix = {
            ("python", "data science"): 0.8,
            ("javascript", "frontend"): 0.9,
            ("java", "spring"): 0.85,
            ("docker", "kubernetes"): 0.75,
            ("sql", "database"): 0.9,
            ("react", "vue.js"): 0.7,
            ("devops", "aws"): 0.6,
            ("machine learning", "data science"): 0.85,
            ("python", "machine learning"): 0.7,
            ("javascript", "node.js"): 0.8
        }
        
        logger.info("Analyseur sémantique initialisé avec succès")
    
    def normalize_skill(self, skill):
        """
        Normalise une compétence en la convertissant en minuscules 
        et en trouvant son terme canonique si un synonyme existe.
        
        Args:
            skill (str): La compétence à normaliser
            
        Returns:
            str: La compétence normalisée
        """
        skill = skill.lower()
        
        # Rechercher dans les synonymes
        for canonical, synonyms in self.synonyms.items():
            if skill in synonyms:
                return canonical
        
        return skill
    
    def calculate_similarity(self, skills1, skills2):
        """
        Calcule la similarité entre deux ensembles de compétences.
        
        Args:
            skills1 (list): Premier ensemble de compétences
            skills2 (list): Deuxième ensemble de compétences
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        if not skills1 or not skills2:
            return 0.0
        
        # Normaliser les compétences
        normalized_skills1 = [self.normalize_skill(skill) for skill in skills1]
        normalized_skills2 = [self.normalize_skill(skill) for skill in skills2]
        
        # Vérifier les correspondances directes et les paires prédéfinies
        direct_matches = 0
        predefined_similarity = 0
        predefined_pairs = 0
        
        for skill1 in normalized_skills1:
            # Correspondances directes
            if skill1 in normalized_skills2:
                direct_matches += 1
            
            # Paires prédéfinies
            for skill2 in normalized_skills2:
                if (skill1, skill2) in self.similarity_matrix:
                    predefined_similarity += self.similarity_matrix[(skill1, skill2)]
                    predefined_pairs += 1
                elif (skill2, skill1) in self.similarity_matrix:
                    predefined_similarity += self.similarity_matrix[(skill2, skill1)]
                    predefined_pairs += 1
        
        # Calcul de similarité par TF-IDF et cosinus pour les compétences restantes
        # Convertir les listes de compétences en documents textuels
        doc1 = " ".join(normalized_skills1)
        doc2 = " ".join(normalized_skills2)
        
        try:
            # Vectoriser les documents
            tfidf_matrix = self.vectorizer.fit_transform([doc1, doc2])
            
            # Calculer la similarité cosinus
            cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception as e:
            logger.warning(f"Erreur lors du calcul de similarité TF-IDF: {e}")
            cos_sim = 0
        
        # Combinaison des scores
        total_skills = max(len(skills1), len(skills2))
        direct_match_score = direct_matches / total_skills if total_skills > 0 else 0
        
        predefined_score = 0
        if predefined_pairs > 0:
            predefined_score = predefined_similarity / predefined_pairs
        
        # Pondération des différentes méthodes
        final_score = 0.5 * direct_match_score + 0.3 * predefined_score + 0.2 * cos_sim
        
        return min(1.0, max(0.0, final_score))
    
    def get_skill_gaps(self, candidate_skills, job_skills):
        """
        Identifie les compétences manquantes à un candidat par rapport à un poste.
        
        Args:
            candidate_skills (list): Les compétences du candidat
            job_skills (list): Les compétences requises pour le poste
            
        Returns:
            list: Liste des compétences manquantes
        """
        normalized_candidate_skills = [self.normalize_skill(skill) for skill in candidate_skills]
        normalized_job_skills = [self.normalize_skill(skill) for skill in job_skills]
        
        missing_skills = []
        
        for job_skill in normalized_job_skills:
            # Vérifier si la compétence est présente directement
            if job_skill not in normalized_candidate_skills:
                # Vérifier s'il existe une compétence similaire
                found_similar = False
                for candidate_skill in normalized_candidate_skills:
                    # Vérifier dans la matrice de similarité
                    if ((candidate_skill, job_skill) in self.similarity_matrix and 
                        self.similarity_matrix[(candidate_skill, job_skill)] > 0.7) or \
                       ((job_skill, candidate_skill) in self.similarity_matrix and 
                        self.similarity_matrix[(job_skill, candidate_skill)] > 0.7):
                        found_similar = True
                        break
                
                if not found_similar:
                    missing_skills.append(job_skill)
        
        return missing_skills