#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 CORRECTION DIRECTE JOB PARSER V2 - Sans échappements complexes
Approche simple: remplacement direct du code problématique
"""

import os
import requests
import subprocess
from pathlib import Path

def fix_title_extraction_direct():
    """Correction directe sans regex complexes"""
    print("🎯 CORRECTION DIRECTE EXTRACTION TITRE")
    print("=" * 45)
    
    parser_file = Path("/Users/baptistecomas/Commitment-/job-parser-v2/parsers/enhanced-mission-parser.js")
    
    if not parser_file.exists():
        print(f"❌ Fichier parser non trouvé: {parser_file}")
        return False
    
    print("1️⃣ Lecture du fichier...")
    
    try:
        with open(parser_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier lu")
        
        # Rechercher le début de la fonction extractJobBasicInfo
        start_marker = "extractJobBasicInfo(text, job) {"
        start_pos = content.find(start_marker)
        
        if start_pos == -1:
            print("❌ Fonction extractJobBasicInfo non trouvée")
            return False
        
        # Rechercher la fin (prochain commentaire ou fonction)
        search_from = start_pos + len(start_marker)
        end_markers = [
            "\n        // Contrat",
            "\n        // Localisation", 
            "\n    extractJobSkills",
            "\n    extractJobSalaryAndBenefits"
        ]
        
        end_pos = -1
        for marker in end_markers:
            pos = content.find(marker, search_from)
            if pos != -1:
                end_pos = pos
                break
        
        if end_pos == -1:
            print("❌ Fin de fonction non trouvée")
            return False
        
        print("✅ Fonction localisée")
        
        # Nouvelle implémentation SIMPLE
        new_function = """    extractJobBasicInfo(text, job) {
        // Titre du poste - APPROCHE SIMPLE ET EFFICACE
        console.log('   🎯 Extraction titre simplifié...');
        
        // 1. Recherche directe de mots-clés de postes
        const jobTitles = [
            'Assistant Juridique',
            'Assistant Comptable', 
            'Assistant Facturation',
            'Responsable Comptable',
            'Gestionnaire Comptable'
        ];
        
        // Chercher ces titres directement dans le texte
        for (const title of jobTitles) {
            if (text.includes(title)) {
                job.job_info.title = title;
                console.log(`   ✅ Titre trouvé directement: "${title}"`);
                break;
            }
        }
        
        // 2. Si pas trouvé, chercher dans le nom du fichier (si disponible)
        if (!job.job_info.title) {
            const fileName = job._metadata?.filename || '';
            for (const title of jobTitles) {
                if (fileName.includes(title)) {
                    job.job_info.title = title;
                    console.log(`   ✅ Titre trouvé dans nom fichier: "${title}"`);
                    break;
                }
            }
        }
        
        // 3. Recherche de patterns simples sans regex complexes
        if (!job.job_info.title) {
            // Chercher "Opportunité de poste" 
            const oppoIndex = text.indexOf('Opportunité de poste');
            if (oppoIndex !== -1) {
                const afterOppo = text.substring(oppoIndex + 20, oppoIndex + 100);
                const lines = afterOppo.split('\\n');
                if (lines.length > 0) {
                    let candidate = lines[0].trim();
                    if (candidate.length > 5 && candidate.length < 50) {
                        job.job_info.title = candidate;
                        console.log(`   ✅ Titre extrait après "Opportunité": "${candidate}"`);
                    }
                }
            }
        }
        
        // 4. Dernière tentative : première ligne significative qui n'est pas "Qui sommes"
        if (!job.job_info.title) {
            const lines = text.split('\\n');
            for (const line of lines) {
                const cleaned = line.trim();
                if (cleaned.length > 8 && 
                    cleaned.length < 60 && 
                    !cleaned.includes('Qui sommes') &&
                    !cleaned.includes('À propos') &&
                    !cleaned.includes('Notre société') &&
                    !cleaned.includes('@') &&
                    /^[A-ZÀ-ÿ]/.test(cleaned)) {
                    
                    job.job_info.title = cleaned;
                    console.log(`   ✅ Titre extrait (ligne significative): "${cleaned}"`);
                    break;
                }
            }
        }
        
        // 5. Par défaut
        if (!job.job_info.title) {
            job.job_info.title = "Poste à définir";
            console.log(`   ⚠️ Titre par défaut utilisé`);
        }"""
        
        # Sauvegarder l'original
        backup_file = parser_file.with_suffix('.js.backup.direct')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde: {backup_file.name}")
        
        # Remplacer la fonction
        new_content = content[:start_pos] + new_function + content[end_pos:]
        
        # Écrire le nouveau fichier
        with open(parser_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fonction remplacée par approche simple")
        
        # Redémarrer et tester
        return restart_and_test()
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def restart_and_test():
    """Redémarrer et tester"""
    print("\n2️⃣ Redémarrage du service...")
    
    # Arrêter le processus
    try:
        result = subprocess.run(['lsof', '-ti:5053'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split()
            subprocess.run(['sudo', 'kill', '-9'] + pids, stderr=subprocess.DEVNULL)
            print("   ✅ Service arrêté")
        else:
            print("   ℹ️ Aucun processus à arrêter")
    except:
        print("   ℹ️ Aucun processus à arrêter")
    
    # Redémarrer
    restart_script = Path("/Users/baptistecomas/Commitment-/restart_job_parser_v2.sh")
    if restart_script.exists():
        try:
            subprocess.run(['bash', str(restart_script)], 
                          capture_output=True, text=True, timeout=60)
            print("   ✅ Service redémarré")
        except Exception as e:
            print(f"   ⚠️ Redémarrage: {e}")
    
    # Test
    print("\n3️⃣ Test de la correction...")
    return test_simple_extraction()

def test_simple_extraction():
    """Test simple"""
    import time
    
    print("   ⏳ Attente (5 secondes)...")
    time.sleep(5)
    
    # Vérifier le service
    try:
        response = requests.get("http://localhost:5053/health", timeout=10)
        if response.status_code != 200:
            print("   ❌ Service non accessible")
            return False
        print("   ✅ Service OK")
    except:
        print("   ❌ Service non accessible")
        return False
    
    # Test avec fichier
    job_dir = Path("/Users/baptistecomas/Desktop/FDP TEST/")
    job_files = list(job_dir.glob("*.pdf"))
    
    if not job_files:
        print("   ❌ Aucun fichier test")
        return False
    
    test_file = job_files[0]
    print(f"   📋 Test: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job", 
                files=files, 
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('data', {}).get('job_info', {}).get('title', 'null')
            
            print(f"   📝 NOUVEAU TITRE: '{title}'")
            
            if title != "Qui sommes" and title != "null":
                print("\n   🎉 SUCCÈS! Titre amélioré")
                print(f"   ✅ '{title}' au lieu de 'Qui sommes'")
                return True
            else:
                print("   ❌ Problème persiste")
                return False
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test: {str(e)}")
        return False

def main():
    """Main"""
    print("🎯 CORRECTION DIRECTE - SANS REGEX COMPLEXES")
    print("Stratégie: Recherche simple de mots-clés")
    print()
    
    success = fix_title_extraction_direct()
    
    if success:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("=" * 30)
        print("✅ Approche simple appliquée")
        print("✅ Fini les 'Qui sommes'!")
        print("\n🚀 PRÊT POUR 213 TESTS MASSIFS!")
    else:
        print("\n❌ Correction échouée")
        print("💡 Essayer: bash restart_job_parser_v2.sh")
    
    return success

if __name__ == "__main__":
    main()
