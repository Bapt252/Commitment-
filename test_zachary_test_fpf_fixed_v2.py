#!/usr/bin/env python3
"""
🚀 VALIDATION CRITIQUE : ZACHARY vs TEST FPF (Version corrigée)
Test si Zachary sur-score vraiment ou si c'est légitime
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
CV_PARSER_URL = "http://localhost:5051"
JOB_PARSER_URL = "http://localhost:5053"
ENHANCED_API_URL = "http://localhost:5055"

def test_services():
    """Vérification détaillée des services"""
    print("🔍 Vérification des services...")
    services = {
        "CV Parser V2": f"{CV_PARSER_URL}/health",
        "Job Parser V2": f"{JOB_PARSER_URL}/health", 
        "Enhanced API V2.1": f"{ENHANCED_API_URL}/health"
    }
    
    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.ok:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"   ❌ {name}: {e}")
            all_ok = False
    
    return all_ok

def parse_cv_with_retries(cv_path, max_retries=3):
    """Parse CV avec plusieurs tentatives et stratégies"""
    print(f"📄 Parsing du CV: {os.path.basename(cv_path)}")
    
    strategies = [
        {"force_refresh": "false", "timeout": 30},
        {"force_refresh": "true", "timeout": 60},
        {"force_refresh": "true", "timeout": 120}
    ]
    
    for attempt, strategy in enumerate(strategies, 1):
        print(f"   🧪 Tentative {attempt}/{len(strategies)} (force_refresh={strategy['force_refresh']})...")
        
        try:
            with open(cv_path, 'rb') as cv_file:
                files = {'file': (os.path.basename(cv_path), cv_file, 'application/pdf')}
                data = {'force_refresh': strategy['force_refresh']}
                
                response = requests.post(
                    f"{CV_PARSER_URL}/api/parse-cv/",
                    files=files,
                    data=data,
                    timeout=strategy['timeout']
                )
                
                print(f"      📡 Status: {response.status_code}")
                
                if response.ok:
                    result = response.json()
                    # Adaptation au format du CV Parser enriched
                    data = result.get('data', {})
                    personal_info = data.get('personal_info', {})
                    candidate_name = personal_info.get('name', 'Non détecté')
                    
                    print(f"      ✅ Succès! Candidat: {candidate_name}")
                    
                    # Convertir au format attendu par l'API de matching
                    converted_result = {
                        'candidate_name': candidate_name,
                        'personal_info': personal_info,
                        'professional_experience': data.get('professional_experience', []),
                        'technical_skills': data.get('technical_skills', []),
                        'soft_skills': data.get('soft_skills', []),
                        'skills': data.get('skills', []),
                        'education': data.get('education', []),
                        'certifications': data.get('certifications', []),
                        'languages': data.get('languages', []),
                        'experience_years': len(data.get('professional_experience', [])) * 2  # Estimation
                    }
                    
                    return converted_result
                else:
                    print(f"      ❌ Erreur: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"      📄 Détail: {error_detail}")
                    except:
                        print(f"      📄 Réponse: {response.text[:200]}...")
                        
        except requests.Timeout:
            print(f"      ⏱️ Timeout après {strategy['timeout']}s")
        except Exception as e:
            print(f"      ❌ Exception: {e}")
        
        if attempt < len(strategies):
            print("      ⏳ Attente avant nouvelle tentative...")
            time.sleep(2)
    
    return None

def parse_job_with_retries(job_path):
    """Parse Job avec gestion d'erreurs"""
    print(f"📋 Parsing de la fiche: {os.path.basename(job_path)}")
    
    try:
        with open(job_path, 'rb') as job_file:
            files = {'file': (os.path.basename(job_path), job_file)}
            data = {'force_refresh': 'true'}
            
            response = requests.post(
                f"{JOB_PARSER_URL}/api/parse-job",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.ok:
                result = response.json()
                job_title = result.get('job_title', 'Non détecté')
                print(f"   ✅ Succès! Poste: {job_title}")
                return result
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   📄 Détail: {error_detail}")
                except:
                    print(f"   📄 Réponse: {response.text[:200]}...")
                return None
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def calculate_matching(cv_data, job_data, job_name):
    """Calcul du matching avec l'API Enhanced"""
    try:
        payload = {
            "cv_data": cv_data,
            "job_data": job_data
        }
        
        response = requests.post(
            f"{ENHANCED_API_URL}/api/calculate-matching",
            json=payload,
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            return {
                "score": result.get('matching_score', 0),
                "confidence": result.get('confidence', 'unknown'),
                "recommendation": result.get('recommendation', 'Non disponible'),
                "details": result.get('details', {})
            }
        else:
            print(f"❌ Erreur matching: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   📄 Détail: {error_detail}")
            except:
                print(f"   📄 Réponse: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception matching: {e}")
        return None

def main():
    print("🚀 VALIDATION CRITIQUE : ZACHARY vs TEST FPF (Version corrigée)")
    print("=" * 70)
    print("🎯 Objectif: Tester si Zachary sur-score vraiment ou si c'est légitime")
    
    # 1. Vérification services
    if not test_services():
        print("❌ Certains services ne sont pas opérationnels!")
        print("💡 Vérifiez que tous les services sont démarrés")
        return
    
    print("✅ Tous les services sont opérationnels!")
    
    # 2. Recherche du CV Zachary
    desktop_path = Path.home() / "Desktop"
    cv_test_folder = desktop_path / "CV TEST"
    zachary_cv = cv_test_folder / "Zachary.pdf"
    
    print(f"📄 Recherche du CV de Zachary (dans {cv_test_folder})...")
    
    if not zachary_cv.exists():
        print(f"❌ CV Zachary non trouvé: {zachary_cv}")
        print("💡 Vérifiez le chemin et le nom du fichier")
        return
    
    print(f"✅ CV Zachary trouvé: {zachary_cv}")
    
    # 3. Recherche du dossier TEST FPF
    fpf_folder = desktop_path / "TEST FPF"
    print(f"📁 Recherche du dossier TEST FPF...")
    
    if not fpf_folder.exists():
        print(f"❌ Dossier TEST FPF non trouvé: {fpf_folder}")
        return
    
    print(f"✅ Dossier TEST FPF trouvé: {fpf_folder}")
    
    # 4. Recherche des fiches Word/PDF
    job_files = []
    for pattern in ["*.docx", "*.doc", "*.pdf"]:
        job_files.extend(fpf_folder.glob(pattern))
    
    if not job_files:
        print("❌ Aucune fiche de poste trouvée")
        return
    
    print(f"✅ {len(job_files)} fiches trouvées")
    for i, job_file in enumerate(job_files, 1):
        print(f"   {i}. {job_file.name}")
    
    # 5. Parsing du CV Zachary (avec retries)
    print("\n📊 Parsing du CV Zachary...")
    cv_data = parse_cv_with_retries(zachary_cv)
    
    if not cv_data:
        print("❌ Impossible de parser le CV de Zachary")
        print("\n🔧 SOLUTIONS À ESSAYER:")
        print("1. Redémarrer le CV Parser: cd cv-parser-v2 && python app.py")
        print("2. Vérifier les logs du CV Parser")
        print("3. Tester avec le script de diagnostic:")
        print("   python3 diagnostic_zachary_cv.py")
        print("4. Vérifier la configuration OpenAI dans .env")
        return
    
    print(f"✅ CV parsé! Candidat: {cv_data.get('candidate_name', 'Zachary')}")
    print(f"   💼 Expérience: {cv_data.get('experience_years', 0)} ans")
    print(f"   🎯 Compétences: {len(cv_data.get('technical_skills', []))} techniques")
    
    # 6. Test de matching pour chaque fiche
    print(f"\n🎯 Test de matching sur {len(job_files)} fiches...")
    results = []
    
    for i, job_file in enumerate(job_files, 1):
        print(f"\n--- Fiche {i}/{len(job_files)}: {job_file.name} ---")
        
        # Parse job
        job_data = parse_job_with_retries(job_file)
        if not job_data:
            print("   ⏭️ Fiche ignorée (parsing échoué)")
            continue
        
        # Calculate matching
        matching = calculate_matching(cv_data, job_data, job_file.name)
        if not matching:
            print("   ⏭️ Matching échoué")
            continue
        
        print(f"   📊 Score: {matching['score']}%")
        print(f"   🎯 Confiance: {matching['confidence']}")
        print(f"   💡 Recommandation: {matching['recommendation']}")
        
        results.append({
            "job_file": job_file.name,
            "job_title": job_data.get('job_title', 'Non détecté'),
            "score": matching['score'],
            "confidence": matching['confidence'],
            "recommendation": matching['recommendation']
        })
    
    # 7. Résumé final
    print(f"\n🏆 RÉSUMÉ FINAL - ZACHARY vs {len(results)} FICHES")
    print("=" * 60)
    
    if not results:
        print("❌ Aucun matching réussi")
        return
    
    # Tri par score décroissant
    results.sort(key=lambda x: x['score'], reverse=True)
    
    for i, result in enumerate(results, 1):
        emoji = "🚨" if result['score'] >= 70 else "⚠️" if result['score'] >= 50 else "✅"
        print(f"{emoji} #{i} - {result['score']}% - {result['job_title']}")
        print(f"      📁 {result['job_file']}")
        print(f"      💡 {result['recommendation']}")
    
    # Analyse critique
    high_scores = [r for r in results if r['score'] >= 70]
    medium_scores = [r for r in results if 50 <= r['score'] < 70]
    low_scores = [r for r in results if r['score'] < 50]
    
    print(f"\n📈 ANALYSE CRITIQUE:")
    print(f"   🚨 Scores élevés (≥70%): {len(high_scores)}")
    print(f"   ⚠️ Scores moyens (50-69%): {len(medium_scores)}")
    print(f"   ✅ Scores faibles (<50%): {len(low_scores)}")
    
    if high_scores:
        print(f"\n🔍 ANALYSE DES SCORES ÉLEVÉS:")
        for result in high_scores:
            print(f"   • {result['score']}% - {result['job_title']}")
            print(f"     👉 À vérifier: Cette correspondance est-elle légitime?")
    
    print(f"\n💡 CONCLUSION:")
    if high_scores:
        print("   🧐 Des scores élevés détectés - Analyse manuelle recommandée")
        print("   📊 Comparez avec la V2.0 pour voir les améliorations V2.1")
    else:
        print("   ✅ Aucun sur-scoring détecté - Système V2.1 Enhanced fonctionnel")
    
    # Sauvegarde des résultats
    timestamp = int(time.time())
    results_file = f"zachary_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "candidate": cv_data.get('candidate_name', 'Zachary'),
            "timestamp": timestamp,
            "results": results,
            "summary": {
                "total_tests": len(results),
                "high_scores": len(high_scores),
                "medium_scores": len(medium_scores),
                "low_scores": len(low_scores)
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés: {results_file}")

if __name__ == "__main__":
    main()
