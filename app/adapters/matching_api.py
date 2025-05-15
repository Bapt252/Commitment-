#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""API REST pour le service de matching SmartMatch."""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from flask import Flask, request, jsonify

from app.adapters.matching_pipeline import MatchingPipeline

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingAPI")

# Configuration de l'API Flask
app = Flask(__name__)

# Initialisation du pipeline de matching
results_dir = os.environ.get("MATCHING_RESULTS_DIR", "matching_results")
cv_parser_url = os.environ.get("CV_PARSER_URL", "http://localhost:5051")
job_parser_url = os.environ.get("JOB_PARSER_URL", "http://localhost:5055")

pipeline = MatchingPipeline(cv_parser_url, job_parser_url, results_dir)

@app.route("/health", methods=["GET"])
def health_check():
    """
    Point de terminaison pour vérifier la santé du service.
    """
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route("/match", methods=["POST"])
def match_all():
    """
    Point de terminaison pour lancer un matching complet entre tous les CVs et fiches de poste.
    """
    try:
        # Exécuter le pipeline complet
        matching_results, insights = pipeline.run_full_pipeline()
        
        # Préparer la réponse
        response = {
            "status": "success",
            "matches_count": len(matching_results),
            "insights_count": len(insights),
            "top_matches": matching_results[:10] if matching_results else [],
            "insights": insights[:5] if insights else []
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Erreur lors du matching complet: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/match/cv/<cv_id>/job/<job_id>", methods=["GET"])
def match_specific(cv_id, job_id):
    """
    Point de terminaison pour lancer un matching spécifique entre un CV et une fiche de poste.
    """
    try:
        result = pipeline.match_specific(cv_id, job_id)
        
        if result:
            return jsonify({"status": "success", "result": result})
        else:
            return jsonify({"status": "error", "message": "Matching impossible ou aucun résultat trouvé"}), 404
    except Exception as e:
        logger.error(f"Erreur lors du matching spécifique: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/match/cv/<cv_id>/all", methods=["GET"])
def match_cv_with_all(cv_id):
    """
    Point de terminaison pour lancer un matching entre un CV et toutes les fiches de poste.
    """
    try:
        results = pipeline.match_cv_with_all_jobs(cv_id)
        
        # Trier les résultats par score décroissant
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return jsonify({
            "status": "success", 
            "matches_count": len(results),
            "results": results
        })
    except Exception as e:
        logger.error(f"Erreur lors du matching CV avec toutes les fiches: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/match/job/<job_id>/all", methods=["GET"])
def match_job_with_all(job_id):
    """
    Point de terminaison pour lancer un matching entre une fiche de poste et tous les CVs.
    """
    try:
        results = pipeline.match_job_with_all_cvs(job_id)
        
        # Trier les résultats par score décroissant
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return jsonify({
            "status": "success", 
            "matches_count": len(results),
            "results": results
        })
    except Exception as e:
        logger.error(f"Erreur lors du matching fiche de poste avec tous les CVs: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/match/results", methods=["GET"])
def get_all_results():
    """
    Point de terminaison pour récupérer tous les résultats de matching.
    """
    try:
        # Lister tous les fichiers de résultats dans le répertoire
        result_files = [f for f in os.listdir(results_dir) if f.startswith("matching_results_")]
        result_files.sort(reverse=True)  # Tri par date décroissante
        
        # Récupérer les 5 derniers résultats
        latest_results = []
        for filename in result_files[:5]:
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                results = json.load(f)
                latest_results.append({
                    "filename": filename,
                    "timestamp": filename.split("_")[-1].split(".")[0],
                    "matches_count": len(results),
                    "results": results[:10]  # Limiter à 10 résultats par fichier
                })
        
        return jsonify({
            "status": "success", 
            "count": len(latest_results),
            "results": latest_results
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des résultats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/match/insights", methods=["GET"])
def get_all_insights():
    """
    Point de terminaison pour récupérer tous les insights générés.
    """
    try:
        # Lister tous les fichiers d'insights dans le répertoire
        insight_files = [f for f in os.listdir(results_dir) if f.startswith("insights_")]
        insight_files.sort(reverse=True)  # Tri par date décroissante
        
        # Récupérer les 5 derniers insights
        latest_insights = []
        for filename in insight_files[:5]:
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                insights = json.load(f)
                latest_insights.append({
                    "filename": filename,
                    "timestamp": filename.split("_")[-1].split(".")[0],
                    "insights_count": len(insights),
                    "insights": insights  # Inclure tous les insights
                })
        
        return jsonify({
            "status": "success", 
            "count": len(latest_insights),
            "results": latest_insights
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des insights: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def start_api(host="0.0.0.0", port=5052, debug=False):
    """
    Démarre l'API REST.
    
    Args:
        host (str): Adresse d'hôte
        port (int): Port d'écoute
        debug (bool): Mode debug
    """
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Démarrer l'API
    start_api()
