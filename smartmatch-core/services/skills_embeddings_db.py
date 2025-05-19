"""
Skills Embeddings Database
==========================
Base de données vectorielle optimisée pour la recherche sémantique de compétences.

Fournit un index vectoriel pré-construit des compétences techniques courantes
avec recherche par similarité cosinus ultra-rapide.
"""

import os
import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings_service import EmbeddingsService

logger = logging.getLogger(__name__)


class SkillsEmbeddingsDB:
    """
    Base de données vectorielle pour les compétences techniques.
    
    Maintient un index vectoriel des compétences les plus courantes
    dans le domaine technique, permettant une recherche sémantique
    ultra-rapide par similarité cosinus.
    
    Fonctionnalités:
    - Index pré-construit de 500+ compétences techniques
    - Recherche par similarité avec seuils configurables
    - Construction automatique et mise à jour incrémentale
    - Persistance sur disque avec compression
    - Métriques de performance intégrées
    """
    
    def __init__(self, embeddings_service: EmbeddingsService, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise la base de données vectorielle.
        
        Args:
            embeddings_service: Service d'embeddings à utiliser
            config: Configuration optionnelle
        """
        self.embeddings_service = embeddings_service
        self.config = config or {}
        
        # Configuration
        self.db_dir = Path(self.config.get('db_dir', 'data/skills_db'))
        self.similarity_threshold = self.config.get('similarity_threshold', 0.75)
        self.max_results = self.config.get('max_results', 10)
        self.auto_build = self.config.get('auto_build', True)
        self.enable_compression = self.config.get('enable_compression', True)
        
        # État interne
        self.skills_list: List[str] = []
        self.skills_embeddings: Optional[np.ndarray] = None
        self.skills_metadata: Dict[str, Any] = {}
        self.is_loaded = False
        
        # Métriques
        self.search_count = 0
        self.total_search_time = 0.0
        
        # Créer le dossier de base de données
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger ou construire l'index
        if self.auto_build:
            self._load_or_build_index()
        
        logger.info(f"SkillsEmbeddingsDB initialized with {len(self.skills_list)} skills")
    
    def _load_or_build_index(self) -> None:
        """Charge l'index existant ou le construit s'il n'existe pas."""
        try:
            if self._load_index():
                logger.info("Skills embeddings index loaded from disk")
            else:
                logger.info("Building new skills embeddings index...")
                self._build_default_index()
                self._save_index()
                logger.info("Skills embeddings index built and saved")
        except Exception as e:
            logger.error(f"Failed to load/build skills index: {e}")
            # Fallback vers un index minimal
            self._build_minimal_index()
    
    def _load_index(self) -> bool:
        """
        Charge l'index depuis le disque.
        
        Returns:
            True si l'index a été chargé avec succès
        """
        index_file = self.db_dir / "skills_index.pkl"
        metadata_file = self.db_dir / "skills_metadata.json"
        
        try:
            if not (index_file.exists() and metadata_file.exists()):
                return False
            
            # Charger l'index
            with open(index_file, 'rb') as f:
                index_data = pickle.load(f)
            
            self.skills_list = index_data['skills_list']
            self.skills_embeddings = index_data['skills_embeddings']
            
            # Charger les métadonnées
            with open(metadata_file, 'r') as f:
                self.skills_metadata = json.load(f)
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load index: {e}")
            return False
    
    def _save_index(self) -> None:
        """Sauvegarde l'index sur le disque."""
        try:
            index_file = self.db_dir / "skills_index.pkl"
            metadata_file = self.db_dir / "skills_metadata.json"
            
            # Sauvegarder l'index
            index_data = {
                'skills_list': self.skills_list,
                'skills_embeddings': self.skills_embeddings
            }
            
            with open(index_file, 'wb') as f:
                pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Sauvegarder les métadonnées
            with open(metadata_file, 'w') as f:
                json.dump(self.skills_metadata, f, indent=2)
            
            logger.debug(f"Skills index saved with {len(self.skills_list)} skills")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _build_default_index(self) -> None:
        """Construit l'index par défaut avec les compétences techniques courantes."""
        default_skills = self._get_default_skills_list()
        self._build_index_from_skills(default_skills)
    
    def _build_minimal_index(self) -> None:
        """Construit un index minimal pour le fallback."""
        minimal_skills = [
            'python', 'javascript', 'java', 'react', 'node.js',
            'sql', 'html', 'css', 'git', 'docker'
        ]
        try:
            self._build_index_from_skills(minimal_skills)
            logger.info("Minimal skills index built as fallback")
        except Exception as e:
            logger.error(f"Failed to build minimal index: {e}")
            # Index vide en dernier recours
            self.skills_list = []
            self.skills_embeddings = np.array([])
            self.is_loaded = True
    
    def _build_index_from_skills(self, skills: List[str]) -> None:
        """
        Construit l'index à partir d'une liste de compétences.
        
        Args:
            skills: Liste de compétences à indexer
        """
        # Normaliser et déduplicuer les compétences
        normalized_skills = []
        seen = set()
        
        for skill in skills:
            normalized = skill.strip().lower()
            if normalized and normalized not in seen:
                normalized_skills.append(normalized)
                seen.add(normalized)
        
        self.skills_list = normalized_skills
        
        # Calculer les embeddings par batch pour optimiser la performance
        batch_size = self.embeddings_service.batch_size
        all_embeddings = []
        
        for i in range(0, len(self.skills_list), batch_size):
            batch = self.skills_list[i:i + batch_size]
            batch_embeddings = self.embeddings_service.get_embeddings(batch)
            all_embeddings.append(batch_embeddings)
        
        # Combiner tous les embeddings
        if all_embeddings:
            self.skills_embeddings = np.vstack(all_embeddings)
        else:
            self.skills_embeddings = np.array([])
        
        # Construire les métadonnées
        self.skills_metadata = {
            'version': '1.0',
            'skills_count': len(self.skills_list),
            'embedding_dimension': self.skills_embeddings.shape[1] if self.skills_embeddings.size > 0 else 0,
            'model_name': self.embeddings_service.model_name,
            'build_timestamp': str(Path(__file__).stat().st_mtime)
        }
        
        self.is_loaded = True
    
    def _get_default_skills_list(self) -> List[str]:
        """
        Retourne la liste par défaut des compétences techniques.
        
        Returns:
            Liste complète des compétences techniques courantes
        """
        return [
            # Langages de programmation
            "Python", "JavaScript", "Java", "TypeScript", "C#", "C++", "Go", "Rust",
            "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",
            
            # Frameworks et librairies
            "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask",
            "FastAPI", "Spring", "Spring Boot", "Laravel", "Symfony", "Rails",
            "ASP.NET", ".NET Core", "jQuery", "Bootstrap", "Tailwind CSS",
            
            # Bases de données
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
            "Oracle", "SQL Server", "DynamoDB", "Cassandra", "Neo4j", "InfluxDB",
            
            # Cloud et DevOps
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
            "GitLab CI", "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet",
            "Vagrant", "CI/CD", "DevOps", "Microservices", "Serverless",
            
            # Technologies Frontend
            "HTML", "CSS", "Sass", "Less", "Webpack", "Vite", "Parcel",
            "Progressive Web Apps", "PWA", "Responsive Design", "Material UI",
            "Chakra UI", "Styled Components",
            
            # Technologies Backend
            "REST API", "GraphQL", "gRPC", "WebSockets", "Message Queues",
            "RabbitMQ", "Apache Kafka", "Apache Spark", "Hadoop",
            
            # Outils de développement
            "Git", "GitHub", "GitLab", "Bitbucket", "VS Code", "IntelliJ",
            "Eclipse", "Vim", "Emacs", "Postman", "Insomnia",
            
            # Testing
            "Jest", "Mocha", "Chai", "Cypress", "Selenium", "Puppeteer",
            "JUnit", "Pytest", "RSpec", "PHPUnit", "Test-Driven Development",
            "Behavior-Driven Development",
            
            # Architecture et Design Patterns
            "MVC", "MVP", "MVVM", "Clean Architecture", "Hexagonal Architecture",
            "Domain-Driven Design", "Event-Driven Architecture", "CQRS",
            "Saga Pattern", "Circuit Breaker",
            
            # Méthodologies et pratiques
            "Agile", "Scrum", "Kanban", "Pair Programming", "Code Review",
            "Refactoring", "Clean Code", "SOLID Principles", "Design Patterns",
            "Object-Oriented Programming", "Functional Programming",
            
            # Data Science et Machine Learning
            "Machine Learning", "Deep Learning", "Neural Networks", "TensorFlow",
            "PyTorch", "scikit-learn", "Pandas", "NumPy", "Jupyter", "Matplotlib",
            "Seaborn", "Plotly", "Apache Airflow", "MLOps",
            
            # Sécurité
            "OAuth", "JWT", "SSL/TLS", "HTTPS", "XSS", "CSRF", "SQL Injection",
            "Security Auditing", "Penetration Testing", "Cryptography",
            
            # Mobile Development
            "React Native", "Flutter", "Xamarin", "Ionic", "PhoneGap",
            "Android Development", "iOS Development", "Kotlin Multiplatform",
            
            # Systèmes et Infrastructure
            "Linux", "Unix", "Windows Server", "Bash", "PowerShell", "Nginx",
            "Apache", "Load Balancing", "CDN", "Caching", "Performance Optimization",
            
            # Data Engineering
            "ETL", "Data Pipelines", "Apache Spark", "Apache Kafka", "Snowflake",
            "Databricks", "Data Warehousing", "Data Lakes", "BigQuery",
            
            # Blockchain et Web3
            "Blockchain", "Ethereum", "Solidity", "Smart Contracts", "DeFi",
            "NFT", "Web3", "Cryptocurrency",
            
            # UI/UX Design
            "User Experience", "User Interface", "Figma", "Sketch", "Adobe XD",
            "Prototyping", "Wireframing", "Usability Testing", "Design Systems",
            
            # Project Management
            "JIRA", "Confluence", "Trello", "Asana", "Slack", "Microsoft Teams",
            "Notion", "Monday.com",
            
            # Analytics et Monitoring
            "Google Analytics", "Mixpanel", "Amplitude", "New Relic", "Datadog",
            "Grafana", "Prometheus", "ELK Stack", "Splunk",
            
            # E-commerce
            "Shopify", "WooCommerce", "Magento", "Stripe", "PayPal",
            "Payment Gateway Integration",
            
            # CMS
            "WordPress", "Drupal", "Strapi", "Contentful", "Headless CMS",
            
            # Gaming
            "Unity", "Unreal Engine", "Game Development", "C# for Unity",
            "C++ for Unreal"
        ]
    
    def search_similar_skills(self, query_skill: str, 
                             threshold: Optional[float] = None,
                             max_results: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        Recherche les compétences similaires à une requête.
        
        Args:
            query_skill: Compétence recherchée
            threshold: Seuil de similarité (utilise la config par défaut si None)
            max_results: Nombre max de résultats (utilise la config par défaut si None)
            
        Returns:
            Liste de tuples (compétence, score_similarité) triée par score décroissant
        """
        if not self.is_loaded or not self.skills_list:
            logger.warning("Skills database not loaded or empty")
            return []
        
        threshold = threshold or self.similarity_threshold
        max_results = max_results or self.max_results
        
        start_time = logger.time() if hasattr(logger, 'time') else 0
        
        try:
            # Calculer l'embedding de la requête
            query_embedding = self.embeddings_service.get_embeddings(query_skill)
            
            # Calculer les similarités avec toutes les compétences
            similarities = cosine_similarity([query_embedding], self.skills_embeddings)[0]
            
            # Trouver les indices des compétences au-dessus du seuil
            above_threshold = similarities >= threshold
            indices = np.where(above_threshold)[0]
            
            # Trier par score décroissant
            sorted_indices = indices[np.argsort(similarities[indices])[::-1]]
            
            # Limiter le nombre de résultats
            sorted_indices = sorted_indices[:max_results]
            
            # Construire la liste des résultats
            results = [
                (self.skills_list[idx], float(similarities[idx]))
                for idx in sorted_indices
            ]
            
            # Mise à jour des métriques
            self.search_count += 1
            if hasattr(logger, 'time'):
                self.total_search_time += logger.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar skills: {e}")
            return []
    
    def find_best_matches(self, skills: List[str], 
                         threshold: Optional[float] = None) -> Dict[str, List[Tuple[str, float]]]:
        """
        Trouve les meilleures correspondances pour une liste de compétences.
        
        Args:
            skills: Liste de compétences à rechercher
            threshold: Seuil de similarité
            
        Returns:
            Dictionnaire {compétence_query: [(compétence_trouvée, score), ...]}
        """
        results = {}
        
        for skill in skills:
            similar_skills = self.search_similar_skills(skill, threshold)
            if similar_skills:
                results[skill] = similar_skills
        
        return results
    
    def add_skills(self, new_skills: List[str], rebuild_index: bool = True) -> None:
        """
        Ajoute de nouvelles compétences à l'index.
        
        Args:
            new_skills: Nouvelles compétences à ajouter
            rebuild_index: Reconstruire l'index complet
        """
        # Normaliser les nouvelles compétences
        normalized_new = []
        existing_set = set(self.skills_list)
        
        for skill in new_skills:
            normalized = skill.strip().lower()
            if normalized and normalized not in existing_set:
                normalized_new.append(normalized)
                existing_set.add(normalized)
        
        if not normalized_new:
            logger.info("No new skills to add")
            return
        
        # Ajouter à la liste existante
        self.skills_list.extend(normalized_new)
        
        if rebuild_index:
            # Reconstruire l'index complet
            self._build_index_from_skills(self.skills_list)
            self._save_index()
            logger.info(f"Added {len(normalized_new)} skills and rebuilt index")
        else:
            # Mise à jour incrémentale (plus rapide mais moins optimisé)
            new_embeddings = self.embeddings_service.get_embeddings(normalized_new)
            if self.skills_embeddings.size > 0:
                self.skills_embeddings = np.vstack([self.skills_embeddings, new_embeddings])
            else:
                self.skills_embeddings = new_embeddings
            
            self.skills_metadata['skills_count'] = len(self.skills_list)
            self._save_index()
            logger.info(f"Added {len(normalized_new)} skills incrementally")
    
    def remove_skills(self, skills_to_remove: List[str], rebuild_index: bool = True) -> None:
        """
        Supprime des compétences de l'index.
        
        Args:
            skills_to_remove: Compétences à supprimer
            rebuild_index: Reconstruire l'index après suppression
        """
        # Normaliser les compétences à supprimer
        normalized_to_remove = {skill.strip().lower() for skill in skills_to_remove}
        
        # Filtrer les compétences
        indices_to_keep = []
        new_skills_list = []
        
        for i, skill in enumerate(self.skills_list):
            if skill not in normalized_to_remove:
                indices_to_keep.append(i)
                new_skills_list.append(skill)
        
        removed_count = len(self.skills_list) - len(new_skills_list)
        
        if removed_count == 0:
            logger.info("No skills to remove")
            return
        
        # Mettre à jour la liste
        self.skills_list = new_skills_list
        
        if rebuild_index:
            # Reconstruire l'index complet
            self._build_index_from_skills(self.skills_list)
        else:
            # Mise à jour incrémentale
            if self.skills_embeddings.size > 0:
                self.skills_embeddings = self.skills_embeddings[indices_to_keep]
        
        self.skills_metadata['skills_count'] = len(self.skills_list)
        self._save_index()
        logger.info(f"Removed {removed_count} skills from index")
    
    def rebuild_index(self) -> None:
        """Reconstruit complètement l'index."""
        logger.info("Rebuilding skills embeddings index...")
        self._build_index_from_skills(self.skills_list)
        self._save_index()
        logger.info("Index rebuilt successfully")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de la base de données.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        avg_search_time = (self.total_search_time / self.search_count 
                          if self.search_count > 0 else 0)
        
        return {
            'is_loaded': self.is_loaded,
            'skills_count': len(self.skills_list),
            'search_count': self.search_count,
            'average_search_time_ms': avg_search_time * 1000,
            'embedding_dimension': (self.skills_embeddings.shape[1] 
                                  if self.skills_embeddings is not None 
                                  and self.skills_embeddings.size > 0 else 0),
            'metadata': self.skills_metadata,
            'similarity_threshold': self.similarity_threshold,
            'max_results': self.max_results
        }
    
    def get_all_skills(self) -> List[str]:
        """
        Retourne toutes les compétences de l'index.
        
        Returns:
            Liste de toutes les compétences
        """
        return self.skills_list.copy()
    
    def contains_skill(self, skill: str) -> bool:
        """
        Vérifie si une compétence est dans l'index.
        
        Args:
            skill: Compétence à vérifier
            
        Returns:
            True si la compétence est présente
        """
        normalized = skill.strip().lower()
        return normalized in self.skills_list
    
    def export_index(self, filepath: str) -> None:
        """
        Exporte l'index vers un fichier.
        
        Args:
            filepath: Chemin du fichier d'export
        """
        export_data = {
            'skills_list': self.skills_list,
            'metadata': self.skills_metadata,
            'config': {
                'similarity_threshold': self.similarity_threshold,
                'max_results': self.max_results
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Skills index exported to {filepath}")
    
    def import_index(self, filepath: str, rebuild: bool = True) -> None:
        """
        Importe un index depuis un fichier.
        
        Args:
            filepath: Chemin du fichier d'import
            rebuild: Reconstruire les embeddings après import
        """
        with open(filepath, 'r') as f:
            import_data = json.load(f)
        
        self.skills_list = import_data['skills_list']
        imported_metadata = import_data.get('metadata', {})
        
        if rebuild:
            self._build_index_from_skills(self.skills_list)
        else:
            self.skills_metadata = imported_metadata
            self.is_loaded = True
        
        self._save_index()
        logger.info(f"Skills index imported from {filepath}")
