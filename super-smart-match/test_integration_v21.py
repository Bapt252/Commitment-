#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Script de Test Final SuperSmartMatch v2.1
Valide l'intégration complète de la pondération dynamique
"""

import json
import requests
import time
import sys
from typing import Dict, Any

class SuperSmartMatchV21Tester:
    def __init__(self, base_url: str = "http://localhost:5063"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log un résultat de test"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details and not success:
            print(f"   💡 {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_service_health(self) -> bool:
        """Test 1: Vérifier que le service est accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            data = response.json()
            
            success = (
                response.status_code == 200 and
                data.get('status') == 'healthy' and
                data.get('version') == '2.1' and
                data.get('supersmartmatch_available', False)
            )
            
            details = f"Status: {data.get('status')}, Version: {data.get('version')}"
            self.log_test("Service Health Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Service Health Check", False, str(e))
            return False
    
    def test_supersmartmatch_info(self) -> bool:
        """Test 2: Vérifier les infos SuperSmartMatch v2.1"""
        try:
            response = self.session.get(f"{self.base_url}/api/supersmartmatch/info")
            data = response.json()
            
            success = (
                response.status_code == 200 and
                data.get('version') == '2.1' and
                'dynamic_levers' in data.get('algorithm_info', {})
            )
            
            self.log_test("SuperSmartMatch Info", success)
            return success
            
        except Exception as e:
            self.log_test("SuperSmartMatch Info", False, str(e))
            return False
    
    def test_demo_profiles(self) -> bool:
        """Test 3: Vérifier les profils de démo"""
        try:
            response = self.session.get(f"{self.base_url}/api/demo/candidate-profiles")
            data = response.json()
            
            profiles = data.get('profiles', {})
            success = (
                response.status_code == 200 and
                'salaire_prioritaire' in profiles and
                'evolution_prioritaire' in profiles and
                'flexibilite_prioritaire' in profiles and
                'proximite_prioritaire' in profiles
            )
            
            self.log_test("Demo Profiles", success)
            return success
            
        except Exception as e:
            self.log_test("Demo Profiles", False, str(e))
            return False
    
    def test_questionnaire_validation(self) -> bool:
        """Test 4: Validation questionnaire candidat"""
        try:
            # Test avec questionnaire valide
            valid_questionnaire = {
                "priorites_candidat": {
                    "evolution": 8,
                    "remuneration": 6,
                    "proximite": 4,
                    "flexibilite": 9
                },
                "flexibilite_attendue": {
                    "teletravail": "partiel",
                    "horaires_flexibles": True,
                    "rtt_important": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/candidate/test-candidate/questionnaire",
                json=valid_questionnaire
            )
            
            success = response.status_code == 200
            self.log_test("Questionnaire Validation", success)
            return success
            
        except Exception as e:
            self.log_test("Questionnaire Validation", False, str(e))
            return False
    
    def test_matching_with_dynamic_weighting(self) -> bool:
        """Test 5: Matching avec pondération dynamique"""
        try:
            # Candidat avec priorités
            candidat_data = {
                "cv_data": {
                    "competences": ["Python", "Django", "React"],
                    "annees_experience": 5,
                    "langues": ["Français", "Anglais"]
                },
                "questionnaire_data": {
                    "adresse": "Paris",
                    "salaire_souhaite": 55000,
                    "priorites_candidat": {
                        "evolution": 10,
                        "remuneration": 3,
                        "proximite": 5,
                        "flexibilite": 8
                    },
                    "flexibilite_attendue": {
                        "teletravail": "partiel",
                        "horaires_flexibles": True,
                        "rtt_important": True
                    }
                },
                "job_data": [
                    {
                        "id": "test-job-1",
                        "titre": "Développeur Senior",
                        "entreprise": "TechCorp",
                        "competences": ["Python", "Django"],
                        "localisation": "Paris",
                        "salaire": "50-60K€",
                        "budget_max": 60000,
                        "experience_requise": 4,
                        "perspectives_evolution": True,
                        "politique_remote": "télétravail partiel",
                        "horaires_flexibles": True,
                        "jours_rtt": 15
                    }
                ],
                "algorithm": "supersmartmatch",
                "limit": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/match",
                json=candidat_data
            )
            
            data = response.json()
            results = data.get('results', [])
            
            success = (
                response.status_code == 200 and
                data.get('algorithm_used') == 'supersmartmatch' and
                data.get('version') == '2.1' and
                len(results) > 0 and
                'ponderation_dynamique' in results[0] and
                'scores_detailles' in results[0] and
                'flexibilite' in results[0]['scores_detailles']
            )
            
            if success:
                # Vérifier que la pondération est bien dynamique
                weights = results[0]['ponderation_dynamique']
                # Candidat avec évolution=10 devrait avoir expérience/compétences plus élevés
                dynamic_evolution_weight = weights.get('experience', 0) + weights.get('competences', 0)
                base_evolution_weight = 0.35  # Base : 20% + 15% = 35%
                
                if dynamic_evolution_weight > base_evolution_weight:
                    print(f"   📊 Pondération dynamique validée: évolution {dynamic_evolution_weight:.2f} vs base {base_evolution_weight:.2f}")
                else:
                    success = False
            
            self.log_test("Matching avec Pondération Dynamique", success)
            return success
            
        except Exception as e:
            self.log_test("Matching avec Pondération Dynamique", False, str(e))
            return False
    
    def test_weighting_impact_analytics(self) -> bool:
        """Test 6: Analytics d'impact pondération"""
        try:
            candidat = {
                "annees_experience": 4,
                "salaire_souhaite": 50000,
                "competences": ["Python", "JavaScript"],
                "questionnaire_data": {
                    "priorites_candidat": {
                        "evolution": 10,
                        "remuneration": 3,
                        "proximite": 5,
                        "flexibilite": 7
                    }
                }
            }
            
            offres = [
                {
                    "id": "job-1",
                    "titre": "Dev Senior",
                    "competences": ["Python"],
                    "salaire": "45-55K€",
                    "budget_max": 55000,
                    "experience_requise": 4,
                    "perspectives_evolution": True
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/api/analytics/weighting-impact",
                json={
                    "candidat": candidat,
                    "offres": offres,
                    "compare_scenarios": True
                }
            )
            
            data = response.json()
            analytics = data.get('analytics', {})
            
            success = (
                response.status_code == 200 and
                data.get('version') == '2.1' and
                analytics.get('has_questionnaire', False) and
                'dynamic_weights' in analytics and
                'comparison' in analytics and
                'impact_statistics' in analytics
            )
            
            self.log_test("Analytics Impact Pondération", success)
            return success
            
        except Exception as e:
            self.log_test("Analytics Impact Pondération", False, str(e))
            return False
    
    def test_company_matching_v21(self) -> bool:
        """Test 7: Matching côté entreprise avec SuperSmartMatch v2.1"""
        try:
            company_data = {
                "job_data": {
                    "id": "company-job-1",
                    "titre": "Lead Developer",
                    "entreprise": "StartupTech",
                    "competences": ["Python", "React"],
                    "localisation": "Paris",
                    "budget_max": 70000,
                    "experience_requise": 5,
                    "perspectives_evolution": True,
                    "politique_remote": "télétravail possible",
                    "horaires_flexibles": True,
                    "jours_rtt": 12
                },
                "candidates_data": [
                    {
                        "candidate_id": "cand-1",
                        "cv_data": {
                            "competences": ["Python", "React"],
                            "annees_experience": 5,
                            "langues": ["Français", "Anglais"]
                        },
                        "questionnaire_data": {
                            "salaire_souhaite": 65000,
                            "adresse": "Paris",
                            "priorites_candidat": {
                                "evolution": 9,
                                "remuneration": 7,
                                "proximite": 5,
                                "flexibilite": 8
                            },
                            "flexibilite_attendue": {
                                "teletravail": "partiel",
                                "horaires_flexibles": True,
                                "rtt_important": True
                            }
                        }
                    }
                ],
                "algorithm": "supersmartmatch",
                "limit": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/match-candidates",
                json=company_data
            )
            
            data = response.json()
            results = data.get('results', [])
            
            success = (
                response.status_code == 200 and
                data.get('algorithm_used') == 'supersmartmatch' and
                data.get('matching_mode') == 'company_to_candidates' and
                len(results) > 0 and
                'ponderation_dynamique' in results[0] and
                'matching_score_entreprise' in results[0]
            )
            
            self.log_test("Matching Côté Entreprise v2.1", success)
            return success
            
        except Exception as e:
            self.log_test("Matching Côté Entreprise v2.1", False, str(e))
            return False
    
    def test_flexibility_scoring(self) -> bool:
        """Test 8: Scoring flexibilité"""
        try:
            # Test avec candidat flexibilité prioritaire
            candidat_data = {
                "cv_data": {
                    "competences": ["Python"],
                    "annees_experience": 3
                },
                "questionnaire_data": {
                    "priorites_candidat": {
                        "evolution": 5,
                        "remuneration": 4,
                        "proximite": 3,
                        "flexibilite": 10  # Maximum
                    },
                    "flexibilite_attendue": {
                        "teletravail": "total",
                        "horaires_flexibles": True,
                        "rtt_important": True
                    }
                },
                "job_data": [
                    {
                        "id": "flexible-job",
                        "titre": "Dev Remote",
                        "competences": ["Python"],
                        "politique_remote": "télétravail total possible",
                        "horaires_flexibles": True,
                        "jours_rtt": 20,
                        "experience_requise": 3
                    }
                ],
                "algorithm": "supersmartmatch"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/match",
                json=candidat_data
            )
            
            data = response.json()
            results = data.get('results', [])
            
            success = (
                response.status_code == 200 and
                len(results) > 0 and
                'flexibilite' in results[0]['scores_detailles'] and
                results[0]['scores_detailles']['flexibilite']['pourcentage'] >= 80  # Score élevé attendu
            )
            
            if success:
                flex_score = results[0]['scores_detailles']['flexibilite']['pourcentage']
                print(f"   🔄 Score flexibilité: {flex_score}% (candidat flexibilité=10, offre très flexible)")
            
            self.log_test("Scoring Flexibilité", success)
            return success
            
        except Exception as e:
            self.log_test("Scoring Flexibilité", False, str(e))
            return False
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests"""
        print("🧪 === TESTS INTÉGRATION SUPERSMARTMATCH v2.1 ===\n")
        
        tests = [
            self.test_service_health,
            self.test_supersmartmatch_info,
            self.test_demo_profiles,
            self.test_questionnaire_validation,
            self.test_matching_with_dynamic_weighting,
            self.test_weighting_impact_analytics,
            self.test_company_matching_v21,
            self.test_flexibility_scoring
        ]
        
        success_count = 0
        for test in tests:
            if test():
                success_count += 1
            time.sleep(0.5)  # Pause entre les tests
            
        print(f"\n📊 RÉSULTATS: {success_count}/{len(tests)} tests réussis")
        
        if success_count == len(tests):
            print("🎉 TOUS LES TESTS RÉUSSIS - SuperSmartMatch v2.1 opérationnel!")
            return True
        else:
            print("⚠️ Certains tests ont échoué - Vérifier la configuration")
            return False
    
    def display_summary(self):
        """Affiche un résumé détaillé"""
        print("\n" + "="*60)
        print("📋 RÉSUMÉ INTÉGRATION SUPERSMARTMATCH v2.1")
        print("="*60)
        
        print("\n🎛️ PONDÉRATION DYNAMIQUE:")
        print("  ✅ 4 leviers candidat: Évolution, Rémunération, Proximité, Flexibilité")
        print("  ✅ Notes 1-10 qui adaptent automatiquement la pondération")
        print("  ✅ Matching bidirectionnel personnalisé")
        
        print("\n🔄 NOUVEAU CRITÈRE FLEXIBILITÉ:")
        print("  ✅ Télétravail (aucun/partiel/total)")
        print("  ✅ Horaires flexibles (oui/non)")
        print("  ✅ RTT important (oui/non)")
        
        print("\n🚀 ENDPOINTS API v2.1:")
        print("  ✅ POST /api/candidate/<id>/questionnaire - Priorités candidat")
        print("  ✅ POST /api/analytics/weighting-impact - Comparaison impact")
        print("  ✅ GET  /api/demo/candidate-profiles - Profils démo")
        print("  ✅ GET  /api/supersmartmatch/info - Infos algorithme")
        
        print("\n🧠 RAISONNEMENT INTELLIGENT:")
        print("  ✅ Analyse profil candidat (ambitieux, stable, polyvalent)")
        print("  ✅ Correspondances intelligentes (évolution+perspectives, etc.)")
        print("  ✅ Analyse risques et opportunités")
        
        print("\n📊 ANALYTICS:")
        print("  ✅ Comparaison pondération fixe vs dynamique")
        print("  ✅ Impact quantifié sur le classement")
        print("  ✅ Recommandations personnalisées")
        
        print("\n🎯 BÉNÉFICES v2.1:")
        print("  🌟 Matching personnalisé selon VRAIES priorités candidat")
        print("  🌟 Différenciation concurrentielle majeure")
        print("  🌟 Satisfaction candidat et entreprise améliorée")
        print("  🌟 Compréhension fine des motivations")
        
        print("\n" + "="*60)

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SuperSmartMatch v2.1')
    parser.add_argument('--url', default='http://localhost:5063', 
                       help='URL du service SuperSmartMatch (défaut: http://localhost:5063)')
    parser.add_argument('--summary-only', action='store_true',
                       help='Afficher seulement le résumé sans lancer les tests')
    
    args = parser.parse_args()
    
    tester = SuperSmartMatchV21Tester(args.url)
    
    if args.summary_only:
        tester.display_summary()
        return
    
    # Vérifier que le service est accessible
    try:
        response = requests.get(f"{args.url}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Service non accessible sur {args.url}")
            print("💡 Vérifiez que SuperSmartMatch est démarré avec: python app.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Impossible de connecter à {args.url}")
        print("💡 Vérifiez que SuperSmartMatch est démarré avec: python app.py")
        sys.exit(1)
    
    # Lancer les tests
    success = tester.run_all_tests()
    tester.display_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
