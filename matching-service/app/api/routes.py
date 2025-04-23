import json
import requests
from flask import Blueprint, request, jsonify, current_app
from app.algorithms.matcher import match_profile_to_jobs, match_job_to_profiles
import pika
import threading

api = Blueprint('api', __name__)

# Fonction pour établir une connexion à RabbitMQ
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        username=current_app.config.get('RABBITMQ_USER', 'guest'),
        password=current_app.config.get('RABBITMQ_PASSWORD', 'guest')
    )
    parameters = pika.ConnectionParameters(
        host=current_app.config.get('RABBITMQ_HOST', 'rabbitmq'),
        port=current_app.config.get('RABBITMQ_PORT', 5672),
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

# Fonction pour récupérer des données depuis d'autres services
def get_service_data(service_url, endpoint):
    """Récupérer des données depuis un autre service"""
    url = f"{service_url}/{endpoint}"
    try:
        response = requests.get(url, timeout=current_app.config.get('REQUEST_TIMEOUT', 5))
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.error(f"Erreur {response.status_code} lors de la récupération des données depuis {url}")
            return None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erreur lors de la connexion à {url}: {str(e)}")
        return None

# Route pour trouver les candidats correspondant à une offre d'emploi
@api.route('/job/<job_id>/candidates', methods=['GET'])
def get_matching_candidates(job_id):
    """Récupération des candidats correspondant à une offre d'emploi"""
    try:
        # Récupérer l'offre d'emploi depuis le Job Service
        job_service_url = current_app.config.get('JOB_SERVICE_URL')
        job_data = get_service_data(job_service_url, f"jobs/{job_id}")
        
        if not job_data:
            return jsonify({"error": "Offre d'emploi non trouvée ou service indisponible"}), 404
        
        # Récupérer tous les profils depuis le Profile Service
        profile_service_url = current_app.config.get('PROFILE_SERVICE_URL')
        profiles_data = get_service_data(profile_service_url, "profiles")
        
        if not profiles_data:
            return jsonify({"error": "Impossible de récupérer les profils"}), 503
        
        # Effectuer le matching
        matching_results = match_job_to_profiles(job_data, profiles_data)
        
        # Tri des résultats par score de matching
        sorted_results = sorted(matching_results, key=lambda x: x['matching_score'], reverse=True)
        
        return jsonify({
            "job_id": job_id,
            "job_title": job_data.get('title', ''),
            "total_candidates": len(sorted_results),
            "candidates": sorted_results
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du matching des candidats: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Route pour trouver les offres d'emploi correspondant à un profil
@api.route('/profile/<profile_id>/jobs', methods=['GET'])
def get_matching_jobs(profile_id):
    """Récupération des offres d'emploi correspondant à un profil"""
    try:
        # Récupérer le profil depuis le Profile Service
        profile_service_url = current_app.config.get('PROFILE_SERVICE_URL')
        profile_data = get_service_data(profile_service_url, f"profiles/{profile_id}")
        
        if not profile_data:
            return jsonify({"error": "Profil non trouvé ou service indisponible"}), 404
        
        # Récupérer toutes les offres d'emploi depuis le Job Service
        job_service_url = current_app.config.get('JOB_SERVICE_URL')
        jobs_data = get_service_data(job_service_url, "jobs")
        
        if not jobs_data:
            return jsonify({"error": "Impossible de récupérer les offres d'emploi"}), 503
        
        # Effectuer le matching
        matching_results = match_profile_to_jobs(profile_data, jobs_data)
        
        # Tri des résultats par score de matching
        sorted_results = sorted(matching_results, key=lambda x: x['matching_score'], reverse=True)
        
        return jsonify({
            "profile_id": profile_id,
            "candidate_name": profile_data.get('name', ''),
            "total_jobs": len(sorted_results),
            "jobs": sorted_results
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du matching des offres d'emploi: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Gestionnaire de messages pour les mises à jour de profil
def handle_profile_update(ch, method, properties, body):
    """Traiter les mises à jour de profil depuis RabbitMQ"""
    try:
        profile_data = json.loads(body)
        profile_id = profile_data.get('id')
        
        current_app.logger.info(f"Mise à jour du profil reçue: {profile_id}")
        
        # Récupérer toutes les offres d'emploi depuis le Job Service
        job_service_url = current_app.config.get('JOB_SERVICE_URL')
        jobs_data = get_service_data(job_service_url, "jobs")
        
        if not jobs_data:
            current_app.logger.error("Impossible de récupérer les offres d'emploi pour le matching automatique")
            return
        
        # Effectuer le matching
        matching_results = match_profile_to_jobs(profile_data, jobs_data)
        
        # Filtrer les résultats avec un score de matching élevé
        threshold = current_app.config.get('MATCHING_THRESHOLD', 0.7)
        high_matches = [match for match in matching_results if match['matching_score'] >= threshold]
        
        if high_matches:
            # Envoyer des notifications pour les correspondances élevées
            notification_service_url = current_app.config.get('NOTIFICATION_SERVICE_URL')
            for match in high_matches:
                notification_data = {
                    "type": "job_match",
                    "recipient_id": profile_id,
                    "data": {
                        "job_id": match['job_id'],
                        "job_title": match['job_title'],
                        "matching_score": match['matching_score']
                    }
                }
                
                try:
                    requests.post(
                        f"{notification_service_url}/send",
                        json=notification_data,
                        timeout=current_app.config.get('REQUEST_TIMEOUT', 5)
                    )
                except requests.exceptions.RequestException as e:
                    current_app.logger.error(f"Erreur lors de l'envoi de notification: {str(e)}")
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du traitement de la mise à jour du profil: {str(e)}", exc_info=True)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Gestionnaire de messages pour les nouvelles offres d'emploi
def handle_job_creation(ch, method, properties, body):
    """Traiter les nouvelles offres d'emploi depuis RabbitMQ"""
    try:
        job_data = json.loads(body)
        job_id = job_data.get('id')
        
        current_app.logger.info(f"Nouvelle offre d'emploi reçue: {job_id}")
        
        # Récupérer tous les profils depuis le Profile Service
        profile_service_url = current_app.config.get('PROFILE_SERVICE_URL')
        profiles_data = get_service_data(profile_service_url, "profiles")
        
        if not profiles_data:
            current_app.logger.error("Impossible de récupérer les profils pour le matching automatique")
            return
        
        # Effectuer le matching
        matching_results = match_job_to_profiles(job_data, profiles_data)
        
        # Filtrer les résultats avec un score de matching élevé
        threshold = current_app.config.get('MATCHING_THRESHOLD', 0.7)
        high_matches = [match for match in matching_results if match['matching_score'] >= threshold]
        
        if high_matches:
            # Envoyer des notifications pour les correspondances élevées
            notification_service_url = current_app.config.get('NOTIFICATION_SERVICE_URL')
            for match in high_matches:
                notification_data = {
                    "type": "profile_match",
                    "recipient_id": match['profile_id'],
                    "data": {
                        "job_id": job_id,
                        "job_title": job_data.get('title', ''),
                        "matching_score": match['matching_score']
                    }
                }
                
                try:
                    requests.post(
                        f"{notification_service_url}/send",
                        json=notification_data,
                        timeout=current_app.config.get('REQUEST_TIMEOUT', 5)
                    )
                except requests.exceptions.RequestException as e:
                    current_app.logger.error(f"Erreur lors de l'envoi de notification: {str(e)}")
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du traitement de la nouvelle offre d'emploi: {str(e)}", exc_info=True)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Démarrer les consommateurs RabbitMQ dans des threads séparés
def start_rabbitmq_consumers():
    def profile_consumer():
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Déclarer la queue pour les mises à jour de profil
            channel.queue_declare(queue='profile_updates', durable=True)
            channel.basic_consume(queue='profile_updates', on_message_callback=handle_profile_update)
            
            current_app.logger.info("Démarrage du consommateur pour les mises à jour de profil")
            channel.start_consuming()
        except Exception as e:
            current_app.logger.error(f"Erreur dans le consommateur de profils: {str(e)}", exc_info=True)
    
    def job_consumer():
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Déclarer la queue pour les nouvelles offres d'emploi
            channel.queue_declare(queue='job_creations', durable=True)
            channel.basic_consume(queue='job_creations', on_message_callback=handle_job_creation)
            
            current_app.logger.info("Démarrage du consommateur pour les nouvelles offres d'emploi")
            channel.start_consuming()
        except Exception as e:
            current_app.logger.error(f"Erreur dans le consommateur d'offres d'emploi: {str(e)}", exc_info=True)
    
    # Démarrer les threads de consommation
    profile_thread = threading.Thread(target=profile_consumer, daemon=True)
    profile_thread.start()
    
    job_thread = threading.Thread(target=job_consumer, daemon=True)
    job_thread.start()

# Démarrer les consommateurs RabbitMQ lorsque l'application est prête
@api.before_app_first_request
def setup_rabbitmq():
    start_rabbitmq_consumers()
