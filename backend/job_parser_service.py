"""
Service pour l'analyse des fiches de poste avec GPT
"""
import os
import json
import time
import uuid
import io
import logging
import re
import requests
from dotenv import load_dotenv
import PyPDF2

# Configuration du logging
logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
JOB_EXPIRATION = int(os.environ.get('JOB_EXPIRATION', 86400))  # 24 heures par défaut

# Stockage temporaire des jobs en mémoire (à remplacer par une base de données en production)
jobs = {}

class JobParserService:
    """Service pour l'analyse des fiches de poste"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        if not self.api_key:
            logger.warning("Clé API OpenAI non configurée - le service GPT ne sera pas disponible")
    
    def queue_job(self, content):
        """
        Mettre en file d'attente un job d'analyse
        
        Args:
            content: Contenu texte de la fiche de poste
        
        Returns:
            dict: Informations sur le job (ID, statut)
        """
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
        thread = threading.Thread(target=self._process_job, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return {"job_id": job_id, "status": "pending"}

    def get_job_result(self, job_id):
        """
        Récupérer le résultat d'un job
        
        Args:
            job_id: Identifiant du job
        
        Returns:
            dict: Résultat du job ou statut courant
        """
        if job_id not in jobs:
            return {"error": "Job non trouvé"}, 404
        
        job = jobs[job_id]
        
        # Si le job est terminé, renvoyer le résultat
        if job["status"] == "done":
            return {"status": "done", "result": job["result"]}
        # Si le job est en erreur, renvoyer l'erreur
        elif job["status"] == "failed":
            return {"status": "failed", "error": job["error"]}
        # Sinon, le job est toujours en cours
        else:
            return {"status": job["status"], "message": "Job en cours de traitement"}

    def parse_pdf(self, file_content):
        """
        Extraire le texte d'un fichier PDF
        
        Args:
            file_content: Contenu binaire du fichier PDF
        
        Returns:
            str: Texte extrait du PDF
        """
        try:
            logger.info(f"Démarrage de l'extraction PDF, taille: {len(file_content)} octets")
            print(f"Démarrage de l'extraction PDF, taille: {len(file_content)} octets")
            
            # Essayer d'abord avec PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            logger.info(f"PDF chargé avec succès: {len(pdf_reader.pages)} pages détectées")
            print(f"PDF chargé avec succès: {len(pdf_reader.pages)} pages détectées")
            
            content = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
                    logger.info(f"Page {i+1}: {len(page_text)} caractères extraits")
                    print(f"Page {i+1}: {len(page_text)} caractères extraits")
                else:
                    logger.warning(f"Page {i+1}: Aucun texte extractible")
                    print(f"Page {i+1}: Aucun texte extractible")
            
            # Si PyPDF2 n'a pas extrait de texte, essayer avec pdfminer si disponible
            if not content.strip():
                logger.warning("PyPDF2 n'a pas réussi à extraire du texte, essai avec d'autres méthodes")
                print("PyPDF2 n'a pas réussi à extraire du texte, essai avec d'autres méthodes")
                
                # Essayer avec pdfminer.six si disponible
                try:
                    import importlib.util
                    if importlib.util.find_spec("pdfminer"):
                        from pdfminer.high_level import extract_text_from_binary
                        logger.info("Tentative avec pdfminer.six")
                        content = extract_text_from_binary(file_content)
                        if content:
                            logger.info(f"Extraction réussie avec pdfminer.six: {len(content)} caractères")
                except ImportError:
                    logger.warning("pdfminer.six non disponible")
                
                # Essayer avec PyMuPDF si disponible
                if not content.strip():
                    try:
                        import importlib.util
                        if importlib.util.find_spec("fitz"):
                            import fitz  # PyMuPDF
                            logger.info("Tentative avec PyMuPDF")
                            mem_stream = io.BytesIO(file_content)
                            doc = fitz.open(stream=mem_stream, filetype="pdf")
                            content = ""
                            for page in doc:
                                content += page.get_text()
                            logger.info(f"Extraction réussie avec PyMuPDF: {len(content)} caractères")
                    except ImportError:
                        logger.warning("PyMuPDF non disponible")
            
            if not content.strip():
                error_msg = "Le PDF ne semble pas contenir de texte extractible ou utilise un format non pris en charge"
                logger.error(error_msg)
                print(error_msg)
                
                # Retourner un message plus convivial pour l'utilisateur
                raise ValueError(error_msg + ". Essayez de copier-coller le texte manuellement.")
            
            # Afficher les 200 premiers caractères pour débogage
            preview = content[:200].replace('\n', ' ')
            logger.info(f"Début du contenu extrait: '{preview}...'")
            print(f"Début du contenu extrait: '{preview}...'")
            
            return content
        except Exception as e:
            logger.error(f"ERREUR lors de l'extraction du PDF: {str(e)}")
            print(f"ERREUR lors de l'extraction du PDF: {str(e)}")
            raise ValueError(f"Impossible de lire le PDF: {str(e)}")

    def _process_job(self, job_id):
        """
        Traiter un job d'analyse
        
        Args:
            job_id: Identifiant du job
        """
        job = jobs[job_id]
        
        try:
            # Mettre à jour le statut du job
            job["status"] = "processing"
            
            # Extraire les informations (avec ou sans GPT selon la configuration)
            if self.api_key:
                result = self._extract_job_info_with_gpt(job["content"])
            else:
                # Fallback sur une analyse locale simplifiée si pas de clé API
                result = self._extract_job_info_locally(job["content"])
            
            # Mettre à jour le job avec le résultat
            job["status"] = "done"
            job["result"] = result
            job["completed_at"] = time.time()
            
            # Nettoyer le contenu original pour économiser de l'espace
            job.pop("content", None)
            
            logger.info(f"Job {job_id} traité avec succès")
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement du job {job_id}: {str(e)}")
            # En cas d'erreur, mettre à jour le statut et stocker l'erreur
            job["status"] = "failed"
            job["error"] = str(e)
            job["completed_at"] = time.time()
            
            # Nettoyer le contenu original pour économiser de l'espace
            job.pop("content", None)
    
    def _extract_job_info_with_gpt(self, content):
        """
        Utiliser GPT pour extraire les informations de la fiche de poste
        
        Args:
            content: Contenu texte de la fiche de poste
        
        Returns:
            dict: Informations structurées extraites de la fiche de poste
        """
        if not self.api_key:
            raise ValueError("Clé API OpenAI non configurée")
        
        # Limiter la taille du contenu pour éviter les problèmes avec l'API
        if len(content) > 15000:
            logger.info(f"Contenu tronqué de {len(content)} à 15000 caractères")
            content = content[:15000] + "...[contenu tronqué pour respecter la limite de l'API]"
        
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
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Tu es un assistant spécialisé dans l'analyse de fiches de poste. Tu extrais avec précision les informations pertinentes."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            logger.info(f"Envoi de la requête à l'API OpenAI (modèle: {self.model})")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # 60 secondes de timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API OpenAI: {response.text}")
                raise ValueError(f"Erreur API OpenAI: {response.status_code}")
            
            result = response.json()
            result_text = result["choices"][0]["message"]["content"].strip()
            logger.info("Réponse reçue de l'API OpenAI")
            
            # Essayer de parser le JSON
            try:
                result_json = json.loads(result_text)
                logger.info("JSON correctement parsé")
                return result_json
            except json.JSONDecodeError:
                # Si GPT n'a pas renvoyé un JSON valide, essayer d'extraire le bloc JSON
                logger.warning("Réponse non JSON, tentative d'extraction d'un bloc JSON")
                json_pattern = r'```json\s*(.*?)\s*```'
                match = re.search(json_pattern, result_text, re.DOTALL)
                
                if match:
                    result_json = json.loads(match.group(1))
                    logger.info("JSON extrait du bloc de code")
                    return result_json
                else:
                    # Si toujours pas de JSON valide, faire une analyse simplifiée
                    logger.warning("JSON non valide retourné par GPT, utilisation de l'analyse locale")
                    return self._extract_job_info_locally(content)
        
        except Exception as e:
            logger.exception(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
            raise ValueError(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")

    def _extract_job_info_locally(self, text):
        """
        Analyse locale simplifiée d'une fiche de poste
        
        Args:
            text: Contenu texte de la fiche de poste
        
        Returns:
            dict: Informations extraites de la fiche de poste
        """
        logger.info("Utilisation de l'analyse locale")
        
        # Enlever les entêtes techniques PDF si présents
        if text.startswith("%PDF"):
            logger.warning("Entête PDF détecté, nettoyage en cours")
            # Trouver la première ligne qui ne contient pas de caractères spéciaux
            lines = text.split('\n')
            cleaned_lines = []
            started = False
            
            for line in lines:
                # Ignorer les lignes d'entête PDF
                if not started and (line.startswith("%") or re.match(r'^[^a-zA-Z0-9\s]', line)):
                    continue
                else:
                    started = True
                    cleaned_lines.append(line)
            
            text = '\n'.join(cleaned_lines)
            logger.info(f"Texte nettoyé: {len(text)} caractères")
        
        # Afficher le début du texte pour débogage
        preview = text[:200].replace('\n', ' ')
        logger.info(f"Début du texte analysé: '{preview}...'")
        
        # Titre du poste (recherche d'un titre au début du texte)
        title_match = re.search(r'^(.+?)(?:[\n\r]|$)', text.strip())
        title = title_match.group(1) if title_match else "Non spécifié"
        
        # Essayer plusieurs patterns pour trouver le titre du poste
        if title == "Non spécifié" or len(title) < 3:
            title_patterns = [
                r'(?:poste|position|job|offre)\s*:?\s*([^\n\r.,]+)',
                r'(?:recrut\w+)\s+(?:un|une|des)?\s+([^\n\r.,]+)',
                r'(?:cherch\w+)\s+(?:un|une|des)?\s+([^\n\r.,]+)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    break
        
        # Essayer de trouver l'entreprise
        company_match = re.search(r'(?:société|entreprise|company)\s*:?\s*([^\n\r,]+)', text, re.IGNORECASE)
        company = company_match.group(1).strip() if company_match else "Non spécifié"
        
        # Essayer de trouver le lieu
        location_match = re.search(r'(?:lieu|location|adresse|ville|localisation)\s*:?\s*([^\n\r,]+)', text, re.IGNORECASE)
        location = location_match.group(1).strip() if location_match else "Non spécifié"
        
        # Essayer de trouver l'expérience
        experience_match = re.search(r'(?:expérience|experience)\s*:?\s*([^\n\r.,]+)', text, re.IGNORECASE)
        experience = experience_match.group(1).strip() if experience_match else "Non spécifié"
        
        # Essayer de trouver le salaire
        salary_match = re.search(r'(?:salaire|rémunération|salary|compensation)\s*:?\s*([^\n\r,]+)', text, re.IGNORECASE)
        salary = salary_match.group(1).strip() if salary_match else "Non spécifié"
        
        # Extraction des compétences (simplifiée)
        skills = ["Non spécifié"]
        skills_section = re.search(r'(?:compétences|skills|profil|qualifications).*?((?:\n|.)*?)(?:\n\s*\n|\Z)', text, re.IGNORECASE)
        if skills_section:
            # Rechercher des listes à puces
            skills_content = skills_section.group(1)
            skills_items = re.findall(r'[•\-*]\s*([^\n]+)', skills_content)
            if skills_items:
                skills = [item.strip() for item in skills_items if item.strip()]
        
        # Extraction des responsabilités (simplifiée)
        responsibilities = ["Non spécifié"]
        resp_section = re.search(r'(?:responsabilités|missions|tâches|duties).*?((?:\n|.)*?)(?:\n\s*\n|\Z)', text, re.IGNORECASE)
        if resp_section:
            # Rechercher des listes à puces
            resp_content = resp_section.group(1)
            resp_items = re.findall(r'[•\-*]\s*([^\n]+)', resp_content)
            if resp_items:
                responsibilities = [item.strip() for item in resp_items if item.strip()]
        
        # Extraction des avantages (simplifiée)
        benefits = ["Non spécifié"]
        benefits_section = re.search(r'(?:avantages|benefits|nous offrons|we offer).*?((?:\n|.)*?)(?:\n\s*\n|\Z)', text, re.IGNORECASE)
        if benefits_section:
            # Rechercher des listes à puces
            benefits_content = benefits_section.group(1)
            benefits_items = re.findall(r'[•\-*]\s*([^\n]+)', benefits_content)
            if benefits_items:
                benefits = [item.strip() for item in benefits_items if item.strip()]
        
        # Renvoyer les informations extraites
        return {
            "title": title,
            "company": company,
            "location": location,
            "skills": skills,
            "experience": experience,
            "responsibilities": responsibilities,
            "requirements": ["Extraction automatique des prérequis non disponible sans GPT"],
            "salary": salary,
            "benefits": benefits
        }


# Créer une instance du service
job_parser = JobParserService()


def cleanup_expired_jobs():
    """Nettoie les jobs qui ont expiré"""
    now = time.time()
    expired_jobs = []
    
    for job_id, job in jobs.items():
        # Calculer l'âge du job
        job_time = job.get("completed_at", job.get("created_at", now))
        job_age = now - job_time
        
        # Si le job est plus vieux que JOB_EXPIRATION, le marquer pour suppression
        if job_age > JOB_EXPIRATION:
            expired_jobs.append(job_id)
    
    # Supprimer les jobs expirés
    for job_id in expired_jobs:
        del jobs[job_id]
    
    if expired_jobs:
        logger.info(f"Nettoyage: {len(expired_jobs)} jobs expirés supprimés")

# Démarrer le thread de nettoyage
import threading

def cleanup_thread():
    while True:
        time.sleep(3600)  # Une fois par heure
        cleanup_expired_jobs()

cleanup_thread_instance = threading.Thread(target=cleanup_thread)
cleanup_thread_instance.daemon = True
cleanup_thread_instance.start()
