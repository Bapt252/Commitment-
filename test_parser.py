#!/usr/bin/env python3

"""
Script de test pour le service de parsing CV

Ce script teste différents endpoints du service CV Parser pour diagnostiquer
les problèmes de parsing via GPT.
"""

import os
import sys
import json
import time
import requests
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000"
CV_PATH = "/Users/baptistecomas/Desktop/MonSuperCV.pdf"  # Chemin par défaut
VERBOSE = True

# Couleurs pour l'affichage
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color


def print_colored(color, message):
    """Affiche un message avec une couleur spécifique"""
    print(f"{color}{message}{NC}")


def check_arguments():
    """Vérifie et traite les arguments de ligne de commande"""
    global CV_PATH, BASE_URL, VERBOSE

    # Traiter les arguments
    if len(sys.argv) > 1:
        CV_PATH = sys.argv[1]

    # Vérifier si le fichier CV existe
    if not os.path.isfile(CV_PATH):
        print_colored(RED, f"❌ Erreur: Le fichier CV n'existe pas: {CV_PATH}")
        print_colored(YELLOW, "👉 Spécifiez un chemin valide comme argument: ./test_parser.py /chemin/vers/cv.pdf")
        sys.exit(1)

    # Afficher la configuration
    print_colored(BLUE, "🔍 Configuration:")
    print(f"- URL de base: {BASE_URL}")
    print(f"- Fichier CV: {CV_PATH}")
    print(f"- Mode verbose: {VERBOSE}")
    print("\n" + "-"*50 + "\n")


def test_health_endpoint():
    """Teste l'endpoint de santé du service"""
    print_colored(BLUE, "🏥 Test de l'endpoint health...")
    
    try:
        response = requests.get(urljoin(BASE_URL, "/health"))
        
        if response.status_code == 200:
            print_colored(GREEN, f"✅ Service en ligne! Réponse: {response.json()}")
            return True
        else:
            print_colored(RED, f"❌ Service accessible mais retourne une erreur: {response.status_code}")
            print(f"Contenu: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_colored(RED, f"❌ Impossible de se connecter au service à {BASE_URL}")
        print_colored(YELLOW, "👉 Vérifiez que le service est démarré et que le port est correct")
        return False
    except Exception as e:
        print_colored(RED, f"❌ Erreur lors du test de santé: {str(e)}")
        return False


def test_direct_parsing_endpoint():
    """Teste l'endpoint de parsing direct"""
    print_colored(BLUE, "\n📄 Test de l'endpoint de parsing direct...")
    
    try:
        with open(CV_PATH, "rb") as cv_file:
            files = {"file": (os.path.basename(CV_PATH), cv_file, "application/pdf")}
            data = {"force_refresh": "true"}  # Force le rafraîchissement pour éviter le cache
            
            print_colored(YELLOW, "Envoi de la requête...")
            start_time = time.time()
            
            # Test sans slash final
            url = urljoin(BASE_URL, "/api/parse-cv")
            print(f"URL: {url}")
            
            response = requests.post(
                url,
                files=files,
                data=data,
                allow_redirects=True  # Suivre les redirections
            )
            
            duration = time.time() - start_time
            
            print(f"Statut: {response.status_code} (en {duration:.2f}s)")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print_colored(GREEN, "\n✅ Parsing réussi!")
                try:
                    result = response.json()
                    print_colored(BLUE, "\nRésultat du parsing:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    return True
                except json.JSONDecodeError:
                    print_colored(YELLOW, "⚠️ La réponse n'est pas au format JSON")
                    print("Contenu brut:")
                    print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            else:
                print_colored(RED, f"❌ Erreur lors du parsing: {response.status_code}")
                print("Contenu de la réponse:")
                print(response.text)
                return False
    
    except Exception as e:
        print_colored(RED, f"❌ Erreur lors du test de parsing direct: {str(e)}")
        return False


def test_queue_endpoint():
    """Teste l'endpoint de file d'attente pour le parsing asynchrone"""
    print_colored(BLUE, "\n🔄 Test de l'endpoint de file d'attente...")
    
    try:
        with open(CV_PATH, "rb") as cv_file:
            files = {"file": (os.path.basename(CV_PATH), cv_file, "application/pdf")}
            data = {"priority": "premium"}  # Priorité maximale pour un traitement rapide
            
            print_colored(YELLOW, "Envoi du CV à la file d'attente...")
            
            # Endpoint de file d'attente
            url = urljoin(BASE_URL, "/api/queue")
            print(f"URL: {url}")
            
            response = requests.post(
                url,
                files=files,
                data=data
            )
            
            if response.status_code in [200, 202]:
                print_colored(GREEN, "\n✅ CV ajouté à la file d'attente!")
                try:
                    result = response.json()
                    print(f"Détails: {json.dumps(result, indent=2)}")
                    
                    # Si on a un job_id, on attend et récupère le résultat
                    if "job_id" in result:
                        job_id = result["job_id"]
                        print_colored(YELLOW, f"\nAttente du traitement du job {job_id}...")
                        
                        # Boucle pour récupérer le résultat (avec timeout)
                        max_attempts = 10
                        for attempt in range(max_attempts):
                            print(f"Tentative {attempt+1}/{max_attempts}...")
                            time.sleep(3)  # Attendre 3 secondes entre chaque tentative
                            
                            result_url = urljoin(BASE_URL, f"/api/result/{job_id}")
                            result_response = requests.get(result_url)
                            
                            if result_response.status_code == 200:
                                result_data = result_response.json()
                                status = result_data.get("status")
                                
                                if status == "done":
                                    print_colored(GREEN, "\n✅ Traitement terminé avec succès!")
                                    print_colored(BLUE, "\nRésultat du parsing:")
                                    print(json.dumps(result_data.get("result", {}), indent=2, ensure_ascii=False))
                                    return True
                                elif status == "failed":
                                    print_colored(RED, f"\n❌ Le traitement a échoué: {result_data.get('error', 'Erreur inconnue')}")
                                    return False
                                else:
                                    print(f"Statut actuel: {status}")
                        
                        print_colored(YELLOW, "⚠️ Timeout: le traitement prend trop de temps")
                    return True
                except json.JSONDecodeError:
                    print_colored(YELLOW, "⚠️ La réponse n'est pas au format JSON")
                    print(response.text)
            else:
                print_colored(RED, f"❌ Erreur lors de l'ajout à la file d'attente: {response.status_code}")
                print(response.text)
                return False
    
    except Exception as e:
        print_colored(RED, f"❌ Erreur lors du test de file d'attente: {str(e)}")
        return False


def main():
    """Fonction principale"""
    print_colored(BLUE, "=== Test du service de parsing CV via GPT ===")
    
    # Vérifier les arguments
    check_arguments()
    
    # Test 1: Vérifier que le service est en ligne
    if not test_health_endpoint():
        print_colored(RED, "\n❌ Le service ne répond pas correctement. Arrêt des tests.")
        return
    
    # Test 2: Parser un CV directement
    direct_result = test_direct_parsing_endpoint()
    
    # Test 3: Utiliser la file d'attente si le parsing direct ne fonctionne pas
    if not direct_result:
        print_colored(YELLOW, "\n⚠️ Le parsing direct n'a pas fonctionné, test de la file d'attente...")
        queue_result = test_queue_endpoint()
        
        if not queue_result:
            print_colored(RED, "\n❌ Tous les tests ont échoué.")
            print_colored(YELLOW, "Suggestions de dépannage:")
            print("1. Vérifiez que la clé API OpenAI est correctement configurée")
            print("2. Vérifiez les logs du service avec 'docker-compose logs cv-parser'")
            print("3. Redémarrez le service avec './restart-cv-parser.sh'")
            print("4. Essayez d'utiliser le mode mock si vous n'avez pas de clé OpenAI valide")
    
    print_colored(BLUE, "\n=== Fin des tests ===\n")


if __name__ == "__main__":
    main()
