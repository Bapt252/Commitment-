#!/usr/bin/env python3
"""
🔄 Test Intégration Réelle - Parser Optimisé avec Système Existant
==================================================================

Test du parser CV optimisé intégré avec l'architecture Commitment- existante
"""

import json
import time
from pathlib import Path
from enhanced_cv_parser import EnhancedCVParser, enhanced_analyze_with_gpt

# Couleurs
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_enhanced_parser_integration():
    """Test du parser amélioré avec intégration réelle"""
    
    print(f"{Colors.BOLD}{Colors.BLUE}🔄 === TEST INTÉGRATION PARSER OPTIMISÉ ==={Colors.END}")
    print("Test avec parser amélioré + système Commitment- existant")
    print()
    
    # Initialiser le parser amélioré
    try:
        parser = EnhancedCVParser()
        print(f"{Colors.GREEN}✅ Parser amélioré initialisé{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur initialisation: {e}{Colors.END}")
        return
    
    # CVs de test avec contenu réaliste
    test_cvs = [
        {
            "name": "CV Tech Senior",
            "content": """
            Mohamed OUADHANE
            Développeur Full-Stack Senior
            mohamed.ouadhane@email.com
            +33 6 12 34 56 78
            Paris, France
            
            EXPÉRIENCE PROFESSIONNELLE:
            2022-2024: Lead Developer Full-Stack - TechStartup (2 ans)
            • Développement d'applications React/Node.js
            • Architecture microservices avec Docker
            • Gestion équipe de 4 développeurs
            
            2020-2022: Développeur Backend Senior - DigitalCorp (2 ans)  
            • APIs REST avec Django/FastAPI
            • Bases de données PostgreSQL, MongoDB
            • DevOps avec AWS, CI/CD
            
            2018-2020: Développeur Full-Stack - WebAgency (2 ans)
            • Développement sites e-commerce
            • React, Vue.js, Node.js
            • Intégration systèmes de paiement
            
            COMPÉTENCES TECHNIQUES:
            - Langages: JavaScript, TypeScript, Python, Java
            - Frontend: React, Vue.js, Angular, HTML5, CSS3
            - Backend: Node.js, Django, FastAPI, Spring Boot
            - Bases de données: PostgreSQL, MongoDB, Redis, MySQL
            - DevOps: Docker, Kubernetes, AWS, GCP, CI/CD
            - Outils: Git, Jira, Figma, Postman
            
            FORMATION:
            Master Informatique - Université Paris-Saclay (2018)
            Licence Informatique - Université Paris-Saclay (2016)
            
            LANGUES:
            - Français: Natif
            - Anglais: Courant (C1)
            - Arabe: Bilingue
            
            CERTIFICATIONS:
            - AWS Solutions Architect Associate (2023)
            - Certified Kubernetes Administrator (2022)
            """
        },
        {
            "name": "CV Data Science",
            "content": """
            AGBASSE Teddy
            Data Scientist & Machine Learning Engineer
            teddy.agbasse@gmail.com
            06 98 76 54 32
            Lyon, France
            
            EXPÉRIENCE:
            2021-2024: Senior Data Scientist - AI Company (3 ans)
            • Modèles ML pour recommandation produits
            • Pipeline MLOps avec Kubeflow
            • Analyse prédictive chiffre d'affaires
            
            2019-2021: Data Analyst - Analytics Firm (2 ans)
            • Dashboards BI avec Tableau
            • Analyses statistiques business
            • Modèles de scoring client
            
            COMPÉTENCES:
            - Python: pandas, numpy, scikit-learn, matplotlib
            - Machine Learning: TensorFlow, PyTorch, XGBoost
            - Big Data: Apache Spark, Hadoop, Kafka
            - Bases de données: SQL, NoSQL, ClickHouse
            - Cloud: AWS, GCP, Azure ML Studio
            - Visualisation: Tableau, Power BI, Plotly
            
            FORMATION:
            Master Data Science - École Centrale Lyon (2019)
            École d'Ingénieur spécialité Mathématiques Appliquées
            """
        },
        {
            "name": "CV Incomplet", 
            "content": """
            MARTIN Jean
            Consultant IT
            jean.martin@email.com
            
            EXPÉRIENCE:
            2019-2024: Consultant - IT Consulting
            
            COMPÉTENCES:
            - Java, Spring
            - Oracle, MySQL
            """
        }
    ]
    
    results = []
    total_start = time.time()
    
    print(f"{Colors.BLUE}🧪 Test de {len(test_cvs)} CVs avec parser optimisé...{Colors.END}")
    
    for i, test_cv in enumerate(test_cvs, 1):
        print(f"   {i}/{len(test_cvs)} - {test_cv['name']}", end=" ")
        
        start_time = time.time()
        
        try:
            # Utiliser le parser amélioré
            result = parser.analyze_with_gpt(test_cv["content"])
            processing_time = time.time() - start_time
            
            # Analyser le résultat
            success = result.get("success", False)
            quality_score = result.get("quality_score", 0)
            
            test_result = {
                "name": test_cv["name"],
                "success": success,
                "processing_time": processing_time,
                "quality_score": quality_score,
                "quality_level": result.get("quality_level", "unknown"),
                "missing_fields": result.get("missing_fields", []),
                "api_compatible": "data" in result,
                "data_fields": len(result.get("data", {}))
            }
            
            results.append(test_result)
            
            if success and quality_score >= 90:
                status = f"{Colors.GREEN}✅ {quality_score:.1f}%{Colors.END}"
            elif success and quality_score >= 70:
                status = f"{Colors.YELLOW}⚠️ {quality_score:.1f}%{Colors.END}"
            else:
                status = f"{Colors.RED}❌ {quality_score:.1f}%{Colors.END}"
            
            print(f"{status} ({processing_time:.3f}s)")
            
            # Afficher quelques données extraites
            if result.get("data"):
                data = result["data"]
                print(f"     📝 Nom: {data.get('prenom', '')} {data.get('nom', '')}")
                print(f"     💼 Poste: {data.get('poste_actuel', 'N/A')}")
                print(f"     📧 Email: {data.get('email', 'N/A')}")
                print(f"     🔧 Compétences: {len(data.get('competences_techniques', []))} identifiées")
                print(f"     📚 Formation: {data.get('niveau_formation', 'N/A')} {data.get('domaine_formation', '')}")
                
        except Exception as e:
            test_result = {
                "name": test_cv["name"],
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            results.append(test_result)
            print(f"{Colors.RED}❌ ERREUR: {str(e)[:50]}...{Colors.END}")
    
    total_time = time.time() - total_start
    
    # Analyser les résultats
    print(f"\n{Colors.BOLD}📊 === ANALYSE INTÉGRATION RÉELLE ==={Colors.END}")
    
    successful_tests = [r for r in results if r["success"]]
    
    if successful_tests:
        qualities = [r["quality_score"] for r in successful_tests]
        avg_quality = sum(qualities) / len(qualities)
        
        excellent_count = sum(1 for q in qualities if q >= 95)
        good_count = sum(1 for q in qualities if q >= 80)
        success_rate = (good_count / len(results)) * 100
        
        print(f"⏱️ Temps total: {total_time:.2f}s")
        print(f"📄 CVs testés: {len(results)}")
        print(f"✅ Parsing réussi: {len(successful_tests)}")
        print(f"📊 Qualité moyenne: {avg_quality:.1f}%")
        print(f"🌟 Excellente (>95%): {excellent_count}")
        print(f"✅ Bonne (>80%): {good_count}")
        print(f"🎯 Taux de succès: {success_rate:.1f}%")
        
        # Vérifier la compatibilité API
        api_compatible = all(r.get("api_compatible", False) for r in successful_tests)
        print(f"🔗 Compatible API existante: {'✅' if api_compatible else '❌'}")
        
        # Comparaison avec baseline
        baseline = 54.5  # Ton taux actuel
        improvement = success_rate - baseline
        
        print(f"\n📈 COMPARAISON vs BASELINE:")
        print(f"   Baseline actuelle: {baseline}%")
        print(f"   Parser optimisé: {success_rate:.1f}%")
        print(f"   Amélioration: {'+' if improvement > 0 else ''}{improvement:.1f} points")
        
        if success_rate >= 90:
            print(f"\n{Colors.GREEN}🎉 OBJECTIF >90% ATTEINT! ({success_rate:.1f}%){Colors.END}")
            print(f"{Colors.GREEN}🚀 Prêt pour intégration en production{Colors.END}")
        elif success_rate > baseline:
            print(f"\n{Colors.YELLOW}👍 AMÉLIORATION SIGNIFICATIVE (+{improvement:.1f}%){Colors.END}")
            print(f"{Colors.YELLOW}📈 Continuer l'optimisation pour atteindre 90%{Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️ Besoin d'optimisation supplémentaire{Colors.END}")
        
        # Détails des problèmes
        problematic_cvs = [r for r in results if not r["success"] or r.get("quality_score", 0) < 80]
        if problematic_cvs:
            print(f"\n{Colors.BOLD}🔍 === CVs À AMÉLIORER ==={Colors.END}")
            for cv in problematic_cvs:
                print(f"❌ {cv['name']}: {cv.get('quality_score', 0):.1f}%")
                if cv.get('missing_fields'):
                    print(f"   Champs manquants: {', '.join(cv['missing_fields'][:3])}")
                if cv.get('error'):
                    print(f"   Erreur: {cv['error'][:50]}...")
    
    # Instructions d'intégration
    print(f"\n{Colors.BOLD}🔧 === INTÉGRATION PRODUCTION ==={Colors.END}")
    print("Pour intégrer dans ton système Commitment- :")
    print("1. Backup du parser actuel")
    print("2. Dans gpt_parser.py, remplacer :")
    print("   from parse_fdp_gpt import analyze_with_gpt")
    print("   par:")
    print("   from enhanced_cv_parser import enhanced_analyze_with_gpt as analyze_with_gpt")
    print("3. Redémarrer le service")
    print("4. Tester avec ton frontend existant")
    print("5. Mesurer l'amélioration sur tes 69 CVs réels")

if __name__ == "__main__":
    test_enhanced_parser_integration()
