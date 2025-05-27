#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 Exemple d'intégration pondération dynamique dans l'app SuperSmartMatch
Démontre comment ajouter le questionnaire candidat et utiliser la v2.1
"""

import sys
import os
import json
from flask import Flask, request, jsonify
from typing import Dict, Any, List

# Ajouter le répertoire racine au path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from algorithms.supersmartmatch import SuperSmartMatchAlgorithm

# ===== 🎯 NOUVEAUX ENDPOINTS QUESTIONNAIRE =====

def create_candidate_questionnaire_route(app: Flask):
    """
    🆕 Route pour créer/mettre à jour le questionnaire priorités candidat
    """
    @app.route('/api/candidate/<candidate_id>/questionnaire', methods=['POST', 'PUT'])
    def update_candidate_questionnaire(candidate_id: str):
        """
        Met à jour les priorités d'un candidat
        
        Body:
        {
            "priorites_candidat": {
                "evolution": 8,
                "remuneration": 6,
                "proximite": 4,
                "flexibilite": 9
            },
            "flexibilite_attendue": {
                "teletravail": "partiel",
                "horaires_flexibles": true,
                "rtt_important": true
            }
        }
        """
        try:
            data = request.get_json()
            
            # Validation des priorités
            priorites = data.get('priorites_candidat', {})
            required_levers = ['evolution', 'remuneration', 'proximite', 'flexibilite']
            
            for lever in required_levers:
                if lever not in priorites:
                    return jsonify({
                        'error': f'Levier manquant: {lever}',
                        'required_levers': required_levers
                    }), 400
                
                note = priorites[lever]
                if not isinstance(note, (int, float)) or not (1 <= note <= 10):
                    return jsonify({
                        'error': f'Note invalide pour {lever}: {note} (doit être entre 1 et 10)'
                    }), 400
            
            # Validation flexibilité attendue
            flex_attendue = data.get('flexibilite_attendue', {})
            if 'teletravail' in flex_attendue:
                valid_teletravail = ['aucun', 'partiel', 'total']
                if flex_attendue['teletravail'] not in valid_teletravail:
                    return jsonify({
                        'error': f'Valeur télétravail invalide: {flex_attendue["teletravail"]}',
                        'valid_values': valid_teletravail
                    }), 400
            
            # Sauvegarder les données questionnaire (ici simulation)
            questionnaire_data = {
                'priorites_candidat': priorites,
                'flexibilite_attendue': flex_attendue,
                'date_maj': '2025-05-27',
                'version': '2.1'
            }
            
            # TODO: Sauvegarder en base de données
            # db.candidates.update_one(
            #     {'id': candidate_id}, 
            #     {'$set': {'questionnaire_data': questionnaire_data}}
            # )
            
            return jsonify({
                'message': 'Questionnaire mis à jour avec succès',
                'candidate_id': candidate_id,
                'questionnaire_data': questionnaire_data,
                'ponderation_preview': _preview_weighting(priorites)
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def _preview_weighting(priorites: Dict[str, float]) -> Dict[str, Any]:
    """
    Prévisualise la pondération qui serait calculée
    """
    algorithm = SuperSmartMatchAlgorithm()
    fake_candidate = {'questionnaire_data': {'priorites_candidat': priorites}}
    weights = algorithm.calculate_dynamic_weights(fake_candidate)
    
    # Calculer les variations vs base
    base_weights = algorithm.config['ponderation_base']
    variations = {}
    for critere in weights:
        variation = ((weights[critere] / base_weights[critere]) - 1) * 100
        variations[critere] = round(variation, 1)
    
    return {
        'ponderation_adaptee': {k: round(v*100, 1) for k, v in weights.items()},
        'variations_vs_base': variations,
        'levier_dominant': max(priorites, key=priorites.get),
        'note_dominante': max(priorites.values())
    }

# ===== 🔄 MODIFICATION ENDPOINT MATCHING EXISTANT =====

def enhance_matching_route(app: Flask):
    """
    ✨ Améliore l'endpoint de matching existant pour supporter la v2.1
    """
    @app.route('/api/supersmartmatch', methods=['POST'])
    def supersmartmatch_v21():
        """
        Endpoint SuperSmartMatch v2.1 avec pondération dynamique
        
        Body:
        {
            "candidat": {
                "id": "cand_123",
                "annees_experience": 5,
                "salaire_souhaite": 55000,
                "competences": ["python", "javascript"],
                "questionnaire_data": {  // ⚡ NOUVEAU
                    "priorites_candidat": {
                        "evolution": 8,
                        "remuneration": 6,
                        "proximite": 4,
                        "flexibilite": 9
                    },
                    "flexibilite_attendue": {
                        "teletravail": "partiel",
                        "horaires_flexibles": true,
                        "rtt_important": true
                    }
                }
            },
            "offres": [...],
            "limit": 10
        }
        """
        try:
            data = request.get_json()
            candidat = data.get('candidat', {})
            offres = data.get('offres', [])
            limit = data.get('limit', 10)
            
            # Initialiser l'algorithme v2.1
            algorithm = SuperSmartMatchAlgorithm()
            
            # Vérifier si questionnaire présent
            has_questionnaire = 'questionnaire_data' in candidat
            
            # Lancer le matching avec pondération dynamique
            results = algorithm.match_candidate_with_jobs(candidat, offres, limit)
            
            # Enrichir la réponse avec infos pondération
            response = {
                'version': '2.1',
                'candidat_id': candidat.get('id'),
                'has_dynamic_weighting': has_questionnaire,
                'results': results,
                
                # ⚡ NOUVELLES INFOS
                'ponderation_info': {
                    'type': 'dynamique' if has_questionnaire else 'base',
                    'weights': results[0]['ponderation_dynamique'] if results else None,
                    'priorites_candidat': candidat.get('questionnaire_data', {}).get('priorites_candidat'),
                },
                
                'summary': {
                    'total_offers_analyzed': len(offres),
                    'results_returned': len(results),
                    'best_score': results[0]['matching_score_entreprise'] if results else 0,
                    'algorithm_features': [
                        'intelligence_reasoning',
                        'detailed_scoring', 
                        'flexibility_analysis',
                        'dynamic_weighting' if has_questionnaire else 'fixed_weighting'
                    ]
                }
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'version': '2.1',
                'message': 'Erreur lors du matching SuperSmartMatch'
            }), 500

# ===== 📊 NOUVEAU ENDPOINT ANALYTICS =====

def create_analytics_route(app: Flask):
    """
    📊 Analytics pour comprendre l'impact de la pondération dynamique
    """
    @app.route('/api/analytics/weighting-impact', methods=['POST'])
    def analyze_weighting_impact():
        """
        Compare l'impact pondération fixe vs dynamique pour un candidat
        
        Body:
        {
            "candidat": {...},
            "offres": [...],
            "compare_scenarios": true
        }
        """
        try:
            data = request.get_json()
            candidat = data.get('candidat', {})
            offres = data.get('offres', [])
            
            algorithm = SuperSmartMatchAlgorithm()
            
            # Scénario 1: Avec pondération dynamique
            results_dynamic = algorithm.match_candidate_with_jobs(candidat, offres, limit=5)
            
            # Scénario 2: Sans questionnaire (pondération fixe)
            candidat_sans_questionnaire = {k: v for k, v in candidat.items() if k != 'questionnaire_data'}
            results_fixed = algorithm.match_candidate_with_jobs(candidat_sans_questionnaire, offres, limit=5)
            
            # Analyse comparative
            comparison = []
            for i in range(min(len(results_dynamic), len(results_fixed))):
                job_id = results_dynamic[i]['id']
                dynamic_score = results_dynamic[i]['matching_score_entreprise']
                
                # Trouver le même job dans les résultats fixes
                fixed_score = None
                fixed_rank = None
                for j, fixed_result in enumerate(results_fixed):
                    if fixed_result['id'] == job_id:
                        fixed_score = fixed_result['matching_score_entreprise']
                        fixed_rank = j + 1
                        break
                
                if fixed_score is not None:
                    comparison.append({
                        'job_id': job_id,
                        'job_title': results_dynamic[i]['titre'],
                        'dynamic_score': dynamic_score,
                        'dynamic_rank': i + 1,
                        'fixed_score': fixed_score,
                        'fixed_rank': fixed_rank,
                        'score_difference': dynamic_score - fixed_score,
                        'rank_difference': fixed_rank - (i + 1)
                    })
            
            # Statistiques globales
            score_differences = [comp['score_difference'] for comp in comparison]
            rank_differences = [comp['rank_difference'] for comp in comparison]
            
            analytics = {
                'has_questionnaire': 'questionnaire_data' in candidat,
                'dynamic_weights': results_dynamic[0]['ponderation_dynamique'] if results_dynamic else None,
                'fixed_weights': algorithm.config['ponderation_base'],
                
                'comparison': comparison,
                
                'impact_statistics': {
                    'avg_score_difference': sum(score_differences) / len(score_differences) if score_differences else 0,
                    'max_score_difference': max(score_differences) if score_differences else 0,
                    'min_score_difference': min(score_differences) if score_differences else 0,
                    'avg_rank_change': sum(rank_differences) / len(rank_differences) if rank_differences else 0,
                    'jobs_improved_ranking': len([r for r in rank_differences if r > 0]),
                    'jobs_degraded_ranking': len([r for r in rank_differences if r < 0])
                },
                
                'recommendations': _generate_impact_recommendations(candidat, score_differences, rank_differences)
            }
            
            return jsonify(analytics), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def _generate_impact_recommendations(candidat: Dict, score_diffs: List, rank_diffs: List) -> List[str]:
    """
    Génère des recommandations basées sur l'impact observé
    """
    recommendations = []
    
    if not candidat.get('questionnaire_data'):
        recommendations.append("Faire remplir le questionnaire de priorités pour personnaliser le matching")
        return recommendations
    
    avg_score_diff = sum(score_diffs) / len(score_diffs) if score_diffs else 0
    avg_rank_diff = sum(rank_diffs) / len(rank_diffs) if rank_diffs else 0
    
    if avg_score_diff > 5:
        recommendations.append("La pondération dynamique améliore significativement les scores (+{:.1f}% en moyenne)".format(avg_score_diff))
    elif avg_score_diff < -5:
        recommendations.append("La pondération fixe pourrait être plus adaptée pour ce profil")
    else:
        recommendations.append("Impact modéré de la pondération dynamique")
    
    if avg_rank_diff > 1:
        recommendations.append("Le classement des offres change significativement avec les priorités candidat")
    
    priorites = candidat.get('questionnaire_data', {}).get('priorites_candidat', {})
    max_priority = max(priorites, key=priorites.get) if priorites else None
    if max_priority:
        recommendations.append(f"Le levier '{max_priority}' domine la personnalisation du matching")
    
    return recommendations

# ===== 🎮 DEMO INTERACTIVE =====

def create_demo_routes(app: Flask):
    """
    🎮 Routes pour une démo interactive de la pondération dynamique
    """
    @app.route('/api/demo/candidate-profiles', methods=['GET'])
    def get_demo_profiles():
        """
        Retourne des profils candidat types pour la démo
        """
        profiles = {
            'salaire_prioritaire': {
                'nom': 'Marie Dubois - Salaire Prioritaire',
                'description': 'Candidate expérimentée qui privilégie la rémunération',
                'questionnaire': {
                    'priorites_candidat': {'evolution': 4, 'remuneration': 9, 'proximite': 6, 'flexibilite': 5},
                    'flexibilite_attendue': {'teletravail': 'partiel', 'horaires_flexibles': False, 'rtt_important': False}
                }
            },
            'evolution_prioritaire': {
                'nom': 'Thomas Martin - Évolution Prioritaire', 
                'description': 'Jeune candidat ambitieux qui veut progresser rapidement',
                'questionnaire': {
                    'priorites_candidat': {'evolution': 10, 'remuneration': 3, 'proximite': 5, 'flexibilite': 6},
                    'flexibilite_attendue': {'teletravail': 'ouvert', 'horaires_flexibles': True, 'rtt_important': False}
                }
            },
            'flexibilite_prioritaire': {
                'nom': 'Sophie Chen - Flexibilité Prioritaire',
                'description': 'Candidate qui privilégie work-life balance et autonomie',
                'questionnaire': {
                    'priorites_candidat': {'evolution': 5, 'remuneration': 4, 'proximite': 3, 'flexibilite': 10},
                    'flexibilite_attendue': {'teletravail': 'total', 'horaires_flexibles': True, 'rtt_important': True}
                }
            },
            'proximite_prioritaire': {
                'nom': 'Jean Rousseau - Proximité Prioritaire',
                'description': 'Candidat senior avec contraintes géographiques familiales',
                'questionnaire': {
                    'priorites_candidat': {'evolution': 6, 'remuneration': 7, 'proximite': 10, 'flexibilite': 4},
                    'flexibilite_attendue': {'teletravail': 'aucun', 'horaires_flexibles': False, 'rtt_important': False}
                }
            }
        }
        
        return jsonify({
            'profiles': profiles,
            'usage': 'Utilisez ces profils pour tester l\'impact de la pondération dynamique'
        })

# ===== 🚀 EXEMPLE UTILISATION =====

def create_example_app():
    """
    Crée une app Flask d'exemple avec tous les nouveaux endpoints
    """
    app = Flask(__name__)
    
    # Routes questionnaire
    create_candidate_questionnaire_route(app)
    
    # Route matching améliorée
    enhance_matching_route(app)
    
    # Routes analytics  
    create_analytics_route(app)
    
    # Routes démo
    create_demo_routes(app)
    
    @app.route('/api/info', methods=['GET'])
    def get_algorithm_info():
        """Info sur SuperSmartMatch v2.1"""
        algorithm = SuperSmartMatchAlgorithm()
        return jsonify(algorithm.get_algorithm_info())
    
    return app

# ===== 🧪 EXEMPLE COMPLET =====

def example_usage():
    """
    Exemple complet d'utilisation de la pondération dynamique
    """
    print("🎯 === EXEMPLE PONDÉRATION DYNAMIQUE ===\n")
    
    # 1. Candidat avec questionnaire
    candidat_complet = {
        'id': 'cand_demo',
        'nom': 'Alex Développeur',
        'annees_experience': 5,
        'salaire_souhaite': 55000,
        'adresse': 'Paris',
        'competences': ['python', 'javascript', 'react', 'django'],
        'langues': ['français', 'anglais'],
        
        # ⚡ NOUVEAU: Questionnaire priorités
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 8,        # Priorité élevée
                'remuneration': 6,     # Moyenne
                'proximite': 4,        # Faible (pas de contrainte géo)
                'flexibilite': 9       # Très important
            },
            'flexibilite_attendue': {
                'teletravail': 'partiel',
                'horaires_flexibles': True,
                'rtt_important': True
            }
        }
    }
    
    # 2. Offres d'exemple
    offres = [
        {
            'id': 'job_1',
            'titre': 'Senior Python Developer',
            'entreprise': 'TechCorp',
            'localisation': 'Paris',
            'experience_requise': 5,
            'salaire': '50-60K€',
            'budget_max': 60000,
            'competences': ['python', 'django', 'postgresql'],
            'politique_remote': 'télétravail partiel',
            'horaires_flexibles': True,
            'jours_rtt': 15,
            'perspectives_evolution': True
        }
    ]
    
    # 3. Lancer l'algorithme v2.1
    algorithm = SuperSmartMatchAlgorithm()
    results = algorithm.match_candidate_with_jobs(candidat_complet, offres)
    
    # 4. Analyser les résultats
    if results:
        result = results[0]
        
        print(f"🎯 Candidat: {candidat_complet['nom']}")
        print(f"📊 Pondération adaptée: {result['ponderation_dynamique']}")
        print(f"🏆 Score final: {result['matching_score_entreprise']}%")
        print(f"✨ Critère flexibilité: {result['scores_detailles']['flexibilite']['pourcentage']}%")
        
        if 'ponderation' in result['explications_entreprise']:
            print(f"💡 {result['explications_entreprise']['ponderation']}")
    
    print("\n✅ Exemple terminé!")

if __name__ == "__main__":
    # Lancer l'exemple
    example_usage()
    
    # Pour lancer l'app Flask de démo:
    # app = create_example_app()
    # app.run(debug=True, port=5064)
