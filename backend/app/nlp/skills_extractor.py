import re
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
import logging

class SkillsKnowledgeBase:
    """
    Base de connaissances des compétences avec catégorisation
    """
    def __init__(self, skills_file: str = None):
        """
        Initialise la base de connaissances des compétences
        
        Args:
            skills_file: Chemin vers le fichier JSON de taxonomie (optionnel)
        """
        self.skills_by_category = {}
        self.all_skills = set()
        self.skill_to_category = {}
        self.synonyms = {}
        
        # Chemin par défaut
        if skills_file is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            skills_file = os.path.join(base_dir, "data", "skills_taxonomy.json")
        
        # Charger les compétences depuis le fichier
        self._load_skills(skills_file)
        
        # Fallback avec liste minimale si nécessaire
        if not self.all_skills:
            self._load_fallback_skills()
    
    def _load_skills(self, skills_file: str) -> None:
        """
        Charge la taxonomie de compétences depuis un fichier JSON
        
        Args:
            skills_file: Chemin vers le fichier JSON
        """
        skills_path = Path(skills_file)
        if skills_path.exists():
            try:
                with open(skills_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for category, skills in data.get("categories", {}).items():
                    self.skills_by_category[category] = set(skills)
                    for skill in skills:
                        self.all_skills.add(skill.lower())
                        self.skill_to_category[skill.lower()] = category
                
                # Charger les synonymes
                for main_skill, synonyms in data.get("synonyms", {}).items():
                    self.synonyms[main_skill.lower()] = synonyms
                    for synonym in synonyms:
                        self.synonyms[synonym.lower()] = [main_skill]
                        
                logging.info(f"Chargement réussi de {len(self.all_skills)} compétences depuis {skills_file}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de la taxonomie de compétences: {e}")
    
    def _load_fallback_skills(self) -> None:
        """
        Charge une liste minimale de compétences si le fichier n'est pas disponible
        """
        logging.info("Chargement de la liste de compétences par défaut")
        categories = {
            "langages_programmation": [
                "python", "java", "javascript", "c++", "c#", "ruby", "php",
                "typescript", "swift", "kotlin", "go", "rust", "scala"
            ],
            "technologies_web": [
                "html", "css", "react", "angular", "vue.js", "node.js", "django",
                "flask", "express", "spring", "laravel", "jquery", "bootstrap"
            ],
            "bases_donnees": [
                "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite",
                "cassandra", "redis", "elasticsearch", "neo4j"
            ],
            "cloud_devops": [
                "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins",
                "ansible", "terraform", "git", "github", "gitlab", "ci/cd"
            ],
            "data_science": [
                "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
                "pandas", "numpy", "r", "tableau", "power bi", "big data", "hadoop", "spark"
            ],
            "soft_skills": [
                "travail d'équipe", "communication", "résolution de problèmes",
                "gestion de projet", "leadership", "organisation", "adaptabilité"
            ]
        }
        
        for category, skills in categories.items():
            self.skills_by_category[category] = set(skills)
            for skill in skills:
                self.all_skills.add(skill.lower())
                self.skill_to_category[skill.lower()] = category
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait les compétences du texte avec catégorisation
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Compétences par catégorie
        """
        text_lower = text.lower()
        found_skills = {}
        
        # Extraction des compétences exactes
        for skill in self.all_skills:
            # Recherche de la compétence avec une frontière de mot
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                category = self.skill_to_category.get(skill, "autres")
                if category not in found_skills:
                    found_skills[category] = []
                
                # Normaliser vers la compétence principale si c'est un synonyme
                if skill in self.synonyms and self.synonyms[skill]:
                    main_skill = self.synonyms[skill][0]
                    if main_skill not in found_skills[category]:
                        found_skills[category].append(main_skill)
                else:
                    if skill not in found_skills[category]:
                        found_skills[category].append(skill)
        
        # Recherche de patterns spécifiques (versions, années d'expérience)
        experience_patterns = [
            (r'(\d+)\s+ans?\s+(?:d\'expérience)?\s+(?:en|avec|de)\s+([a-zA-Z0-9\+\#\.]+)',
             lambda m: (m.group(2).lower(), f"{m.group(2)} ({m.group(1)} ans)")),
            (r'([a-zA-Z]+)\s+(\d+\.\d+)', 
             lambda m: (m.group(1).lower(), f"{m.group(1)} {m.group(2)}"))
        ]
        
        for pattern, formatter in experience_patterns:
            for match in re.finditer(pattern, text_lower):
                skill_base, formatted_skill = formatter(match)
                
                # Vérifier si c'est une compétence connue
                if any(skill_base in skill for skill in self.all_skills):
                    category = next((self.skill_to_category.get(skill) for skill in self.all_skills 
                                    if skill_base in skill), "autres")
                    
                    if category not in found_skills:
                        found_skills[category] = []
                    
                    if formatted_skill not in found_skills[category]:
                        found_skills[category].append(formatted_skill)
        
        return found_skills
    
    def extract_skills_from_section(self, section_text: List[str]) -> Dict[str, List[str]]:
        """
        Extrait les compétences d'une section spécifique (comme "compétences")
        
        Args:
            section_text: Liste des lignes de la section
            
        Returns:
            Dict: Compétences par catégorie
        """
        # Joindre les lignes de la section
        full_text = " ".join(section_text)
        
        # Extraction basique
        skills_by_category = self.extract_skills(full_text)
        
        # Extraction des éléments de liste (points, tirets, etc.)
        list_items = []
        for line in section_text:
            # Détecter les éléments de liste
            if re.match(r'^\s*[•\-\*\+]\s+', line):
                clean_item = re.sub(r'^\s*[•\-\*\+]\s+', '', line).strip()
                list_items.append(clean_item)
        
        # Analyser chaque élément de liste
        for item in list_items:
            item_skills = self.extract_skills(item)
            
            # Si aucune compétence connue n'est trouvée dans l'élément,
            # le considérer comme une compétence potentielle
            if not any(item_skills.values()):
                # Vérifier si c'est une compétence valide (pas trop longue, pas trop courte)
                if 2 <= len(item.split()) <= 5:
                    if "autres" not in skills_by_category:
                        skills_by_category["autres"] = []
                    skills_by_category["autres"].append(item)
            else:
                # Fusionner avec les résultats existants
                for category, skills in item_skills.items():
                    if category not in skills_by_category:
                        skills_by_category[category] = []
                    for skill in skills:
                        if skill not in skills_by_category[category]:
                            skills_by_category[category].append(skill)
        
        return skills_by_category


def create_skills_taxonomy_template():
    """
    Crée un fichier modèle de taxonomie des compétences
    """
    template = {
        "categories": {
            "langages_programmation": [
                "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP",
                "TypeScript", "Swift", "Kotlin", "Go", "Rust", "Scala"
            ],
            "technologies_web": [
                "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django",
                "Flask", "Express", "Spring", "Laravel", "jQuery", "Bootstrap"
            ],
            "bases_donnees": [
                "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite",
                "Cassandra", "Redis", "Elasticsearch", "Neo4j"
            ],
            "cloud_devops": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
                "Ansible", "Terraform", "Git", "GitHub", "GitLab", "CI/CD"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn",
                "Pandas", "NumPy", "R", "Tableau", "Power BI", "Big Data", "Hadoop", "Spark"
            ],
            "soft_skills": [
                "Travail d'équipe", "Communication", "Résolution de problèmes",
                "Gestion de projet", "Leadership", "Organisation", "Adaptabilité"
            ]
        },
        "synonyms": {
            "Python": ["py", "python3"],
            "JavaScript": ["JS", "ECMAScript"],
            "Machine Learning": ["ML", "apprentissage automatique"],
            "Deep Learning": ["DL", "apprentissage profond"],
            "Gestion de projet": ["project management", "management de projet"]
        }
    }
    
    # Créer le répertoire data s'il n'existe pas
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Écrire le fichier modèle
    file_path = os.path.join(data_dir, "skills_taxonomy.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Fichier modèle de taxonomie créé: {file_path}")
