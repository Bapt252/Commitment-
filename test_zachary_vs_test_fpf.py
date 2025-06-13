#!/usr/bin/env python3
"""
🏆 Test spécialisé : CV Zachary vs Fiches de Poste TEST FPF
Zachary ayant obtenu 94% sur les tests précédents, testons-le sur de nouvelles offres !
"""

import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime

def find_zachary_cv():
    """Localise le CV de Zachary"""
    cv_dir = Path("/Users/baptistecomas/Desktop/CV TEST/")
    
    # Rechercher Zachary
    for cv_file in cv_dir.glob("*.pdf"):
        if "zachary" in cv_file.name.lower():
            return cv_file
    
    return None

def find_test_fpf_folder():
    """Localise le dossier TEST FPF"""
    possible_paths = [
        Path("/Users/baptistecomas/Desktop/TEST FPF/"),
        Path("/Users/baptistecomas/Desktop/TEST FPF"),
        Path("/Users/baptistecomas/Downloads/TEST FPF/"),
        Path("/Users/baptistecomas/Documents/TEST FPF/"),
        Path("/Users/baptistecomas/TEST FPF/"),
        Path("/Users/baptistecomas/Commitment-/TEST FPF/")
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def parse_cv(cv_file):
    """Parser un CV via l'API"""
    try:
        with open(cv_file, 'rb') as f:
            files = {'file': (cv_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5051/api/parse-cv",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            print(f"   ❌ Erreur parsing CV: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception parsing CV: {e}")
        return None

def parse_job(job_file):
    """Parser un Job via l'API"""
    try:
        with open(job_file, 'rb') as f:
            files = {'file': (job_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            print(f"   ❌ Erreur parsing Job: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception parsing Job: {e}")
        return None

def calculate_matching(cv_data, job_data):
    """Calculer le matching via l'Enhanced API"""
    try:
        payload = {
            "cv_data": cv_data,
            "job_data": job_data
        }
        
        response = requests.post(
            "http://localhost:5055/api/calculate-matching",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'score': result.get('matching_score', 0),
                'confidence': result.get('confidence', 'low'),
                'recommendation': result.get('recommendation', ''),
                'details': result.get('details', {}),
                'processing_time': result.get('processing_time_ms', 0)
            }
        else:
            print(f"   ❌ Erreur matching: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception matching: {e}")
        return None

def display_detailed_analysis(matching_result, job_name):
    """Affiche l'analyse détaillée du matching"""
    if not matching_result:
        return
    
    details = matching_result.get('details', {})
    
    print(f"\\n📋 ANALYSE DÉTAILLÉE - {job_name[:40]}...")
    print("-" * 60)
    
    # Score global
    score = matching_result['score']
    confidence = matching_result['confidence']
    recommendation = matching_result['recommendation']
    
    if score >= 70:
        status_icon = "🟢"
        status_text = "EXCELLENT"
    elif score >= 40:
        status_icon = "🟡"
        status_text = "MOYEN"
    else:
        status_icon = "🔴"
        status_text = "FAIBLE"
    
    print(f"🎯 Score Global: {score}% {status_icon} {status_text}")
    print(f"🔍 Confiance: {confidence.upper()}")
    print(f"💡 Recommandation: {recommendation}")
    
    # Détails par composant
    if 'mission_analysis' in details:
        mission = details['mission_analysis']
        print(f"\\n📝 Missions (40%): {mission.get('score', 0):.0f}%")
        print(f"   {mission.get('explanation', 'N/A')}")
        if mission.get('matched_categories'):
            print(f"   ✅ Catégories correspondantes: {', '.join(mission['matched_categories'])}")
    
    if 'skills_analysis' in details:
        skills = details['skills_analysis']
        print(f"\\n🛠️ Compétences (30%): {skills.get('score', 0):.0f}%")
        print(f"   {skills.get('explanation', 'N/A')}")
        if skills.get('exact_matches'):
            print(f"   ✅ Compétences exactes: {', '.join(skills['exact_matches'][:5])}")
        if skills.get('partial_matches'):
            print(f"   🔹 Compétences partielles: {', '.join(skills['partial_matches'][:3])}")
    
    if 'experience_analysis' in details:
        exp = details['experience_analysis']
        print(f"\\n⏰ Expérience (15%): {exp.get('score', 0):.0f}%")
        print(f"   {exp.get('explanation', 'N/A')}")
    
    if 'quality_analysis' in details:
        quality = details['quality_analysis']
        print(f"\\n⭐ Qualité CV (15%): {quality.get('score', 0):.0f}%")
        print(f"   {quality.get('explanation', 'N/A')}")

def test_zachary_vs_test_fpf():
    """Test principal : Zachary vs TEST FPF"""
    print("🏆 TEST SPÉCIALISÉ : ZACHARY vs TEST FPF")
    print("=" * 60)
    print("🎯 Zachary a obtenu 94% sur les tests précédents")
    print("🔍 Testons-le maintenant sur de nouvelles fiches de poste !")
    print()
    
    # Localiser Zachary
    print("📄 Recherche du CV de Zachary...")
    zachary_cv = find_zachary_cv()
    
    if not zachary_cv:
        print("❌ CV de Zachary non trouvé dans /Users/baptistecomas/Desktop/CV TEST/")
        print("💡 Fichiers disponibles :")
        cv_dir = Path("/Users/baptistecomas/Desktop/CV TEST/")
        if cv_dir.exists():
            for f in list(cv_dir.glob("*.pdf"))[:5]:
                print(f"   - {f.name}")
        return False
    
    print(f"✅ CV Zachary trouvé: {zachary_cv.name}")
    
    # Localiser dossier TEST FPF
    print("\\n📁 Recherche du dossier TEST FPF...")
    fpf_dir = find_test_fpf_folder()
    
    if not fpf_dir:
        print("❌ Dossier TEST FPF non trouvé")
        print("💡 Chemins testés :")
        print("   - /Users/baptistecomas/Desktop/TEST FPF/")
        print("   - /Users/baptistecomas/Downloads/TEST FPF/")
        print("   - /Users/baptistecomas/Documents/TEST FPF/")
        print("\\n🔧 Veuillez indiquer le chemin exact du dossier TEST FPF")
        return False
    
    print(f"✅ Dossier TEST FPF trouvé: {fpf_dir}")
    
    # Lister les fiches de poste
    job_files = list(fpf_dir.glob("*.pdf"))
    if not job_files:
        print(f"❌ Aucun fichier PDF trouvé dans {fpf_dir}")
        return False
    
    print(f"💼 {len(job_files)} fiches de poste trouvées :")
    for job_file in job_files:
        print(f"   - {job_file.name}")
    
    # Parser le CV de Zachary
    print("\\n🔄 Parsing du CV de Zachary...")
    zachary_data = parse_cv(zachary_cv)
    
    if not zachary_data:
        print("❌ Impossible de parser le CV de Zachary")
        return False
    
    print("✅ CV de Zachary parsé avec succès")
    
    # Informations sur Zachary
    candidate_name = zachary_data.get('candidate_name', 'Zachary')
    experience_years = zachary_data.get('experience_years', 0)
    technical_skills = zachary_data.get('technical_skills', [])
    
    print(f"\\n👤 PROFIL DE {candidate_name.upper()}")
    print(f"   ⏰ Expérience: {experience_years} ans")
    print(f"   🛠️ Compétences techniques: {len(technical_skills)} compétences")
    if technical_skills:
        print(f"   📋 Principales: {', '.join(technical_skills[:8])}")
    
    # Tester contre chaque fiche de poste
    print(f"\\n🚀 DÉBUT DES TESTS CONTRE {len(job_files)} FICHES DE POSTE")
    print("=" * 60)
    
    results = []
    start_time = time.time()
    
    for i, job_file in enumerate(job_files, 1):
        print(f"\\n💼 Test {i}/{len(job_files)}: {job_file.name[:50]}...")
        
        # Parser la fiche de poste
        job_data = parse_job(job_file)
        if not job_data:
            print("   ❌ Échec parsing fiche de poste")
            continue
        
        # Calculer le matching
        matching_result = calculate_matching(zachary_data, job_data)
        if not matching_result:
            print("   ❌ Échec calcul matching")
            continue
        
        score = matching_result['score']
        confidence = matching_result['confidence']
        
        # Affichage résultat
        if score >= 70:
            status = "🟢 EXCELLENT"
        elif score >= 40:
            status = "🟡 MOYEN"
        else:
            status = "🔴 FAIBLE"
        
        print(f"   🎯 Résultat: {score}% {status} (Confiance: {confidence})")
        
        # Stocker le résultat
        results.append({
            'job_file': job_file.name,
            'score': score,
            'confidence': confidence,
            'recommendation': matching_result['recommendation'],
            'processing_time': matching_result['processing_time'],
            'details': matching_result['details']
        })
        
        # Afficher analyse détaillée pour les meilleurs scores
        if score >= 70:
            display_detailed_analysis(matching_result, job_file.name)
    
    # Résultats finaux
    total_time = time.time() - start_time
    
    print("\\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX - ZACHARY vs TEST FPF")
    print("=" * 60)
    
    if results:
        scores = [r['score'] for r in results]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        # Trouver le meilleur match
        best_match = max(results, key=lambda x: x['score'])
        
        print(f"🎯 Nombre de tests: {len(results)}")
        print(f"📈 Score moyen: {avg_score:.1f}%")
        print(f"⬆️ Score maximum: {max_score}%")
        print(f"⬇️ Score minimum: {min_score}%")
        print(f"⏱️ Temps total: {total_time:.1f} secondes")
        
        print(f"\\n🏆 MEILLEUR MATCH:")
        print(f"   📋 Poste: {best_match['job_file']}")
        print(f"   🎯 Score: {best_match['score']}%")
        print(f"   🔍 Confiance: {best_match['confidence']}")
        print(f"   💡 Recommandation: {best_match['recommendation']}")
        
        # Distribution des scores
        excellent = len([s for s in scores if s >= 70])
        moyen = len([s for s in scores if 40 <= s < 70])
        faible = len([s for s in scores if s < 40])
        
        print(f"\\n📊 DISTRIBUTION:")
        print(f"   🟢 Excellents (≥70%): {excellent}")
        print(f"   🟡 Moyens (40-69%): {moyen}")
        print(f"   🔴 Faibles (<40%): {faible}")
        
        # Sauvegarder rapport
        report = {
            'candidate': candidate_name,
            'cv_file': zachary_cv.name,
            'test_folder': str(fpf_dir),
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(results),
                'avg_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'processing_time': total_time
            },
            'detailed_results': results
        }
        
        report_file = f"zachary_vs_test_fpf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📋 Rapport détaillé sauvegardé: {report_file}")
        
        return True
    else:
        print("❌ Aucun résultat obtenu")
        return False

def main():
    """Fonction principale"""
    print("🚀 VALIDATION PRÉALABLE")
    print("Vérification que les services sont opérationnels...")
    
    # Vérifier les services
    services = [
        ("CV Parser V2", "http://localhost:5051/health"),
        ("Job Parser V2", "http://localhost:5053/health"),
        ("Enhanced API V2.1", "http://localhost:5055/health")
    ]
    
    all_ok = True
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: OK")
            else:
                print(f"❌ {service_name}: Erreur {response.status_code}")
                all_ok = False
        except:
            print(f"❌ {service_name}: Inaccessible")
            all_ok = False
    
    if not all_ok:
        print("\\n❌ Certains services ne sont pas opérationnels")
        print("💡 Assurez-vous que tous les services sont démarrés")
        return False
    
    print("\\n✅ Tous les services sont opérationnels!")
    print()
    
    # Lancer le test
    return test_zachary_vs_test_fpf()

if __name__ == "__main__":
    main()
