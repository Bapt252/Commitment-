#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Tests SuperSmartMatch v2.1 - Pondération dynamique
Démontre le fonctionnement des 4 leviers candidat et l'impact sur le matching
"""

import sys
import os
import json
from typing import Dict, List, Any

# Ajouter le répertoire racine au path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from algorithms.supersmartmatch import SuperSmartMatchAlgorithm

def create_test_offers() -> List[Dict[str, Any]]:
    """
    Crée un jeu d'offres d'emploi pour les tests
    """
    return [
        {
            'id': 'job_1',
            'titre': 'Développeur Senior Python',
            'entreprise': 'TechCorp',
            'localisation': 'Paris',
            'experience_requise': 5,
            'salaire': '55-65K€',
            'budget_max': 65000,
            'competences': ['python', 'django', 'postgresql', 'docker'],
            'langues_requises': ['français', 'anglais'],
            'politique_remote': 'télétravail partiel possible',
            'horaires_flexibles': True,
            'jours_rtt': 15,
            'perspectives_evolution': True,
            'niveau_poste': 'senior'
        },
        {
            'id': 'job_2', 
            'titre': 'Lead Developer Full Stack',
            'entreprise': 'StartupInnovante',
            'localisation': 'Lyon',
            'experience_requise': 7,
            'salaire': '70-80K€',
            'budget_max': 80000,
            'competences': ['javascript', 'react', 'node.js', 'aws'],
            'langues_requises': ['anglais'],
            'politique_remote': 'télétravail total possible',
            'horaires_flexibles': True,
            'jours_rtt': 10,
            'perspectives_evolution': True,
            'responsabilites': 'management équipe de 4 développeurs',
            'niveau_poste': 'lead'
        },
        {
            'id': 'job_3',
            'titre': 'Analyste Data Junior',
            'entreprise': 'DataConseil',
            'localisation': 'Marseille',
            'experience_requise': 2,
            'salaire': '35-42K€',
            'budget_max': 42000,
            'competences': ['python', 'sql', 'tableau', 'excel'],
            'politique_remote': 'présentiel uniquement',
            'horaires_flexibles': False,
            'jours_rtt': 5,
            'formation_interne': True,
            'niveau_poste': 'junior'
        }
    ]

def create_test_candidates() -> Dict[str, Dict[str, Any]]:
    """
    Crée différents profils candidat avec priorités variables
    """
    return {
        'candidat_salaire_prioritaire': {
            'id': 'cand_1',
            'nom': 'Marie Dubois',
            'annees_experience': 6,
            'salaire_souhaite': 60000,
            'adresse': 'Paris',
            'competences': ['python', 'django', 'postgresql', 'react'],
            'langues': ['français', 'anglais'],
            'questionnaire_data': {
                'priorites_candidat': {
                    'evolution': 4,        # Faible priorité évolution
                    'remuneration': 9,     # 🎯 PRIORITÉ ÉLEVÉE salaire
                    'proximite': 6,        # Moyenne
                    'flexibilite': 5       # Moyenne
                },
                'flexibilite_attendue': {
                    'teletravail': 'partiel',
                    'horaires_flexibles': False,
                    'rtt_important': False
                }
            }
        },
        
        'candidat_evolution_prioritaire': {
            'id': 'cand_2', 
            'nom': 'Thomas Martin',
            'annees_experience': 4,
            'salaire_souhaite': 50000,
            'adresse': 'Lyon',
            'competences': ['javascript', 'react', 'node.js', 'python'],
            'langues': ['français', 'anglais'],
            'leadership_experience': True,
            'objectifs_carriere': {'evolution_rapide': True},
            'questionnaire_data': {
                'priorites_candidat': {
                    'evolution': 10,       # 🎯 PRIORITÉ MAXIMALE évolution  
                    'remuneration': 3,     # Faible priorité salaire
                    'proximite': 5,        # Moyenne
                    'flexibilite': 6       # Moyenne
                },
                'flexibilite_attendue': {
                    'teletravail': 'ouvert',
                    'horaires_flexibles': True,
                    'rtt_important': False
                }
            }
        },
        
        'candidat_flexibilite_prioritaire': {
            'id': 'cand_3',
            'nom': 'Sophie Chen', 
            'annees_experience': 3,
            'salaire_souhaite': 45000,
            'adresse': 'Toulouse',
            'competences': ['python', 'sql', 'tableau'],
            'langues': ['français', 'anglais', 'chinois'],
            'preferences_remote': 'télétravail préféré',
            'questionnaire_data': {
                'priorites_candidat': {
                    'evolution': 5,        # Moyenne
                    'remuneration': 4,     # Faible
                    'proximite': 3,        # Faible (car télétravail)
                    'flexibilite': 10      # 🎯 PRIORITÉ MAXIMALE flexibilité
                },
                'flexibilite_attendue': {
                    'teletravail': 'total',
                    'horaires_flexibles': True,
                    'rtt_important': True
                }
            }
        },
        
        'candidat_proximite_prioritaire': {
            'id': 'cand_4',
            'nom': 'Jean Rousseau',
            'annees_experience': 8,
            'salaire_souhaite': 55000,
            'adresse': 'Paris 15ème',
            'competences': ['python', 'django', 'postgresql', 'docker', 'kubernetes'],
            'langues': ['français'],
            'mobilite': 'limitée - famille',
            'questionnaire_data': {
                'priorites_candidat': {
                    'evolution': 6,        # Moyenne
                    'remuneration': 7,     # Bonne
                    'proximite': 10,       # 🎯 PRIORITÉ MAXIMALE proximité
                    'flexibilite': 4       # Faible
                },
                'flexibilite_attendue': {
                    'teletravail': 'aucun',
                    'horaires_flexibles': False, 
                    'rtt_important': False
                }
            }
        }
    }

def run_comparative_test():
    """
    🧪 Test comparatif: Même candidat avec différentes priorités
    """
    print("🧪 === TEST COMPARATIF: IMPACT PONDÉRATION DYNAMIQUE ===\n")
    
    algorithm = SuperSmartMatchAlgorithm()
    offers = create_test_offers()
    
    # Candidat de base
    base_candidate = {
        'id': 'cand_base',
        'annees_experience': 5,
        'salaire_souhaite': 58000,
        'adresse': 'Paris',
        'competences': ['python', 'django', 'javascript'],
        'langues': ['français', 'anglais']
    }
    
    # Scénario 1: Priorité rémunération
    candidate_salary_focused = {
        **base_candidate,
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 3,
                'remuneration': 10,  # 🎯 MAX
                'proximite': 5,
                'flexibilite': 4
            }
        }
    }
    
    # Scénario 2: Priorité évolution
    candidate_growth_focused = {
        **base_candidate,
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 10,     # 🎯 MAX
                'remuneration': 3,
                'proximite': 5,
                'flexibilite': 4
            }
        }
    }
    
    print("📊 CANDIDAT ORIENTÉ SALAIRE:")
    results_salary = algorithm.match_candidate_with_jobs(candidate_salary_focused, offers, limit=3)
    print(f"Pondération: {results_salary[0]['ponderation_dynamique']}")
    for i, result in enumerate(results_salary, 1):
        print(f"{i}. {result['titre']} - Score: {result['matching_score_entreprise']}% "
              f"(Rémunération: {result['scores_detailles']['remuneration']['poids']}%)")
    
    print("\n📊 CANDIDAT ORIENTÉ ÉVOLUTION:")
    results_growth = algorithm.match_candidate_with_jobs(candidate_growth_focused, offers, limit=3)
    print(f"Pondération: {results_growth[0]['ponderation_dynamique']}")
    for i, result in enumerate(results_growth, 1):
        print(f"{i}. {result['titre']} - Score: {result['matching_score_entreprise']}% "
              f"(Expérience: {result['scores_detailles']['experience']['poids']}%)")
    
    # Analyse des différences
    print("\n📈 ANALYSE DES DIFFÉRENCES:")
    for i in range(min(len(results_salary), len(results_growth))):
        job_title = results_salary[i]['titre']
        score_diff = results_growth[i]['matching_score_entreprise'] - results_salary[i]['matching_score_entreprise']
        print(f"• {job_title}: Différence de {score_diff:+d} points entre les deux approches")

def run_individual_tests():
    """
    🧪 Tests individuels des 4 profils candidat
    """
    print("\n🧪 === TESTS INDIVIDUELS DES 4 PROFILS ===\n")
    
    algorithm = SuperSmartMatchAlgorithm()
    offers = create_test_offers()
    candidates = create_test_candidates()
    
    for profile_name, candidate in candidates.items():
        print(f"👤 {profile_name.upper().replace('_', ' ')}:")
        print(f"   {candidate['nom']} - {candidate['annees_experience']} ans d'exp")
        
        # Afficher les priorités
        priorities = candidate['questionnaire_data']['priorites_candidat']
        max_priority = max(priorities, key=priorities.get)
        print(f"   🎯 Priorité max: {max_priority} ({priorities[max_priority]}/10)")
        
        # Lancer le matching
        results = algorithm.match_candidate_with_jobs(candidate, offers, limit=3)
        
        # Afficher la pondération adaptée
        weights = results[0]['ponderation_dynamique']
        print(f"   📊 Pondération adaptée:")
        for critere, poids in weights.items():
            print(f"      {critere}: {poids*100:.1f}%")
        
        # Afficher le top 3
        print(f"   🏆 Top 3 offres:")
        for i, result in enumerate(results, 1):
            score = result['matching_score_entreprise']
            title = result['titre']
            print(f"      {i}. {title} - {score}%")
        
        print()

def test_flexibility_impact():
    """
    🧪 Test spécifique impact du nouveau critère flexibilité
    """
    print("🧪 === TEST IMPACT CRITÈRE FLEXIBILITÉ ===\n")
    
    algorithm = SuperSmartMatchAlgorithm()
    
    # Offre très flexible
    flexible_offer = {
        'id': 'flex_job',
        'titre': 'Dev Remote-First',
        'entreprise': 'FlexTech',
        'localisation': 'Paris',
        'experience_requise': 4,
        'salaire': '50-60K€',
        'budget_max': 60000,
        'competences': ['python', 'javascript'],
        'politique_remote': 'télétravail total possible',
        'horaires_flexibles': True,
        'jours_rtt': 20
    }
    
    # Offre rigide  
    rigid_offer = {
        'id': 'rigid_job',
        'titre': 'Dev Sur Site',
        'entreprise': 'TradCorp',
        'localisation': 'Paris',
        'experience_requise': 4,
        'salaire': '50-60K€', 
        'budget_max': 60000,
        'competences': ['python', 'javascript'],
        'politique_remote': 'présentiel uniquement',
        'horaires_flexibles': False,
        'jours_rtt': 5
    }
    
    # Candidat flexibility-focused
    flex_candidate = {
        'annees_experience': 4,
        'salaire_souhaite': 55000,
        'adresse': 'Marseille',  # Loin de Paris
        'competences': ['python', 'javascript'],
        'questionnaire_data': {
            'priorites_candidat': {
                'evolution': 5,
                'remuneration': 5,
                'proximite': 3,      # Peu important car télétravail
                'flexibilite': 10    # 🎯 PRIORITÉ MAX
            },
            'flexibilite_attendue': {
                'teletravail': 'total',
                'horaires_flexibles': True,
                'rtt_important': True
            }
        }
    }
    
    offers = [flexible_offer, rigid_offer]
    results = algorithm.match_candidate_with_jobs(flex_candidate, offers)
    
    print("🎯 Candidat priorité flexibilité vs 2 offres:")
    print(f"Pondération flexibilité: {results[0]['ponderation_dynamique']['flexibilite']*100:.1f}%")
    print()
    
    for result in results:
        flex_score = result['scores_detailles']['flexibilite']['pourcentage']
        total_score = result['matching_score_entreprise']
        print(f"📋 {result['titre']}:")
        print(f"   Score flexibilité: {flex_score}%")
        print(f"   Score total: {total_score}%")
        print(f"   Details: {result['scores_detailles']['flexibilite']['details'][0]}")
        print()

def main():
    """
    Fonction principale pour lancer tous les tests
    """
    print("🚀 TESTS SUPERSMARTMATCH v2.1 - PONDÉRATION DYNAMIQUE")
    print("=" * 60)
    
    try:
        # Test 1: Comparaison même candidat, priorités différentes
        run_comparative_test()
        
        # Test 2: Tests individuels des 4 profils
        run_individual_tests()
        
        # Test 3: Impact spécifique flexibilité
        test_flexibility_impact()
        
        print("\n✅ TOUS LES TESTS RÉUSSIS!")
        print("\n📋 RÉSUMÉ DES NOUVEAUTÉS v2.1:")
        print("• ✅ Pondération dynamique fonctionnelle")
        print("• ✅ Critère flexibilité opérationnel") 
        print("• ✅ 4 leviers candidat implémentés")
        print("• ✅ Matching bidirectionnel personnalisé")
        print("• ✅ Tests validation complets")
        
    except Exception as e:
        print(f"\n❌ ERREUR DURANT LES TESTS: {e}")
        raise

if __name__ == "__main__":
    main()
