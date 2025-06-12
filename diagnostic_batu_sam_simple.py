#!/usr/bin/env python3
"""
Script de diagnostic simplifié pour BATU Sam.pdf
Évite les problèmes de compatibilité pdfplumber/pdfminer
"""

import PyPDF2
import fitz  # PyMuPDF
import os
import logging
import requests

def diagnose_pdf_extraction(pdf_path):
    """
    Diagnostic complet d'un fichier PDF avec PyPDF2 et PyMuPDF uniquement
    """
    print(f"🔍 DIAGNOSTIC PDF: {pdf_path}")
    print("=" * 60)
    
    # Vérification existence fichier
    if not os.path.exists(pdf_path):
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return {}
    
    # Infos fichier
    file_size = os.path.getsize(pdf_path)
    print(f"📁 Taille fichier: {file_size} bytes")
    
    results = {}
    
    # 1. Test avec PyPDF2
    print("\n1️⃣ TEST PyPDF2:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"   📄 Nombre de pages: {num_pages}")
            
            text_pypdf2 = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text_pypdf2 += page.extract_text()
            
            results['pypdf2'] = len(text_pypdf2)
            print(f"   📝 Caractères extraits: {len(text_pypdf2)}")
            if len(text_pypdf2) > 0:
                print(f"   🔍 Aperçu: {text_pypdf2[:100]}...")
                
    except Exception as e:
        print(f"   ❌ Erreur PyPDF2: {e}")
        results['pypdf2'] = 0

    # 2. Test avec PyMuPDF (fitz)
    print("\n2️⃣ TEST PyMuPDF (fitz):")
    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        print(f"   📄 Nombre de pages: {num_pages}")
        
        text_fitz = ""
        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            text_fitz += page.get_text()
        
        doc.close()
        
        results['fitz'] = len(text_fitz)
        print(f"   📝 Caractères extraits: {len(text_fitz)}")
        if len(text_fitz) > 0:
            print(f"   🔍 Aperçu: {text_fitz[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Erreur PyMuPDF: {e}")
        results['fitz'] = 0
    
    # 3. Analyse métadonnées
    print("\n3️⃣ MÉTADONNÉES PDF:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            if metadata:
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            else:
                print("   Aucune métadonnée trouvée")
                
    except Exception as e:
        print(f"   ❌ Erreur métadonnées: {e}")
    
    # 4. Test lecture raw bytes
    print("\n4️⃣ ANALYSE CONTENU BRUT:")
    try:
        with open(pdf_path, 'rb') as file:
            # Lire les premiers 1000 bytes
            raw_content = file.read(1000)
            
            # Vérifier la signature PDF
            if raw_content.startswith(b'%PDF-'):
                version = raw_content[:8].decode('ascii', errors='ignore')
                print(f"   ✅ Signature PDF valide: {version}")
            else:
                print("   ❌ Signature PDF invalide")
            
            # Chercher des mots-clés PDF
            keywords = [b'/Type', b'/Page', b'/Contents', b'/Font']
            found_keywords = [kw for kw in keywords if kw in raw_content]
            print(f"   📋 Mots-clés PDF trouvés: {len(found_keywords)}/{len(keywords)}")
            
    except Exception as e:
        print(f"   ❌ Erreur analyse brute: {e}")
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ EXTRACTION:")
    for method, char_count in results.items():
        status = "✅" if char_count > 0 else "❌"
        print(f"   {status} {method}: {char_count} caractères")
    
    # Recommandation
    if results:
        best_method = max(results.items(), key=lambda x: x[1])
        print(f"\n🎯 MEILLEURE MÉTHODE: {best_method[0]} ({best_method[1]} caractères)")
    
    return results

def test_cv_parser_api(pdf_path):
    """
    Test du CV Parser API actuel
    """
    print(f"\n🔗 TEST CV PARSER API (port 5051):")
    
    try:
        with open(pdf_path, 'rb') as file:
            files = {'file': file}
            response = requests.post('http://localhost:5051/parse', files=files, timeout=10)
            
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response: {response.status_code}")
            print(f"   📝 Caractères extraits: {len(data.get('text', ''))}")
            print(f"   👤 Nom: {data.get('name', 'Non trouvé')}")
            print(f"   🎯 Missions: {len(data.get('missions', []))}")
            print(f"   🏆 Score qualité: {data.get('quality_score', 0)}%")
            
            # Afficher le début du texte si disponible
            text = data.get('text', '')
            if text:
                print(f"   🔍 Aperçu texte API: {text[:100]}...")
            
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erreur connexion API: {e}")

def fix_cv_parser_suggestion(results):
    """
    Suggestions pour corriger le CV Parser
    """
    print("\n🔧 SUGGESTIONS DE CORRECTION:")
    
    if not results:
        print("   ❌ Aucune méthode ne fonctionne - PDF corrompu ou protégé")
        print("   💡 Actions recommandées:")
        print("      - Ouvrir le PDF avec un lecteur et le réexporter")
        print("      - Vérifier que le fichier n'est pas protégé")
        print("      - Essayer de convertir en PDF/A")
        return
    
    total_chars = sum(results.values())
    if total_chars == 0:
        print("   ❌ Toutes les méthodes échouent")
        print("   💡 Le PDF pourrait être:")
        print("      - Une image scannée (nécessite OCR)")
        print("      - Protégé en écriture")
        print("      - Corrompu")
    else:
        best_method = max(results.items(), key=lambda x: x[1])
        print(f"   ✅ Utiliser la méthode: {best_method[0]}")
        print(f"   📈 Performance: {best_method[1]} caractères extraits")
        
        if best_method[0] == 'fitz':
            print("   🔄 Modifier le CV Parser pour utiliser PyMuPDF:")
            print("      import fitz")
            print("      doc = fitz.open(pdf_path)")
            print("      text = doc[0].get_text()")
        elif best_method[0] == 'pypdf2':
            print("   🔄 S'assurer que PyPDF2 est bien configuré dans le CV Parser")

def test_other_files():
    """
    Test rapide sur d'autres fichiers CV pour comparaison
    """
    print("\n🔍 TEST DE COMPARAISON SUR AUTRES CV:")
    
    cv_folder = "/Users/baptistecomas/Desktop/CV TEST"
    if not os.path.exists(cv_folder):
        print("   ❌ Dossier CV TEST non trouvé")
        return
    
    pdf_files = [f for f in os.listdir(cv_folder) if f.endswith('.pdf')][:3]  # Test sur 3 fichiers
    
    for pdf_file in pdf_files:
        if 'BATU' in pdf_file:
            continue  # Skip BATU Sam qu'on a déjà testé
            
        pdf_path = os.path.join(cv_folder, pdf_file)
        print(f"\n   📄 Test: {pdf_file}")
        
        # Test rapide avec PyMuPDF seulement
        try:
            doc = fitz.open(pdf_path)
            text = doc[0].get_text() if len(doc) > 0 else ""
            doc.close()
            print(f"      📝 {len(text)} caractères extraits")
        except Exception as e:
            print(f"      ❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC SIMPLIFIÉ BATU Sam.pdf")
    print("=" * 50)
    
    # Chemin vers BATU Sam.pdf
    pdf_path = "/Users/baptistecomas/Desktop/CV TEST/BATU Sam.pdf"
    
    # Diagnostic principal
    results = diagnose_pdf_extraction(pdf_path)
    
    # Test API actuelle
    test_cv_parser_api(pdf_path)
    
    # Suggestions de correction
    fix_cv_parser_suggestion(results)
    
    # Test de comparaison
    test_other_files()
    
    print("\n🎯 RÉSUMÉ:")
    if results and max(results.values()) > 0:
        best = max(results.items(), key=lambda x: x[1])
        print(f"   ✅ Solution trouvée: {best[0]} extrait {best[1]} caractères")
        print(f"   🔄 Prochaine étape: Adapter le CV Parser pour utiliser {best[0]}")
    else:
        print("   ❌ Problème critique: Aucune méthode ne fonctionne")
        print("   🔄 Prochaine étape: Vérifier l'intégrité du fichier PDF")
    
    print("\n🚀 Une fois corrigé, lancer: python3 enhanced_batch_testing_fixed.py")
