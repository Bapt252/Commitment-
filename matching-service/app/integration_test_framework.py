"""
Framework de Tests d'Intégration pour Nexten SmartMatch
----------------------------------------------------------------
Ce module fournit un framework complet pour les tests d'intégration
du système Nexten SmartMatch, permettant de tester les différents
composants ensemble.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import sys
import json
import logging
import time
import uuid
import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
import unittest
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTestFramework:
    """
    Framework pour l'exécution des tests d'intégration pour Nexten SmartMatch
    """
    
    def __init__(self, base_dir: str = None, output_dir: str = None):
        """
        Initialise le framework de tests d'intégration
        
        Args:
            base_dir: Répertoire de base du projet (détecté automatiquement si None)
            output_dir: Répertoire pour les résultats des tests
        """
        # Déterminer le répertoire de base si non spécifié
        if base_dir is None:
            # Utiliser le répertoire parent du répertoire courant
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir
        
        # Déterminer le répertoire de sortie
        if output_dir is None:
            self.output_dir = os.path.join(self.base_dir, "test_results")
        else:
            self.output_dir = output_dir
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialiser les listes pour stocker les tests et résultats
        self.test_cases = []
        self.test_results = []
        
        # Identifiant unique pour cette session de test
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.datetime.now()
        
        # Stocker les composants à tester
        self.components = {}
        
        logger.info(f"Framework de Tests d'Intégration initialisé - Session ID: {self.session_id}")
        logger.info(f"Répertoire de base: {self.base_dir}")
        logger.info(f"Répertoire de sortie: {self.output_dir}")
    
    def register_component(self, name: str, component_class: Any, *args, **kwargs) -> Any:
        """
        Enregistre un composant à tester
        
        Args:
            name: Nom du composant
            component_class: Classe du composant
            *args, **kwargs: Arguments pour l'initialisation du composant
            
        Returns:
            Instance du composant
        """
        try:
            # Instancier le composant
            component = component_class(*args, **kwargs)
            
            # Stocker l'instance
            self.components[name] = component
            
            logger.info(f"Composant '{name}' enregistré")
            return component
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du composant '{name}': {str(e)}")
            return None
    
    def get_component(self, name: str) -> Any:
        """
        Récupère un composant enregistré
        
        Args:
            name: Nom du composant
            
        Returns:
            Instance du composant ou None si non trouvé
        """
        return self.components.get(name)
    
    def add_test_case(self, name: str, description: str, test_func: Callable, 
                     expected_result: Any = None, dependencies: List[str] = None):
        """
        Ajoute un cas de test au framework
        
        Args:
            name: Nom du test
            description: Description du test
            test_func: Fonction de test (sera appelée avec self comme argument)
            expected_result: Résultat attendu (optionnel)
            dependencies: Liste des noms de tests dont ce test dépend
        """
        test_case = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "function": test_func,
            "expected_result": expected_result,
            "dependencies": dependencies or [],
            "status": "pending"
        }
        
        self.test_cases.append(test_case)
        logger.info(f"Test '{name}' ajouté")
    
    def run_all_tests(self):
        """
        Exécute tous les tests enregistrés
        
        Returns:
            Dict: Résultats des tests
        """
        logger.info("Démarrage de l'exécution de tous les tests")
        
        # Réinitialiser les résultats
        self.test_results = []
        
        # Classer les tests par dépendances
        ordered_tests = self._order_tests_by_dependencies()
        
        # Exécuter les tests dans l'ordre
        for test_case in ordered_tests:
            self._run_test(test_case)
        
        # Générer le rapport
        self._generate_report()
        
        return self.test_results
    
    def run_test(self, test_name: str):
        """
        Exécute un test spécifique par son nom
        
        Args:
            test_name: Nom du test à exécuter
            
        Returns:
            Dict: Résultat du test
        """
        # Trouver le test
        test_case = next((test for test in self.test_cases if test["name"] == test_name), None)
        
        if test_case is None:
            logger.error(f"Test '{test_name}' non trouvé")
            return None
        
        # Vérifier les dépendances
        for dependency in test_case["dependencies"]:
            dependency_test = next((test for test in self.test_cases if test["name"] == dependency), None)
            
            if dependency_test is None:
                logger.error(f"Dépendance '{dependency}' non trouvée pour le test '{test_name}'")
                return None
            
            # Vérifier si la dépendance a été exécutée et a réussi
            dependency_result = next((res for res in self.test_results if res["test_id"] == dependency_test["id"]), None)
            
            if dependency_result is None or dependency_result["status"] != "passed":
                logger.error(f"La dépendance '{dependency}' n'a pas été exécutée ou a échoué")
                return None
        
        # Exécuter le test
        return self._run_test(test_case)
    
    def _run_test(self, test_case: Dict[str, Any]):
        """
        Exécute un cas de test
        
        Args:
            test_case: Cas de test à exécuter
            
        Returns:
            Dict: Résultat du test
        """
        test_id = test_case["id"]
        test_name = test_case["name"]
        
        logger.info(f"Exécution du test '{test_name}'")
        
        # Préparer le résultat
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "start_time": datetime.datetime.now(),
            "duration": 0,
            "status": "running",
            "error": None,
            "details": {}
        }
        
        try:
            # Mesurer le temps d'exécution
            start_time = time.time()
            
            # Exécuter la fonction de test
            test_result = test_case["function"](self)
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Vérifier le résultat
            expected_result = test_case["expected_result"]
            
            if expected_result is not None and test_result != expected_result:
                result["status"] = "failed"
                result["error"] = f"Résultat attendu: {expected_result}, obtenu: {test_result}"
            else:
                result["status"] = "passed"
            
            # Ajouter les détails
            result["details"] = test_result if isinstance(test_result, dict) else {"result": test_result}
            
        except Exception as e:
            # En cas d'erreur
            duration = time.time() - start_time
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Erreur lors de l'exécution du test '{test_name}': {str(e)}")
        
        # Mettre à jour le résultat
        result["duration"] = duration
        result["end_time"] = datetime.datetime.now()
        
        # Stocker le résultat
        self.test_results.append(result)
        
        # Mettre à jour le statut du test
        test_case["status"] = result["status"]
        
        logger.info(f"Test '{test_name}' terminé avec le statut '{result['status']}' en {duration:.2f}s")
        
        return result
    
    def _order_tests_by_dependencies(self) -> List[Dict[str, Any]]:
        """
        Ordonne les tests en fonction de leurs dépendances
        
        Returns:
            List[Dict]: Tests ordonnés
        """
        # Copier la liste des tests
        remaining_tests = self.test_cases.copy()
        ordered_tests = []
        
        # Tant qu'il reste des tests à ordonner
        while remaining_tests:
            # Trouver les tests sans dépendances ou dont les dépendances sont déjà satisfaites
            tests_to_add = []
            
            for test in remaining_tests:
                # Vérifier si toutes les dépendances sont dans les tests ordonnés
                dependencies_satisfied = True
                
                for dependency in test["dependencies"]:
                    # Trouver le test de dépendance
                    dependency_test = next((t for t in self.test_cases if t["name"] == dependency), None)
                    
                    if dependency_test is None or dependency_test not in ordered_tests:
                        dependencies_satisfied = False
                        break
                
                if dependencies_satisfied:
                    tests_to_add.append(test)
            
            # Si aucun test ne peut être ajouté, il y a une dépendance circulaire
            if not tests_to_add:
                logger.error("Dépendance circulaire détectée dans les tests")
                
                # Ajouter un test au hasard pour éviter une boucle infinie
                tests_to_add.append(remaining_tests[0])
            
            # Ajouter les tests à la liste ordonnée et les retirer des tests restants
            for test in tests_to_add:
                ordered_tests.append(test)
                remaining_tests.remove(test)
        
        return ordered_tests
    
    def _generate_report(self):
        """
        Génère un rapport des tests exécutés
        """
        if not self.test_results:
            logger.warning("Aucun résultat de test à rapporter")
            return
        
        # Calculer les statistiques
        total_tests = len(self.test_results)
        passed_tests = sum(1 for res in self.test_results if res["status"] == "passed")
        failed_tests = sum(1 for res in self.test_results if res["status"] == "failed")
        error_tests = sum(1 for res in self.test_results if res["status"] == "error")
        
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Créer le rapport
        report = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "end_time": datetime.datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "pass_rate": pass_rate,
            "results": self.test_results
        }
        
        # Enregistrer le rapport au format JSON
        report_file = os.path.join(self.output_dir, f"integration_test_report_{self.session_id}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Rapport des tests enregistré dans {report_file}")
        
        # Générer un rapport visuel
        self._generate_visual_report(report)
        
        # Afficher un résumé
        logger.info(f"Résumé des tests: {passed_tests}/{total_tests} réussis ({pass_rate:.1f}%)")
        
        if failed_tests > 0 or error_tests > 0:
            logger.warning(f"Attention: {failed_tests} tests ont échoué et {error_tests} ont généré des erreurs")
    
    def _generate_visual_report(self, report: Dict[str, Any]):
        """
        Génère un rapport visuel des tests
        
        Args:
            report: Données du rapport
        """
        try:
            # Créer un DataFrame à partir des résultats
            results_data = []
            
            for result in report["results"]:
                results_data.append({
                    "Test": result["test_name"],
                    "Status": result["status"],
                    "Duration": result["duration"]
                })
            
            df = pd.DataFrame(results_data)
            
            # Configurer le style
            sns.set_theme(style="whitegrid")
            
            # Figure 1: Statut des tests (camembert)
            plt.figure(figsize=(10, 6))
            status_counts = df["Status"].value_counts()
            colors = {
                "passed": "green",
                "failed": "red",
                "error": "orange",
                "running": "blue",
                "pending": "gray"
            }
            status_colors = [colors.get(status, "gray") for status in status_counts.index]
            
            plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
                   colors=status_colors, startangle=90)
            plt.title('Statut des Tests')
            plt.axis('equal')
            
            # Enregistrer le graphique
            status_file = os.path.join(self.output_dir, f"test_status_{self.session_id}.png")
            plt.savefig(status_file)
            plt.close()
            
            # Figure 2: Durée des tests (barres)
            plt.figure(figsize=(12, 8))
            
            # Trier par durée
            df_sorted = df.sort_values("Duration", ascending=False)
            
            # Colorer les barres selon le statut
            bar_colors = [colors.get(status, "gray") for status in df_sorted["Status"]]
            
            sns.barplot(x="Duration", y="Test", data=df_sorted, palette=bar_colors)
            plt.title('Durée des Tests (secondes)')
            plt.tight_layout()
            
            # Enregistrer le graphique
            duration_file = os.path.join(self.output_dir, f"test_duration_{self.session_id}.png")
            plt.savefig(duration_file)
            plt.close()
            
            logger.info(f"Rapport visuel généré: {status_file}, {duration_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport visuel: {str(e)}")

# Exemple d'utilisation pour les tests
if __name__ == "__main__":
    # Initialiser le framework
    framework = IntegrationTestFramework()
    
    # Exemple de fonction de test
    def test_exemple(fw):
        # Simuler un test
        time.sleep(1)
        return True
    
    # Ajouter un test
    framework.add_test_case(
        name="test_exemple",
        description="Un exemple de test",
        test_func=test_exemple,
        expected_result=True
    )
    
    # Exécuter les tests
    framework.run_all_tests()
