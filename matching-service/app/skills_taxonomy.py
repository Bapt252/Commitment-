"""
Taxonomie enrichie des compétences pour Nexten SmartMatch
-------------------------------------------------------
Ce module définit une taxonomie hiérarchique des compétences techniques
pour améliorer l'analyse sémantique et le matching des compétences.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import json
import os
import logging
from typing import Dict, List, Any, Set

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillsTaxonomy:
    """
    Classe gérant une taxonomie hiérarchique des compétences techniques,
    avec support pour le chargement/sauvegarde de fichiers JSON.
    """
    
    def __init__(self, taxonomy_file: str = None):
        """
        Initialise la taxonomie des compétences
        
        Args:
            taxonomy_file: Chemin du fichier JSON de taxonomie (optionnel)
        """
        # Taxonomie par défaut et étendue
        self.taxonomy = self._get_default_taxonomy()
        
        # Si un fichier est fourni, charger la taxonomie depuis ce fichier
        if taxonomy_file and os.path.exists(taxonomy_file):
            self.load_from_file(taxonomy_file)
        
        # Stocker le chemin du fichier pour des sauvegardes ultérieures
        self.taxonomy_file = taxonomy_file
        
        # Indexer les synonymes pour une recherche rapide
        self._build_synonyms_index()
        
        logger.info(f"Taxonomie des compétences initialisée avec {len(self.taxonomy)} entrées")
    
    def _get_default_taxonomy(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne la taxonomie par défaut des compétences
        
        Returns:
            Dict: Taxonomie par défaut
        """
        return {
            # CATÉGORIES PRINCIPALES
            "programming": {
                "type": "category",
                "related": ["development", "coding", "software engineering"],
                "children": ["python", "javascript", "java", "c++", "c#", "ruby", "php", "go", "rust", "typescript", "kotlin", "swift"]
            },
            "web_development": {
                "type": "category",
                "related": ["frontend", "backend", "full-stack", "web design"],
                "children": ["frontend", "backend", "fullstack", "web_frameworks", "web_design"]
            },
            "data_science": {
                "type": "category",
                "related": ["machine learning", "statistics", "analytics", "big data"],
                "children": ["machine_learning", "statistics", "data_analysis", "data_visualization", "big_data"]
            },
            "devops": {
                "type": "category",
                "related": ["infrastructure", "cloud", "automation", "sre"],
                "children": ["cloud_platforms", "ci_cd", "containerization", "infrastructure_as_code", "monitoring"]
            },
            "databases": {
                "type": "category",
                "related": ["data storage", "data management", "sql", "nosql"],
                "children": ["sql_databases", "nosql_databases", "database_design", "query_languages"]
            },
            "mobile_development": {
                "type": "category",
                "related": ["app development", "ios", "android", "cross-platform"],
                "children": ["ios", "android", "cross_platform", "mobile_frameworks"]
            },
            "security": {
                "type": "category",
                "related": ["cybersecurity", "infosec", "application security", "network security"],
                "children": ["application_security", "network_security", "security_tools", "cryptography", "secure_coding"]
            },
            
            # LANGAGES DE PROGRAMMATION
            "python": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["py", "python3"],
                "related": ["django", "flask", "data science", "machine learning", "automation"],
                "children": ["django", "flask", "fastapi", "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn"]
            },
            "javascript": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["js", "ecmascript"],
                "related": ["frontend", "web development", "node.js"],
                "children": ["react", "vue", "angular", "node.js", "express", "next.js", "nuxt.js"]
            },
            "typescript": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["ts"],
                "related": ["javascript", "angular", "type safety"],
                "children": []
            },
            "java": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["jdk", "jre"],
                "related": ["backend", "enterprise", "android"],
                "children": ["spring", "hibernate", "spring boot", "jakarta ee", "quarkus"]
            },
            "c++": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["cpp", "c plus plus"],
                "related": ["systems programming", "game development", "embedded systems"],
                "children": ["qt", "boost", "stl", "unreal engine"]
            },
            "c#": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["csharp", "c sharp", "net", ".net"],
                "related": ["microsoft", ".net", "unity"],
                "children": ["asp.net", "entity framework", "xamarin", "unity", "wpf", "uwp"]
            },
            "ruby": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["rb"],
                "related": ["web development", "ruby on rails", "scripting"],
                "children": ["ruby on rails", "sinatra", "rspec"]
            },
            "php": {
                "type": "technical",
                "parent": "programming",
                "synonyms": [],
                "related": ["web development", "backend", "wordpress"],
                "children": ["laravel", "symfony", "wordpress", "drupal", "magento"]
            },
            "go": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["golang"],
                "related": ["backend", "microservices", "cloud native"],
                "children": ["gin", "echo", "fiber"]
            },
            "rust": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["rs"],
                "related": ["systems programming", "memory safety", "high performance"],
                "children": ["tokio", "actix", "rocket"]
            },
            "kotlin": {
                "type": "technical",
                "parent": "programming",
                "synonyms": ["kt"],
                "related": ["android", "java", "mobile development"],
                "children": ["ktor", "spring boot kotlin", "android kotlin"]
            },
            "swift": {
                "type": "technical",
                "parent": "programming",
                "synonyms": [],
                "related": ["ios", "macos", "apple", "mobile development"],
                "children": ["uikit", "swiftui", "cocoa touch"]
            },
            
            # FRAMEWORKS WEB
            "frontend": {
                "type": "category",
                "parent": "web_development",
                "synonyms": ["front-end", "client-side"],
                "related": ["ui", "ux", "web design", "html", "css", "javascript"],
                "children": ["html", "css", "javascript", "react", "vue", "angular"]
            },
            "backend": {
                "type": "category",
                "parent": "web_development",
                "synonyms": ["back-end", "server-side"],
                "related": ["api", "databases", "server", "rest"],
                "children": ["node.js", "django", "spring", "laravel", "express", "fastapi", "flask"]
            },
            "fullstack": {
                "type": "category",
                "parent": "web_development",
                "synonyms": ["full-stack", "full stack"],
                "related": ["frontend", "backend", "web development"],
                "children": []
            },
            "web_frameworks": {
                "type": "category",
                "parent": "web_development",
                "related": ["frontend frameworks", "backend frameworks", "web development"],
                "children": ["react", "vue", "angular", "django", "spring", "laravel", "ruby on rails"]
            },
            "web_design": {
                "type": "category",
                "parent": "web_development",
                "related": ["ui", "ux", "graphic design", "frontend"],
                "children": ["ui", "ux", "responsive design", "css"]
            },
            
            # FRAMEWORKS SPÉCIFIQUES
            "react": {
                "type": "technical",
                "parent": "frontend",
                "synonyms": ["reactjs", "react.js"],
                "related": ["javascript", "jsx", "frontend", "single page application"],
                "children": ["redux", "react router", "next.js", "react native"]
            },
            "vue": {
                "type": "technical",
                "parent": "frontend",
                "synonyms": ["vuejs", "vue.js"],
                "related": ["javascript", "frontend", "single page application"],
                "children": ["vuex", "vue router", "nuxt.js"]
            },
            "angular": {
                "type": "technical",
                "parent": "frontend",
                "synonyms": ["angularjs", "angular.js"],
                "related": ["typescript", "frontend", "single page application"],
                "children": ["rxjs", "ngxs", "ngrx"]
            },
            "node.js": {
                "type": "technical",
                "parent": "backend",
                "synonyms": ["nodejs", "node"],
                "related": ["javascript", "backend", "server-side javascript"],
                "children": ["express", "nest.js", "socket.io", "mongoose"]
            },
            "django": {
                "type": "technical",
                "parent": "backend",
                "synonyms": [],
                "related": ["python", "backend", "web framework"],
                "children": ["django rest framework", "django orm", "django templates"]
            },
            "spring": {
                "type": "technical",
                "parent": "backend",
                "synonyms": ["spring framework"],
                "related": ["java", "enterprise", "backend"],
                "children": ["spring boot", "spring mvc", "spring security", "spring data"]
            },
            "laravel": {
                "type": "technical",
                "parent": "backend",
                "synonyms": [],
                "related": ["php", "backend", "web framework"],
                "children": ["blade", "eloquent", "artisan"]
            },
            
            # DATA SCIENCE
            "machine_learning": {
                "type": "category",
                "parent": "data_science",
                "synonyms": ["ml", "ai", "artificial intelligence"],
                "related": ["deep learning", "neural networks", "data science"],
                "children": ["supervised_learning", "unsupervised_learning", "reinforcement_learning", "deep_learning"]
            },
            "supervised_learning": {
                "type": "technical",
                "parent": "machine_learning",
                "related": ["classification", "regression", "machine learning"],
                "children": ["classification", "regression"]
            },
            "unsupervised_learning": {
                "type": "technical",
                "parent": "machine_learning",
                "related": ["clustering", "dimensionality reduction", "machine learning"],
                "children": ["clustering", "dimensionality reduction"]
            },
            "deep_learning": {
                "type": "technical",
                "parent": "machine_learning",
                "synonyms": ["dl"],
                "related": ["neural networks", "tensorflow", "pytorch", "machine learning"],
                "children": ["neural_networks", "cnn", "rnn", "transformer_models"]
            },
            "neural_networks": {
                "type": "technical",
                "parent": "deep_learning",
                "synonyms": ["nn", "neural nets"],
                "related": ["deep learning", "machine learning", "ai"],
                "children": ["cnn", "rnn", "gan", "transformer_models"]
            },
            "transformer_models": {
                "type": "technical",
                "parent": "neural_networks",
                "related": ["nlp", "bert", "gpt", "deep learning"],
                "children": ["bert", "gpt", "t5", "llm"]
            },
            "llm": {
                "type": "technical",
                "parent": "transformer_models",
                "synonyms": ["large language models", "language models"],
                "related": ["nlp", "gpt", "transformers", "ai"],
                "children": ["gpt", "llama", "claude", "palm"]
            },
            
            # DEVOPS ET CLOUD
            "cloud_platforms": {
                "type": "category",
                "parent": "devops",
                "related": ["aws", "azure", "gcp", "cloud computing"],
                "children": ["aws", "azure", "gcp", "alibaba_cloud", "ibm_cloud"]
            },
            "aws": {
                "type": "technical",
                "parent": "cloud_platforms",
                "synonyms": ["amazon web services", "amazon aws"],
                "related": ["cloud", "amazon", "iaas", "paas"],
                "children": ["ec2", "s3", "lambda", "rds", "dynamodb", "sqs", "sns"]
            },
            "azure": {
                "type": "technical",
                "parent": "cloud_platforms",
                "synonyms": ["microsoft azure"],
                "related": ["cloud", "microsoft", "iaas", "paas"],
                "children": ["azure functions", "azure vm", "cosmos db", "azure storage"]
            },
            "gcp": {
                "type": "technical",
                "parent": "cloud_platforms",
                "synonyms": ["google cloud platform", "google cloud"],
                "related": ["cloud", "google", "iaas", "paas"],
                "children": ["gce", "gcs", "bigquery", "cloud functions", "app engine"]
            },
            "ci_cd": {
                "type": "category",
                "parent": "devops",
                "synonyms": ["continuous integration", "continuous deployment", "continuous delivery"],
                "related": ["automation", "devops", "testing"],
                "children": ["jenkins", "travis_ci", "circle_ci", "github_actions", "gitlab_ci"]
            },
            "containerization": {
                "type": "category",
                "parent": "devops",
                "related": ["docker", "kubernetes", "containers", "microservices"],
                "children": ["docker", "kubernetes", "container_orchestration"]
            },
            "docker": {
                "type": "technical",
                "parent": "containerization",
                "synonyms": ["docker containers"],
                "related": ["containers", "devops", "microservices"],
                "children": ["docker-compose", "dockerfile", "docker swarm"]
            },
            "kubernetes": {
                "type": "technical",
                "parent": "containerization",
                "synonyms": ["k8s", "kube"],
                "related": ["container orchestration", "docker", "microservices", "cloud native"],
                "children": ["kubectl", "helm", "operators", "istio"]
            },
            
            # BASES DE DONNÉES
            "sql_databases": {
                "type": "category",
                "parent": "databases",
                "synonyms": ["relational databases", "rdbms"],
                "related": ["sql", "relational", "data storage"],
                "children": ["mysql", "postgresql", "sql_server", "oracle", "sqlite"]
            },
            "nosql_databases": {
                "type": "category",
                "parent": "databases",
                "synonyms": ["non-relational databases"],
                "related": ["document store", "key-value", "graph databases", "columnar"],
                "children": ["mongodb", "cassandra", "redis", "dynamodb", "couchbase", "neo4j"]
            },
            "postgresql": {
                "type": "technical",
                "parent": "sql_databases",
                "synonyms": ["postgres", "pg"],
                "related": ["sql", "relational database", "data storage"],
                "children": ["postgis", "postgresql extensions"]
            },
            "mongodb": {
                "type": "technical",
                "parent": "nosql_databases",
                "synonyms": ["mongo"],
                "related": ["document database", "nosql", "json", "data storage"],
                "children": ["mongoose", "mongodb atlas", "mongodb compass"]
            },
            
            # DÉVELOPPEMENT MOBILE
            "ios": {
                "type": "technical",
                "parent": "mobile_development",
                "synonyms": ["iphone", "ipad", "apple mobile"],
                "related": ["mobile", "apple", "swift", "objective-c"],
                "children": ["swift", "objective-c", "uikit", "swiftui", "xcode"]
            },
            "android": {
                "type": "technical",
                "parent": "mobile_development",
                "synonyms": ["android os", "android sdk"],
                "related": ["mobile", "google", "java", "kotlin"],
                "children": ["android sdk", "android studio", "kotlin", "java android", "jetpack compose"]
            },
            "cross_platform": {
                "type": "category",
                "parent": "mobile_development",
                "related": ["hybrid", "multi-platform", "mobile"],
                "children": ["react_native", "flutter", "xamarin", "ionic"]
            },
            "react_native": {
                "type": "technical",
                "parent": "cross_platform",
                "synonyms": ["rn"],
                "related": ["react", "javascript", "mobile", "cross-platform"],
                "children": ["expo", "react navigation", "redux"]
            },
            "flutter": {
                "type": "technical",
                "parent": "cross_platform",
                "synonyms": [],
                "related": ["dart", "mobile", "cross-platform", "ui framework"],
                "children": ["dart", "flutter widgets", "bloc", "provider"]
            },
            
            # SÉCURITÉ
            "application_security": {
                "type": "category",
                "parent": "security",
                "related": ["appsec", "secure coding", "web security"],
                "children": ["owasp", "authentication", "authorization", "data_encryption"]
            },
            "network_security": {
                "type": "category",
                "parent": "security",
                "related": ["firewalls", "vpn", "intrusion detection", "network protocols"],
                "children": ["firewalls", "vpn", "ids_ips", "network_monitoring"]
            },
            "security_tools": {
                "type": "category",
                "parent": "security",
                "related": ["vulnerability scanners", "pentest", "siem"],
                "children": ["vulnerability_scanners", "penetration_testing", "siem", "threat_intelligence"]
            }
        }
    
    def _build_synonyms_index(self):
        """
        Construit un index des synonymes pour une recherche rapide
        """
        self.synonyms_index = {}
        
        # Ajouter les synonymes directs et les variantes
        for skill_name, skill_info in self.taxonomy.items():
            # Ajouter le nom principal (en minuscules)
            self.synonyms_index[skill_name.lower()] = skill_name
            
            # Ajouter les synonymes explicites
            for synonym in skill_info.get("synonyms", []):
                self.synonyms_index[synonym.lower()] = skill_name
            
            # Traiter les variantes orthographiques communes
            variants = self._generate_common_variants(skill_name)
            for variant in variants:
                if variant.lower() not in self.synonyms_index:
                    self.synonyms_index[variant.lower()] = skill_name
    
    def _generate_common_variants(self, skill_name: str) -> List[str]:
        """
        Génère des variantes orthographiques communes pour une compétence
        
        Args:
            skill_name: Nom de la compétence
            
        Returns:
            List[str]: Liste des variantes
        """
        variants = []
        
        # Remplacer les espaces par des traits d'union ou des underscores
        if " " in skill_name:
            variants.append(skill_name.replace(" ", "-"))
            variants.append(skill_name.replace(" ", "_"))
        
        # Remplacer les traits d'union par des espaces ou des underscores
        if "-" in skill_name:
            variants.append(skill_name.replace("-", " "))
            variants.append(skill_name.replace("-", "_"))
        
        # Remplacer les underscores par des espaces ou des traits d'union
        if "_" in skill_name:
            variants.append(skill_name.replace("_", " "))
            variants.append(skill_name.replace("_", "-"))
        
        # Ajouter des versions avec/sans ".js"
        if skill_name.endswith(".js"):
            variants.append(skill_name[:-3])
        elif skill_name.lower() in ["react", "vue", "angular", "node"]:
            variants.append(f"{skill_name}.js")
        
        return variants
    
    def get_canonical_skill_name(self, skill: str) -> str:
        """
        Retourne le nom canonique d'une compétence à partir d'une variante
        
        Args:
            skill: Variante du nom de la compétence
            
        Returns:
            str: Nom canonique ou le nom original si non trouvé
        """
        return self.synonyms_index.get(skill.lower(), skill)
    
    def get_related_skills(self, skill: str) -> List[str]:
        """
        Retourne une liste de compétences reliées à une compétence donnée
        
        Args:
            skill: Nom de la compétence
            
        Returns:
            List[str]: Liste des compétences reliées
        """
        # Normaliser le nom de la compétence
        canonical_name = self.get_canonical_skill_name(skill)
        skill_info = self.taxonomy.get(canonical_name)
        
        if not skill_info:
            # Chercher si c'est un enfant d'une catégorie
            for category, info in self.taxonomy.items():
                if "children" in info and canonical_name in info["children"]:
                    # Récupérer le parent, les frères/sœurs et les compétences reliées
                    siblings = [child for child in info["children"] if child != canonical_name]
                    return [category] + siblings + info.get("related", [])
            
            # Si non trouvé, retourner une liste vide
            return []
        
        # Rassembler toutes les compétences reliées
        result = set()
        
        # Ajouter les compétences directement reliées
        for related in skill_info.get("related", []):
            result.add(related)
        
        # Ajouter les enfants
        for child in skill_info.get("children", []):
            result.add(child)
        
        # Ajouter le parent si défini
        if "parent" in skill_info:
            result.add(skill_info["parent"])
            
            # Ajouter les frères/sœurs (autres enfants du même parent)
            parent_info = self.taxonomy.get(skill_info["parent"])
            if parent_info and "children" in parent_info:
                for sibling in parent_info["children"]:
                    if sibling != canonical_name:
                        result.add(sibling)
        
        return list(result)
    
    def get_skill_info(self, skill: str) -> Dict[str, Any]:
        """
        Retourne les informations complètes sur une compétence
        
        Args:
            skill: Nom de la compétence
            
        Returns:
            Dict: Informations sur la compétence ou None si non trouvée
        """
        # Normaliser le nom de la compétence
        canonical_name = self.get_canonical_skill_name(skill)
        return self.taxonomy.get(canonical_name)
    
    def get_all_skills(self) -> List[str]:
        """
        Retourne la liste de toutes les compétences dans la taxonomie
        
        Returns:
            List[str]: Liste des noms de compétences
        """
        return list(self.taxonomy.keys())
    
    def add_skill(self, skill_name: str, skill_info: Dict[str, Any]) -> bool:
        """
        Ajoute une nouvelle compétence à la taxonomie
        
        Args:
            skill_name: Nom de la compétence
            skill_info: Informations sur la compétence
            
        Returns:
            bool: True si ajoutée avec succès, False sinon
        """
        if skill_name in self.taxonomy:
            logger.warning(f"La compétence '{skill_name}' existe déjà dans la taxonomie")
            return False
        
        # Ajouter la compétence
        self.taxonomy[skill_name] = skill_info
        
        # Mettre à jour l'index des synonymes
        self.synonyms_index[skill_name.lower()] = skill_name
        for synonym in skill_info.get("synonyms", []):
            self.synonyms_index[synonym.lower()] = skill_name
        
        # Ajouter les variantes orthographiques
        variants = self._generate_common_variants(skill_name)
        for variant in variants:
            if variant.lower() not in self.synonyms_index:
                self.synonyms_index[variant.lower()] = skill_name
        
        # Si un parent est spécifié, vérifier qu'il existe et ajouter l'enfant
        if "parent" in skill_info:
            parent_name = skill_info["parent"]
            if parent_name in self.taxonomy:
                if "children" not in self.taxonomy[parent_name]:
                    self.taxonomy[parent_name]["children"] = []
                if skill_name not in self.taxonomy[parent_name]["children"]:
                    self.taxonomy[parent_name]["children"].append(skill_name)
        
        # Sauvegarder si un fichier est défini
        if self.taxonomy_file:
            self.save_to_file(self.taxonomy_file)
        
        logger.info(f"Compétence '{skill_name}' ajoutée à la taxonomie")
        return True
    
    def update_skill(self, skill_name: str, skill_info: Dict[str, Any]) -> bool:
        """
        Met à jour une compétence existante dans la taxonomie
        
        Args:
            skill_name: Nom de la compétence
            skill_info: Nouvelles informations sur la compétence
            
        Returns:
            bool: True si mise à jour avec succès, False sinon
        """
        canonical_name = self.get_canonical_skill_name(skill_name)
        
        if canonical_name not in self.taxonomy:
            logger.warning(f"La compétence '{skill_name}' n'existe pas dans la taxonomie")
            return False
        
        # Supprimer l'ancienne entrée de l'index des synonymes
        old_info = self.taxonomy[canonical_name]
        for synonym in old_info.get("synonyms", []):
            if synonym.lower() in self.synonyms_index:
                del self.synonyms_index[synonym.lower()]
        
        # Mettre à jour les informations
        self.taxonomy[canonical_name] = skill_info
        
        # Mettre à jour l'index des synonymes
        for synonym in skill_info.get("synonyms", []):
            self.synonyms_index[synonym.lower()] = canonical_name
        
        # Sauvegarder si un fichier est défini
        if self.taxonomy_file:
            self.save_to_file(self.taxonomy_file)
        
        logger.info(f"Compétence '{canonical_name}' mise à jour dans la taxonomie")
        return True
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Charge la taxonomie depuis un fichier JSON
        
        Args:
            file_path: Chemin du fichier JSON
            
        Returns:
            bool: True si chargé avec succès, False sinon
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Vérifier le format
                if not isinstance(data, dict):
                    logger.error(f"Format de fichier invalide : {file_path}")
                    return False
                
                # Fusionner avec la taxonomie par défaut
                self.taxonomy.update(data)
                
                # Reconstruire l'index des synonymes
                self._build_synonyms_index()
                
                logger.info(f"Taxonomie chargée depuis {file_path} avec {len(self.taxonomy)} entrées")
                return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la taxonomie : {str(e)}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Sauvegarde la taxonomie dans un fichier JSON
        
        Args:
            file_path: Chemin du fichier JSON
            
        Returns:
            bool: True si sauvegardé avec succès, False sinon
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.taxonomy, f, indent=2)
                
            logger.info(f"Taxonomie sauvegardée dans {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la taxonomie : {str(e)}")
            return False

# Exemple d'utilisation
if __name__ == "__main__":
    taxonomy = SkillsTaxonomy()
    
    # Exemples d'utilisation
    python_related = taxonomy.get_related_skills("python")
    print(f"Compétences reliées à Python: {python_related}")
    
    # Test des variantes et synonymes
    print(f"Nom canonique pour 'js': {taxonomy.get_canonical_skill_name('js')}")
    print(f"Nom canonique pour 'react.js': {taxonomy.get_canonical_skill_name('react.js')}")
    
    # Ajouter une nouvelle compétence
    taxonomy.add_skill("svelte", {
        "type": "technical",
        "parent": "frontend",
        "synonyms": ["sveltejs", "svelte.js"],
        "related": ["javascript", "frontend", "reactive"],
        "children": ["svelte kit"]
    })
    
    # Vérifier que la compétence a été ajoutée
    svelte_info = taxonomy.get_skill_info("svelte")
    print(f"Informations sur Svelte: {svelte_info}")
    
    # Obtenir les compétences reliées à Svelte
    svelte_related = taxonomy.get_related_skills("svelte")
    print(f"Compétences reliées à Svelte: {svelte_related}")
