"""
Système de feedback pour améliorer continuellement le parsing de documents.
Ce module permet aux recruteurs de corriger les erreurs de parsing et
crée un dataset d'apprentissage pour l'amélioration continue.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
import uuid
from pathlib import Path
import shutil

# Configuration du logging
logger = logging.getLogger(__name__)

class ParserFeedbackSystem:
    """
    Classe pour collecter, stocker et utiliser les feedbacks des utilisateurs
    pour améliorer le système de parsing.
    """
    
    def __init__(self, storage_dir=None):
        """
        Initialise le système de feedback.
        
        Args:
            storage_dir: Répertoire de stockage des feedbacks (optionnel)
        """
        # Déterminer le répertoire de stockage
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Par défaut, utiliser un répertoire dans les données de l'application
            self.storage_dir = Path(__file__).resolve().parent.parent.parent / "data" / "feedback"
        
        # S'assurer que le répertoire existe
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-répertoires pour les différents types de feedback
        self.feedback_dirs = {
            "corrections": self.storage_dir / "corrections",
            "improvements": self.storage_dir / "improvements",
            "training_data": self.storage_dir / "training_data"
        }
        
        # Créer les sous-répertoires
        for dir_path in self.feedback_dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        logger.info(f"Système de feedback initialisé avec stockage dans {self.storage_dir}")
    
    def save_parsing_correction(self, 
                               original_data: Dict[str, Any], 
                               corrected_data: Dict[str, Any], 
                               doc_type: str,
                               user_id: Optional[str] = None,
                               original_text: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Enregistre une correction de parsing effectuée par un utilisateur.
        
        Args:
            original_data: Données extraites automatiquement
            corrected_data: Données corrigées par l'utilisateur
            doc_type: Type de document ('cv', 'job_posting', etc.)
            user_id: Identifiant de l'utilisateur (optionnel)
            original_text: Texte original du document (optionnel)
            metadata: Métadonnées supplémentaires (optionnel)
            
        Returns:
            str: Identifiant unique de la correction
        """
        # Générer un ID unique pour cette correction
        correction_id = str(uuid.uuid4())
        
        # Préparer les données à sauvegarder
        correction_data = {
            "id": correction_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "doc_type": doc_type,
            "original_extraction": original_data,
            "corrected_extraction": corrected_data,
            "metadata": metadata or {}
        }
        
        # Si le texte original est fourni, le sauvegarder séparément
        if original_text:
            text_file = self.feedback_dirs["corrections"] / f"{correction_id}_text.txt"
            try:
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(original_text)
                correction_data["original_text_file"] = str(text_file.name)
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du texte original: {e}")
        
        # Sauvegarder les données de correction
        json_file = self.feedback_dirs["corrections"] / f"{correction_id}.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(correction_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Correction sauvegardée avec ID: {correction_id}")
            
            # Ajouter automatiquement aux données d'entraînement
            self._add_to_training_data(correction_data, original_text)
            
            return correction_id
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la correction: {e}")
            return ""
    
    def save_improvement_suggestion(self, 
                                   suggestion: str, 
                                   doc_type: str, 
                                   extraction_sample: Optional[Dict[str, Any]] = None,
                                   user_id: Optional[str] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Enregistre une suggestion d'amélioration pour le système de parsing.
        
        Args:
            suggestion: Texte de la suggestion
            doc_type: Type de document concerné
            extraction_sample: Exemple d'extraction problématique (optionnel)
            user_id: Identifiant de l'utilisateur (optionnel)
            metadata: Métadonnées supplémentaires (optionnel)
            
        Returns:
            str: Identifiant unique de la suggestion
        """
        # Générer un ID unique pour cette suggestion
        suggestion_id = str(uuid.uuid4())
        
        # Préparer les données à sauvegarder
        suggestion_data = {
            "id": suggestion_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "doc_type": doc_type,
            "suggestion": suggestion,
            "extraction_sample": extraction_sample,
            "metadata": metadata or {},
            "status": "new"  # new, reviewed, implemented, rejected
        }
        
        # Sauvegarder la suggestion
        json_file = self.feedback_dirs["improvements"] / f"{suggestion_id}.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(suggestion_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Suggestion d'amélioration sauvegardée avec ID: {suggestion_id}")
            return suggestion_id
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la suggestion: {e}")
            return ""
    
    def _add_to_training_data(self, correction_data: Dict[str, Any], original_text: Optional[str] = None):
        """
        Ajoute une correction aux données d'entraînement.
        
        Args:
            correction_data: Données de correction
            original_text: Texte original du document (optionnel)
        """
        try:
            doc_type = correction_data.get("doc_type", "unknown")
            
            # Créer un sous-répertoire pour ce type de document s'il n'existe pas
            doc_type_dir = self.feedback_dirs["training_data"] / doc_type
            doc_type_dir.mkdir(exist_ok=True)
            
            # Préparer les données d'entraînement
            training_item = {
                "id": correction_data["id"],
                "source": "user_correction",
                "timestamp": correction_data["timestamp"],
                "corrected_extraction": correction_data["corrected_extraction"]
            }
            
            # Si le texte original est disponible, l'inclure
            original_text_file = correction_data.get("original_text_file")
            if original_text_file and not original_text:
                try:
                    text_path = self.feedback_dirs["corrections"] / original_text_file
                    with open(text_path, 'r', encoding='utf-8') as f:
                        original_text = f.read()
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du texte original: {e}")
            
            if original_text:
                # Sauvegarder le texte
                text_file = doc_type_dir / f"{correction_data['id']}_text.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(original_text)
                training_item["text_file"] = str(text_file.name)
            
            # Sauvegarder les données d'entraînement
            json_file = doc_type_dir / f"{correction_data['id']}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(training_item, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Ajouté aux données d'entraînement: {correction_data['id']}")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout aux données d'entraînement: {e}")
    
    def get_correction(self, correction_id: str) -> Dict[str, Any]:
        """
        Récupère une correction spécifique.
        
        Args:
            correction_id: Identifiant de la correction
            
        Returns:
            Dict: Données de correction ou dictionnaire vide si non trouvée
        """
        json_file = self.feedback_dirs["corrections"] / f"{correction_id}.json"
        
        if not json_file.exists():
            logger.warning(f"Correction non trouvée: {correction_id}")
            return {}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                correction_data = json.load(f)
            
            # Si un fichier texte est référencé, le charger aussi
            text_file_name = correction_data.get("original_text_file")
            if text_file_name:
                text_file = self.feedback_dirs["corrections"] / text_file_name
                if text_file.exists():
                    with open(text_file, 'r', encoding='utf-8') as f:
                        correction_data["original_text"] = f.read()
            
            return correction_data
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la correction: {e}")
            return {}
    
    def get_training_data(self, doc_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les données d'entraînement.
        
        Args:
            doc_type: Type de document à filtrer (optionnel)
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            List: Liste des données d'entraînement
        """
        training_data = []
        
        try:
            # Si un type de document est spécifié, chercher uniquement dans ce répertoire
            if doc_type:
                doc_type_dir = self.feedback_dirs["training_data"] / doc_type
                if not doc_type_dir.exists():
                    logger.warning(f"Aucune donnée d'entraînement pour le type: {doc_type}")
                    return []
                
                json_files = list(doc_type_dir.glob("*.json"))
                
                # Limiter le nombre de fichiers
                json_files = sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
                
                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Charger le texte associé si disponible
                        text_file_name = data.get("text_file")
                        if text_file_name:
                            text_file = doc_type_dir / text_file_name
                            if text_file.exists():
                                with open(text_file, 'r', encoding='utf-8') as f:
                                    data["text"] = f.read()
                        
                        training_data.append(data)
                    except Exception as e:
                        logger.error(f"Erreur lors de la lecture du fichier d'entraînement {json_file}: {e}")
            else:
                # Parcourir tous les sous-répertoires
                for item in self.feedback_dirs["training_data"].iterdir():
                    if item.is_dir():
                        # Récupérer une partie des données de chaque type
                        sub_limit = limit // 5  # Diviser la limite pour avoir une répartition équilibrée
                        sub_limit = max(sub_limit, 10)  # Au moins 10 par type
                        
                        json_files = list(item.glob("*.json"))
                        json_files = sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:sub_limit]
                        
                        for json_file in json_files:
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                # Ajouter le type de document
                                data["doc_type"] = item.name
                                
                                # Charger le texte associé si disponible
                                text_file_name = data.get("text_file")
                                if text_file_name:
                                    text_file = item / text_file_name
                                    if text_file.exists():
                                        with open(text_file, 'r', encoding='utf-8') as f:
                                            data["text"] = f.read()
                                
                                training_data.append(data)
                                
                                # Arrêter si on atteint la limite globale
                                if len(training_data) >= limit:
                                    break
                            except Exception as e:
                                logger.error(f"Erreur lors de la lecture du fichier d'entraînement {json_file}: {e}")
                        
                        # Arrêter si on atteint la limite globale
                        if len(training_data) >= limit:
                            break
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données d'entraînement: {e}")
        
        return training_data
    
    def export_training_dataset(self, output_dir: str, doc_type: Optional[str] = None) -> bool:
        """
        Exporte les données d'entraînement dans un format adapté pour le fine-tuning.
        
        Args:
            output_dir: Répertoire de sortie
            doc_type: Type de document à exporter (optionnel)
            
        Returns:
            bool: True si l'exportation a réussi
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Récupérer les données d'entraînement
            training_data = self.get_training_data(doc_type=doc_type, limit=1000)
            
            if not training_data:
                logger.warning("Aucune donnée d'entraînement à exporter.")
                return False
            
            # Préparer les données pour l'exportation
            export_data = []
            
            for item in training_data:
                if "text" in item and "corrected_extraction" in item:
                    export_item = {
                        "id": item.get("id", str(uuid.uuid4())),
                        "text": item["text"],
                        "extraction": item["corrected_extraction"],
                        "doc_type": item.get("doc_type", doc_type or "unknown")
                    }
                    export_data.append(export_item)
            
            # Écrire le fichier d'exportation
            if doc_type:
                export_file = output_path / f"training_data_{doc_type}.json"
            else:
                export_file = output_path / "training_data_all.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Créer également des fichiers séparés pour chaque type de document si on exporte tout
            if not doc_type:
                doc_types = set(item.get("doc_type", "unknown") for item in training_data)
                for dt in doc_types:
                    if dt == "unknown":
                        continue
                        
                    dt_data = [item for item in export_data if item.get("doc_type") == dt]
                    if dt_data:
                        dt_export_file = output_path / f"training_data_{dt}.json"
                        with open(dt_export_file, 'w', encoding='utf-8') as f:
                            json.dump(dt_data, f, ensure_ascii=False, indent=2)
                        logger.info(f"Données d'entraînement pour {dt} exportées dans {dt_export_file} ({len(dt_data)} éléments)")
            
            # Créer également un format compatible avec le fine-tuning BERT
            bert_format = []
            for item in export_data:
                if "text" in item and "extraction" in item:
                    # Pour chaque paire clé-valeur dans l'extraction, créer un exemple d'entraînement
                    for key, value in item["extraction"].items():
                        if isinstance(value, str):
                            bert_item = {
                                "text": item["text"],
                                "field": key,
                                "value": value
                            }
                            bert_format.append(bert_item)
            
            if bert_format:
                bert_file = output_path / "bert_training_data.json"
                with open(bert_file, 'w', encoding='utf-8') as f:
                    json.dump(bert_format, f, ensure_ascii=False, indent=2)
                logger.info(f"Format d'entraînement BERT exporté dans {bert_file} ({len(bert_format)} exemples)")
            
            logger.info(f"Données d'entraînement exportées dans {export_file} ({len(export_data)} éléments)")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des données d'entraînement: {e}")
            return False
    
    def update_extraction_with_feedback(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour un résultat d'extraction avec des corrections similaires précédentes.
        
        Args:
            extraction_result: Résultat d'extraction original
            
        Returns:
            Dict: Résultat mis à jour avec des améliorations basées sur le feedback
        """
        try:
            # Vérifier qu'il y a suffisamment d'informations pour appliquer des corrections
            if "doc_type" not in extraction_result or "extracted_data" not in extraction_result:
                logger.warning("Données d'extraction insuffisantes pour appliquer des corrections")
                return extraction_result
            
            doc_type = extraction_result["doc_type"]
            
            # Récupérer les données d'entraînement pertinentes
            training_data = self.get_training_data(doc_type=doc_type, limit=20)
            
            if not training_data:
                logger.info(f"Aucune donnée d'entraînement disponible pour le type {doc_type}")
                return extraction_result
            
            # Copie du résultat original pour ne pas le modifier directement
            updated_result = extraction_result.copy()
            
            # 1. Vérifier les champs manquants
            if "extracted_data" in updated_result:
                original_fields = set(updated_result["extracted_data"].keys())
                
                # Collecter les champs présents dans les données d'entraînement
                training_fields = set()
                for item in training_data:
                    if "corrected_extraction" in item:
                        training_fields.update(item["corrected_extraction"].keys())
                
                # Identifier les champs manquants dans le résultat original
                missing_fields = training_fields - original_fields
                
                # Si des champs sont manquants, marquer pour amélioration
                if missing_fields:
                    if "improvement_suggestions" not in updated_result:
                        updated_result["improvement_suggestions"] = {}
                    
                    updated_result["improvement_suggestions"]["missing_fields"] = list(missing_fields)
                    logger.info(f"Champs potentiellement manquants identifiés: {missing_fields}")
            
            # 2. Corriger les formats et valeurs erronés basés sur des patterns connus
            corrections_applied = []
            
            if "extracted_data" in updated_result:
                extracted_data = updated_result["extracted_data"]
                
                # Pour chaque champ dans les données extraites
                for field, value in extracted_data.items():
                    # Chercher des modèles de correction dans les données d'entraînement
                    potential_corrections = {}
                    
                    for training_item in training_data:
                        if "corrected_extraction" in training_item and field in training_item["corrected_extraction"]:
                            # Si le champ existe à la fois dans l'extraction originale et corrigée
                            if "original_extraction" in training_item and field in training_item["original_extraction"]:
                                orig_val = training_item["original_extraction"][field]
                                corrected_val = training_item["corrected_extraction"][field]
                                
                                # Si une correction a été appliquée et que la valeur originale est similaire à notre valeur actuelle
                                if orig_val != corrected_val and str(orig_val) == str(value):
                                    # Enregistrer cette correction comme potentielle
                                    if str(orig_val) not in potential_corrections:
                                        potential_corrections[str(orig_val)] = []
                                    potential_corrections[str(orig_val)].append(corrected_val)
                    
                    # Appliquer la correction la plus fréquente si disponible
                    if str(value) in potential_corrections and potential_corrections[str(value)]:
                        # Compter les occurrences de chaque correction
                        correction_counts = {}
                        for correction in potential_corrections[str(value)]:
                            correction_str = str(correction)
                            correction_counts[correction_str] = correction_counts.get(correction_str, 0) + 1
                        
                        # Trouver la correction la plus fréquente
                        most_common_correction = max(correction_counts.items(), key=lambda x: x[1])[0]
                        
                        # Appliquer la correction si elle est significativement différente
                        if most_common_correction != str(value):
                            # Convertir au bon type si nécessaire
                            if isinstance(value, int):
                                try:
                                    updated_result["extracted_data"][field] = int(most_common_correction)
                                except ValueError:
                                    updated_result["extracted_data"][field] = most_common_correction
                            elif isinstance(value, float):
                                try:
                                    updated_result["extracted_data"][field] = float(most_common_correction)
                                except ValueError:
                                    updated_result["extracted_data"][field] = most_common_correction
                            else:
                                updated_result["extracted_data"][field] = most_common_correction
                            
                            corrections_applied.append({
                                "field": field,
                                "original": value,
                                "corrected": updated_result["extracted_data"][field]
                            })
            
            # 3. Ajouter des métadonnées sur les corrections appliquées
            if corrections_applied:
                if "feedback_applied" not in updated_result:
                    updated_result["feedback_applied"] = {}
                
                updated_result["feedback_applied"]["corrections"] = corrections_applied
                updated_result["feedback_applied"]["timestamp"] = datetime.datetime.now().isoformat()
                updated_result["feedback_applied"]["source"] = "automatic"
                
                logger.info(f"{len(corrections_applied)} corrections appliquées basées sur le feedback utilisateur.")
            
            # 4. Calculer un score de confiance pour les corrections
            if corrections_applied or ("improvement_suggestions" in updated_result and "missing_fields" in updated_result["improvement_suggestions"]):
                confidence_adjustment = min(0.2, 0.05 * len(corrections_applied))
                
                if "confidence_scores" not in updated_result:
                    updated_result["confidence_scores"] = {}
                
                # Ajuster le score global d'extraction
                if "extraction" in updated_result["confidence_scores"]:
                    # Diminuer le score car des corrections ont été nécessaires
                    updated_result["confidence_scores"]["extraction"] = max(
                        0.3, updated_result["confidence_scores"]["extraction"] - confidence_adjustment
                    )
                
                # Ajouter un score pour les corrections appliquées
                updated_result["confidence_scores"]["feedback_correction"] = min(0.9, 0.5 + 0.1 * len(corrections_applied))
            
            return updated_result
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour avec feedback: {e}")
            return extraction_result


# Fonctions d'interface pour utilisation dans d'autres modules
def get_feedback_system() -> ParserFeedbackSystem:
    """
    Obtient une instance du système de feedback.
    
    Returns:
        ParserFeedbackSystem: Instance du système
    """
    return ParserFeedbackSystem()

def save_parsing_correction(original_data: Dict[str, Any], 
                          corrected_data: Dict[str, Any], 
                          doc_type: str, 
                          user_id: Optional[str] = None,
                          original_text: Optional[str] = None) -> str:
    """
    Fonction d'interface pour sauvegarder une correction de parsing.
    
    Args:
        original_data: Données extraites automatiquement
        corrected_data: Données corrigées par l'utilisateur
        doc_type: Type de document
        user_id: Identifiant de l'utilisateur (optionnel)
        original_text: Texte original du document (optionnel)
        
    Returns:
        str: Identifiant de la correction
    """
    feedback_system = ParserFeedbackSystem()
    return feedback_system.save_parsing_correction(
        original_data=original_data,
        corrected_data=corrected_data,
        doc_type=doc_type,
        user_id=user_id,
        original_text=original_text
    )

def improve_extraction_with_feedback(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Améliore un résultat d'extraction avec le feedback précédent.
    
    Args:
        extraction_result: Résultat d'extraction original
        
    Returns:
        Dict: Résultat amélioré
    """
    feedback_system = ParserFeedbackSystem()
    return feedback_system.update_extraction_with_feedback(extraction_result)