import os
import sys
import requests
import json

def test_job_parser(pdf_path):
    """Teste le service de parsing de fiches de poste avec un fichier PDF local"""
    
    # Vérifier que le fichier existe
    if not os.path.exists(pdf_path):
        print(f"Erreur: Le fichier {pdf_path} n'existe pas!")
        return False
    
    # URL du service
    url = "http://localhost:5053/api/parse-job"
    
    # Vérifier que le service est en ligne
    try:
        health_response = requests.get("http://localhost:5053/health")
        if health_response.status_code != 200:
            print(f"Erreur: Le service n'est pas disponible (HTTP {health_response.status_code})")
            print("Vérifiez que les conteneurs Docker sont en cours d'exécution:")
            print("  docker-compose ps")
            print("  docker-compose logs job-parser")
            return False
        else:
            print("Service de parsing de fiches de poste en ligne.")
    except requests.exceptions.ConnectionError:
        print("Erreur: Impossible de se connecter au service. Vérifiez que:")
        print("1. Les conteneurs Docker sont en cours d'exécution:")
        print("   docker-compose ps")
        print("2. Le service job-parser est bien démarré:")
        print("   docker-compose logs job-parser")
        print("3. Le port 5053 est bien accessible:")
        print("   docker-compose port job-parser 5000")
        return False
    
    print(f"Envoi du fichier {pdf_path} au service de parsing...")
    
    # Préparer les fichiers et données pour la requête
    files = {
        'file': open(pdf_path, 'rb')
    }
    data = {
        'force_refresh': 'true'
    }
    
    try:
        # Envoyer la requête
        response = requests.post(url, files=files, data=data)
        
        # Afficher la réponse formatée
        try:
            parsed_response = json.loads(response.text)
            print("\nRésultat du parsing:")
            print(json.dumps(parsed_response, indent=2, ensure_ascii=False))
            print("\nStructure des données extraites:")
            if 'data' in parsed_response:
                print(json.dumps(parsed_response['data'], indent=2, ensure_ascii=False))
            return True
        except json.JSONDecodeError:
            print("Erreur: Impossible de décoder la réponse JSON")
            print("Réponse brute:")
            print(response.text)
            return False
    except Exception as e:
        print(f"Erreur lors de l'envoi de la requête: {e}")
        return False
    finally:
        # Fermer le fichier
        files['file'].close()

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python test_local_pdf.py /chemin/vers/votre/fiche_poste.pdf")
        return
    
    pdf_path = sys.argv[1]
    test_job_parser(pdf_path)

if __name__ == "__main__":
    main()
