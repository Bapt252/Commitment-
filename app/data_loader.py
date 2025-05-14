"""Module pour charger les données des candidats et entreprises.
"""

import os
import json
import logging
import pandas as pd

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataLoader")

class DataLoader:
    """
    Classe pour charger les données des candidats et entreprises à partir de fichiers.
    """
    
    def __init__(self):
        """
        Initialise le chargeur de données.
        """
        logger.info("DataLoader initialisé")
    
    def load_candidates(self, file_path):
        """
        Charge les données des candidats à partir d'un fichier JSON ou CSV.
        
        Args:
            file_path (str): Chemin vers le fichier de données
            
        Returns:
            list: Liste des données des candidats
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == ".json":
                return self._load_from_json(file_path, "candidates")
            elif file_extension == ".csv":
                return self._load_from_csv(file_path)
            else:
                logger.error(f"Format de fichier non supporté: {file_extension}")
                return []
        except Exception as e:
            logger.error(f"Erreur lors du chargement des candidats depuis {file_path}: {e}")
            return []
    
    def load_companies(self, file_path):
        """
        Charge les données des entreprises à partir d'un fichier JSON ou CSV.
        
        Args:
            file_path (str): Chemin vers le fichier de données
            
        Returns:
            list: Liste des données des entreprises
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == ".json":
                return self._load_from_json(file_path, "companies")
            elif file_extension == ".csv":
                return self._load_from_csv(file_path)
            else:
                logger.error(f"Format de fichier non supporté: {file_extension}")
                return []
        except Exception as e:
            logger.error(f"Erreur lors du chargement des entreprises depuis {file_path}: {e}")
            return []
    
    def _load_from_json(self, file_path, key=None):
        """
        Charge des données à partir d'un fichier JSON.
        
        Args:
            file_path (str): Chemin vers le fichier JSON
            key (str, optional): Clé pour accéder aux données dans le JSON
            
        Returns:
            list: Liste des données chargées
        """
        logger.info(f"Chargement des données depuis le fichier JSON {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if key and key in data:
            return data[key]
        
        # Si la clé n'est pas trouvée mais que c'est une liste, retourner directement
        if isinstance(data, list):
            return data
        
        # Sinon, chercher la première liste dans les clés du dictionnaire
        for k, v in data.items():
            if isinstance(v, list):
                logger.info(f"Utilisation de la clé '{k}' pour accéder aux données")
                return v
        
        logger.error(f"Structure JSON non supportée dans {file_path}")
        return []
    
    def _load_from_csv(self, file_path):
        """
        Charge des données à partir d'un fichier CSV.
        
        Args:
            file_path (str): Chemin vers le fichier CSV
            
        Returns:
            list: Liste des données chargées (format dictionnaire)
        """
        logger.info(f"Chargement des données depuis le fichier CSV {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Traitement spécial pour les colonnes qui devraient être des listes
        list_columns = ["skills", "required_skills", "preferred_sectors"]
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])
        
        # Traitement spécial pour les colonnes qui devraient être des dictionnaires
        dict_columns = ["salary_range"]
        for col in dict_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) else {})
        
        # Convertir le DataFrame en liste de dictionnaires
        data = df.to_dict(orient='records')
        return data
    
    def save_results(self, results, file_path):
        """
        Sauvegarde les résultats de matching dans un fichier.
        
        Args:
            results (list): Résultats de matching
            file_path (str): Chemin du fichier de sortie
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if file_extension == ".json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            elif file_extension == ".csv":
                # Aplatir les détails pour le CSV
                flat_results = []
                for result in results:
                    flat_result = {k: v for k, v in result.items() if k != "details"}
                    
                    # Ajouter les détails comme colonnes séparées
                    if "details" in result:
                        for detail_key, detail_value in result["details"].items():
                            if detail_key == "missing_skills" and isinstance(detail_value, list):
                                flat_result[detail_key] = ",".join(detail_value)
                            else:
                                flat_result[detail_key] = detail_value
                    
                    flat_results.append(flat_result)
                
                df = pd.DataFrame(flat_results)
                df.to_csv(file_path, index=False)
            else:
                logger.error(f"Format de fichier non supporté pour la sauvegarde: {file_extension}")
                return
            
            logger.info(f"Résultats sauvegardés dans {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats dans {file_path}: {e}")