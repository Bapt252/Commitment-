#!/usr/bin/env python3
"""
🎯 Test SuperSmartMatch V2 avec données réelles de CV et questionnaires
Scénarios de test complets après correction des endpoints
"""

import requests
import json
import time
from datetime import datetime

def test_data_scientist_profile():
    """Test avec profil Data Scientist senior"""
    
    print("\n🧪 TEST 1: Profil Data Scientist Senior")
    print("-" * 50)
    
    payload = {
        "candidate": {
            "name": "Marie Dubois",
            "email": "marie.dubois@email.com",
            "technical_skills": [
                "Python", "R", "Machine Learning", "Deep Learning", 
                "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
                "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
                "Apache Spark", "Hadoop", "Tableau", "Power BI"
            ],
            "soft_skills": [
                "Communication", "Leadership", "Problem Solving", 
                "Critical Thinking", "Team Collaboration"
            ],
            "experience_years": 7,
            "education": "PhD Computer Science - Sorbonne",
            "languages": ["French", "English", "Spanish"],
            "certifications": [
                "AWS Certified Data Analytics",
                "Google Cloud Professional Data Engineer",
                "Certified Analytics Professional (CAP)"
            ],
            "experiences": [
                {
                    "title": "Senior Data Scientist",
                    "company": "Airbus",
                    "duration_months": 36,
                    "technologies": ["Python", "TensorFlow", "AWS", "Spark"],
                    "achievements": [
                        "Led ML team of 8 engineers",
                        "Reduced prediction error by 35%",
                        "Deployed 12 ML models in production"
                    ]
                },
                {
                    "title": "Data Scientist",
                    "company": "BNP Paribas",
                    "duration_months": 24,
                    "technologies": ["R", "Python", "SQL", "Tableau"],
                    "achievements": [
                        "Built fraud detection system",
                        "Improved model accuracy by 28%"
                    ]
                }
            ]
        },
        "candidate_questionnaire": {
            "adresse": "Paris 15ème",
            "code_postal": "75015",
            "salaire_actuel": 85000,
            "salaire_souhaite": 100000,
            "types_contrat": ["CDI"],
            "disponibilite": "1 mois",
            "mode_transport": "metro",
            "mobilite_geographique": "Paris et banlieue",
            "priorite": "competences",
            "objectif": "expertise",
            "secteur_preference": "tech",
            "work_style": "analytical",
            "culture_preferences": "data_driven",
            "remote_preference": "hybrid",
            "team_size_preference": "medium",
            "management_interest": True,
            "formation_continue": True,
            "innovation_appetite": "high",
            "risk_tolerance": "medium",
            "communication_style": "direct",
            "motivations": ["innovation", "impact", "leadership"],
            "deal_breakers": ["low_tech", "micromanagement"]
        },
        "offers": [
            {
                "id": "ai_startup_lead_001",
                "title": "Lead Data Scientist",
                "company": "InnovAI",
                "location": "Paris 9ème",
                "contract_type": "CDI",
                "salary_min": 95000,
                "salary_max": 115000,
                "required_skills": [
                    "Python", "Machine Learning", "Deep Learning",
                    "TensorFlow", "Leadership", "Team Management"
                ],
                "nice_to_have": ["PyTorch", "MLOps", "AWS"],
                "experience_required": 5,
                "remote_policy": "hybrid",
                "team_size": 15,
                "sector": "AI/ML",
                "culture": "innovative",
                "description": "Lead our ML team in developing cutting-edge AI solutions"
            },
            {
                "id": "bank_senior_ds_002",
                "title": "Senior Data Scientist - Risk",
                "company": "Société Générale",
                "location": "La Défense",
                "contract_type": "CDI",
                "salary_min": 85000,
                "salary_max": 105000,
                "required_skills": [
                    "Python", "R", "Machine Learning", "Risk Modeling",
                    "SQL", "Regulatory Knowledge"
                ],
                "nice_to_have": ["SAS", "Credit Risk", "Basel III"],
                "experience_required": 6,
                "remote_policy": "partial",
                "team_size": 8,
                "sector": "finance",
                "culture": "structured",
                "description": "Build risk models for credit and market risk"
            }
        ],
        "algorithm": "auto"
    }
    
    return test_matching_request("Data Scientist Senior", payload)

def test_junior_developer_profile():
    """Test avec profil développeur junior"""
    
    print("\n🧪 TEST 2: Profil Développeur Junior Full-Stack")
    print("-" * 50)
    
    payload = {
        "candidate": {
            "name": "Thomas Martin",
            "email": "thomas.martin@email.com",
            "technical_skills": [
                "JavaScript", "React", "Node.js", "Express.js",
                "HTML5", "CSS3", "MongoDB", "Git", "Docker"
            ],
            "soft_skills": [
                "Curiosity", "Fast Learning", "Team Work", "Communication"
            ],
            "experience_years": 2,
            "education": "Master Informatique - INSA Lyon",
            "languages": ["French", "English"],
            "experiences": [
                {
                    "title": "Développeur Full-Stack Junior",
                    "company": "WebStart",
                    "duration_months": 18,
                    "technologies": ["React", "Node.js", "MongoDB"],
                    "achievements": [
                        "Developed 3 complete web applications",
                        "Improved loading speed by 40%"
                    ]
                },
                {
                    "title": "Stage Développeur",
                    "company": "Digital Agency",
                    "duration_months": 6,
                    "technologies": ["JavaScript", "React", "CSS"],
                    "achievements": ["Built responsive e-commerce site"]
                }
            ]
        },
        "candidate_questionnaire": {
            "adresse": "Lyon 3ème",
            "code_postal": "69003",
            "salaire_actuel": 32000,
            "salaire_souhaite": 38000,
            "types_contrat": ["CDI", "CDD"],
            "disponibilite": "immédiate",
            "mode_transport": "velo",
            "mobilite_geographique": "Lyon métropole",
            "priorite": "experience",
            "objectif": "apprentissage",
            "secteur_preference": "web",
            "work_style": "collaborative",
            "culture_preferences": "startup",
            "remote_preference": "office",
            "team_size_preference": "small",
            "management_interest": False,
            "formation_continue": True,
            "innovation_appetite": "high",
            "risk_tolerance": "high",
            "communication_style": "friendly",
            "motivations": ["learning", "creativity", "team"],
            "deal_breakers": ["outdated_tech", "isolation"]
        },
        "offers": [
            {
                "id": "startup_fullstack_001",
                "title": "Développeur Full-Stack",
                "company": "TechStartup",
                "location": "Lyon Part-Dieu",
                "contract_type": "CDI",
                "salary_min": 35000,
                "salary_max": 42000,
                "required_skills": [
                    "JavaScript", "React", "Node.js", "MongoDB"
                ],
                "nice_to_have": ["TypeScript", "Docker", "AWS"],
                "experience_required": 1,
                "remote_policy": "flexible",
                "team_size": 6,
                "sector": "fintech",
                "culture": "startup",
                "description": "Join our agile team building next-gen fintech solutions"
            }
        ],
        "algorithm": "auto"
    }
    
    return test_matching_request("Développeur Junior", payload)

def test_experienced_manager_profile():
    """Test avec profil manager expérimenté"""
    
    print("\n🧪 TEST 3: Profil Engineering Manager Expérimenté")
    print("-" * 50)
    
    payload = {
        "candidate": {
            "name": "Sophie Leroy",
            "email": "sophie.leroy@email.com",
            "technical_skills": [
                "Java", "Spring Boot", "Microservices", "Kubernetes",
                "AWS", "DevOps", "Jenkins", "Terraform", "Monitoring"
            ],
            "soft_skills": [
                "Leadership", "Strategic Thinking", "Team Building",
                "Conflict Resolution", "Budget Management", "Stakeholder Management"
            ],
            "experience_years": 12,
            "education": "MBA + Master Informatique",
            "languages": ["French", "English", "German"],
            "certifications": [
                "PMP Certified", "AWS Solutions Architect",
                "Scrum Master", "ITIL Foundation"
            ],
            "experiences": [
                {
                    "title": "Engineering Manager",
                    "company": "Orange",
                    "duration_months": 48,
                    "technologies": ["Java", "Spring", "AWS", "Kubernetes"],
                    "achievements": [
                        "Managed 25-person engineering team",
                        "Delivered 15 major projects on time",
                        "Reduced infrastructure costs by 30%",
                        "Implemented CI/CD across all teams"
                    ]
                },
                {
                    "title": "Tech Lead",
                    "company": "Capgemini",
                    "duration_months": 36,
                    "technologies": ["Java", "Spring", "Docker", "Jenkins"],
                    "achievements": [
                        "Led technical architecture decisions",
                        "Mentored 8 junior developers"
                    ]
                }
            ]
        },
        "candidate_questionnaire": {
            "adresse": "Paris 8ème",
            "code_postal": "75008",
            "salaire_actuel": 110000,
            "salaire_souhaite": 130000,
            "types_contrat": ["CDI"],
            "disponibilite": "3 mois",
            "mode_transport": "metro",
            "mobilite_geographique": "Paris et banlieue",
            "priorite": "management",
            "objectif": "leadership",
            "secteur_preference": "enterprise",
            "work_style": "strategic",
            "culture_preferences": "structured",
            "remote_preference": "hybrid",
            "team_size_preference": "large",
            "management_interest": True,
            "formation_continue": True,
            "innovation_appetite": "medium",
            "risk_tolerance": "low",
            "communication_style": "diplomatic",
            "motivations": ["leadership", "impact", "strategy"],
            "deal_breakers": ["micromanagement", "lack_resources"]
        },
        "offers": [
            {
                "id": "corp_eng_manager_001",
                "title": "Senior Engineering Manager",
                "company": "Société Générale",
                "location": "La Défense",
                "contract_type": "CDI",
                "salary_min": 120000,
                "salary_max": 150000,
                "required_skills": [
                    "Team Leadership", "Java", "Spring Boot",
                    "Microservices", "AWS", "Project Management"
                ],
                "nice_to_have": ["Financial Services", "Regulatory"],
                "experience_required": 10,
                "remote_policy": "hybrid",
                "team_size": 30,
                "sector": "finance",
                "culture": "corporate",
                "description": "Lead our digital transformation initiatives"
            }
        ],
        "algorithm": "auto"
    }
    
    return test_matching_request("Engineering Manager", payload)

def test_specialized_security_profile():
    """Test avec profil cybersécurité spécialisé"""
    
    print("\n🧪 TEST 4: Profil Expert Cybersécurité")
    print("-" * 50)
    
    payload = {
        "candidate": {
            "name": "Alex Moreau",
            "email": "alex.moreau@email.com",
            "technical_skills": [
                "Penetration Testing", "Vulnerability Assessment",
                "SIEM", "SOC", "Incident Response", "Forensics",
                "Python", "PowerShell", "Linux", "Windows Security",
                "CISSP", "CEH", "OSCP", "Nessus", "Burp Suite"
            ],
            "soft_skills": [
                "Analytical Thinking", "Attention to Detail",
                "Stress Management", "Communication", "Continuous Learning"
            ],
            "experience_years": 8,
            "education": "Master Cybersécurité - ESIEA",
            "languages": ["French", "English"],
            "certifications": [
                "CISSP", "CEH", "OSCP", "GCIH", "SANS GIAC"
            ],
            "experiences": [
                {
                    "title": "Security Consultant",
                    "company": "Thales",
                    "duration_months": 30,
                    "technologies": ["SIEM", "Penetration Testing", "Python"],
                    "achievements": [
                        "Conducted 50+ security assessments",
                        "Reduced security incidents by 60%",
                        "Built automated threat detection"
                    ]
                }
            ]
        },
        "candidate_questionnaire": {
            "adresse": "Toulouse",
            "code_postal": "31000",
            "salaire_actuel": 65000,
            "salaire_souhaite": 75000,
            "types_contrat": ["CDI", "Freelance"],
            "disponibilite": "2 mois",
            "mode_transport": "voiture",
            "mobilite_geographique": "France entière",
            "priorite": "competences",
            "objectif": "expertise",
            "secteur_preference": "security",
            "work_style": "independent",
            "culture_preferences": "security_focused",
            "remote_preference": "remote",
            "team_size_preference": "small",
            "management_interest": False,
            "formation_continue": True,
            "innovation_appetite": "high",
            "risk_tolerance": "low",
            "communication_style": "technical",
            "motivations": ["security", "challenge", "continuous_learning"],
            "deal_breakers": ["poor_security_culture", "outdated_tools"]
        },
        "offers": [
            {
                "id": "cyber_specialist_001",
                "title": "Senior Cybersecurity Specialist",
                "company": "CyberDefense Corp",
                "location": "Remote/Paris",
                "contract_type": "CDI",
                "salary_min": 70000,
                "salary_max": 85000,
                "required_skills": [
                    "Penetration Testing", "SIEM", "Incident Response",
                    "Python", "Security Assessment"
                ],
                "nice_to_have": ["CISSP", "Cloud Security", "DevSecOps"],
                "experience_required": 6,
                "remote_policy": "full_remote",
                "team_size": 5,
                "sector": "cybersecurity",
                "culture": "security_first",
                "description": "Protect critical infrastructure from advanced threats"
            }
        ],
        "algorithm": "auto"
    }
    
    return test_matching_request("Expert Cybersécurité", payload)

def test_matching_request(profile_name, payload):
    """Effectue le test de matching et analyse les résultats"""
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:5070/api/v2/match",
            json=payload,
            timeout=20,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            # Analyse des résultats
            algorithm_used = result.get('algorithm_used', 'unknown')
            fallback = result.get('metadata', {}).get('fallback', True)
            execution_time = result.get('execution_time_ms', response_time)
            matches = result.get('matches', [])
            
            print(f"✅ {profile_name} - Test réussi")
            print(f"   🎯 Algorithme utilisé: {algorithm_used}")
            print(f"   ⚡ Temps d'exécution: {execution_time:.0f}ms")
            print(f"   🔄 Mode fallback: {fallback}")
            print(f"   📊 Nombre de matches: {len(matches)}")
            
            if matches:
                best_match = matches[0]
                score = best_match.get('overall_score', best_match.get('score', 'N/A'))
                offer_id = best_match.get('offer_id', best_match.get('id', 'N/A'))
                
                print(f"   🏆 Meilleur match: {offer_id} (Score: {score})")
                
                # Détails du scoring si disponible
                if 'detailed_scores' in best_match:
                    details = best_match['detailed_scores']
                    print(f"   📈 Détails scoring:")
                    for key, value in details.items():
                        print(f"      - {key}: {value}")
            
            # Indicateur de succès
            success = not fallback and algorithm_used != "fallback_basic"
            if success:
                print(f"   🎉 SUCCÈS: {algorithm_used} utilisé avec succès!")
            else:
                print(f"   ⚠️  Attention: Mode fallback activé")
                
            return success, result
            
        else:
            print(f"❌ {profile_name} - Erreur {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"❌ {profile_name} - Exception: {e}")
        return False, None

def run_comprehensive_tests():
    """Lance tous les tests avec données réelles"""
    
    print("🎯 TESTS SUPERSMARTMATCH V2 - DONNÉES RÉELLES")
    print("=" * 65)
    print(f"🕐 Démarrage à {datetime.now().strftime('%H:%M:%S')}")
    
    tests = [
        test_data_scientist_profile,
        test_junior_developer_profile,
        test_experienced_manager_profile,
        test_specialized_security_profile
    ]
    
    results = []
    total_start = time.time()
    
    for test_func in tests:
        success, result = test_func()
        results.append((test_func.__name__, success, result))
        time.sleep(1)  # Pause entre tests
    
    total_time = (time.time() - total_start) * 1000
    
    # Résumé final
    print("\n" + "=" * 65)
    print("📊 RÉSUMÉ DES TESTS AVEC DONNÉES RÉELLES")
    print("=" * 65)
    
    successful_tests = sum(1 for _, success, _ in results if success)
    total_tests = len(results)
    
    print(f"🏆 Tests réussis: {successful_tests}/{total_tests}")
    print(f"⏱️  Temps total: {total_time:.0f}ms")
    
    for test_name, success, result in results:
        status = "✅" if success else "❌"
        test_display = test_name.replace("test_", "").replace("_profile", "").replace("_", " ").title()
        print(f"{status} {test_display}")
        
        if success and result:
            algorithm = result.get('algorithm_used', 'unknown')
            print(f"    → Algorithme: {algorithm}")
    
    if successful_tests == total_tests:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ SuperSmartMatch V2 fonctionne parfaitement avec données réelles")
        print("✅ Les endpoints sont correctement configurés")
        print("✅ Communication avec Nexten Matcher opérationnelle")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} test(s) en échec")
        print("🔧 Vérifier la configuration et les logs des services")
    
    print(f"\n🕐 Terminé à {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_comprehensive_tests()
