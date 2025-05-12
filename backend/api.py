import os
import json
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Configuration
API_KEY = os.environ.get('OPENAI_API_KEY')  # Assurez-vous de définir cette variable d'environnement
MODEL = "gpt-3.5-turbo"  # Modèle GPT à utiliser

# Initialisation de l'API OpenAI
if API_KEY:
    openai.api_key = API_KEY
else:
    print("ATTENTION: Clé API OpenAI non définie. Le service ne fonctionnera pas correctement.")

# Création de l'application Flask
app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Stockage temporaire des jobs (simulé, à remplacer par une base de données en production)
jobs = {}

@app.route('/api/job-parser/queue', methods=['POST'])
def queue_job():
    """
    Point d'entrée pour soumettre un job d'analyse de fiche de poste
    """
    try:
        # Vérifier si un fichier a été envoyé
        if 'file' in request.files:
            file = request.files['file']
            content = file.read().decode('utf-8', errors='ignore')
        # Sinon, vérifier si le texte a été envoyé
        elif request.form.get('text'):
            content = request.form.get('text')
        else:
            return jsonify({"error": "Aucun fichier ou texte fourni"}), 400
        
        # Générer un ID unique pour le job
        job_id = str(uuid.uuid4())
        
        # Stocker le job avec le statut "pending"
        jobs[job_id] = {
            "status": "pending",
            "content": content,
            "created_at": time.time()
        }
        
        # Lancer l'analyse en arrière-plan (dans une vraie application, utilisez une file de tâches)
        # Ici, nous simulons un traitement asynchrone avec un thread
        import threading
        thread = threading.Thread(target=process_job, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({"job_id": job_id, "status": "pending"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-parser/result/<job_id>', methods=['GET'])
def get_job_result(job_id):
    """
    Point d'entrée pour récupérer le résultat d'un job
    """
    if job_id not in jobs:
        return jsonify({"error": "Job non trouvé"}), 404
    
    job = jobs[job_id]
    
    # Si le job est terminé, renvoyer le résultat
    if job["status"] == "done":
        return jsonify({
            "status": "done",
            "result": job["result"]
        })
    # Si le job est en erreur, renvoyer l'erreur
    elif job["status"] == "failed":
        return jsonify({
            "status": "failed",
            "error": job["error"]
        })
    # Sinon, le job est toujours en cours
    else:
        return jsonify({
            "status": job["status"],
            "message": "Job en cours de traitement"
        })

def process_job(job_id):
    """
    Fonction pour traiter un job d'analyse
    """
    job = jobs[job_id]
    
    try:
        # Mettre à jour le statut du job
        job["status"] = "processing"
        
        # Extraire les informations avec GPT
        result = extract_job_info_with_gpt(job["content"])
        
        # Mettre à jour le job avec le résultat
        job["status"] = "done"
        job["result"] = result
        job["completed_at"] = time.time()
        
        # Nettoyer le contenu original pour économiser de l'espace
        job.pop("content", None)
    
    except Exception as e:
        # En cas d'erreur, mettre à jour le statut et stocker l'erreur
        job["status"] = "failed"
        job["error"] = str(e)
        job["completed_at"] = time.time()
        
        # Nettoyer le contenu original pour économiser de l'espace
        job.pop("content", None)

def extract_job_info_with_gpt(content):
    """
    Utilise GPT pour extraire les informations de la fiche de poste
    """
    if not API_KEY:
        raise Exception("Clé API OpenAI non configurée")
    
    # Préparer le prompt pour GPT
    prompt = f"""
    Analyse la fiche de poste suivante et extrait les informations clés sous format JSON.
    Retourne uniquement le JSON sans aucune autre explication.
    
    Fiche de poste:
    {content}
    
    Format du JSON attendu:
    {{
        "title": "Titre du poste",
        "company": "Nom de l'entreprise",
        "location": "Lieu",
        "skills": ["Compétence 1", "Compétence 2", ...],
        "experience": "Niveau d'expérience requis",
        "responsibilities": ["Responsabilité 1", "Responsabilité 2", ...],
        "requirements": ["Prérequis 1", "Prérequis 2", ...],
        "salary": "Fourchette de salaire",
        "benefits": ["Avantage 1", "Avantage 2", ...]
    }}
    """
    
    try:
        # Appeler l'API OpenAI
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant spécialisé dans l'analyse de fiches de poste. Tu extrais avec précision les informations pertinentes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Valeur basse pour maximiser la précision
            max_tokens=2000
        )
        
        # Extraire la réponse
        result_text = response.choices[0].message.content.strip()
        
        # Essayer de parser le JSON
        try:
            result_json = json.loads(result_text)
            return result_json
        except json.JSONDecodeError:
            # Si GPT n'a pas renvoyé un JSON valide, essayer d'extraire le bloc JSON
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            match = re.search(json_pattern, result_text, re.DOTALL)
            
            if match:
                result_json = json.loads(match.group(1))
                return result_json
            else:
                # Si toujours pas de JSON valide, faire une analyse simplifiée
                return {
                    "title": "Non spécifié",
                    "company": "Non spécifié",
                    "location": "Non spécifié",
                    "skills": ["Non spécifié"],
                    "experience": "Non spécifié",
                    "responsibilities": ["Non spécifié"],
                    "requirements": ["Non spécifié"],
                    "salary": "Non spécifié",
                    "benefits": ["Non spécifié"],
                    "error": "Impossible d'extraire les informations structurées"
                }
    
    except Exception as e:
        raise Exception(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
