#!/usr/bin/env python3
"""
Script de diagnostic ultra-simplifié pour BATU Sam.pdf
Utilise seulement PyPDF2 et requests (modules déjà installés)
"""

import PyPDF2
import os
import requests

def diagnose_pdf_extraction(pdf_path):
    """
    Diagnostic complet d'un fichier PDF avec PyPDF2 uniquement
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
                page_text = page.extract_text()
                text_pypdf2 += page_text
            
            results['pypdf2'] = len(text_pypdf2)
            print(f"   📝 Caractères extraits: {len(text_pypdf2)}")
            
            if len(text_pypdf2) > 0:
                print(f"   🔍 Aperçu: {text_pypdf2[:100]}...")
            else:
                print("   ⚠️ Aucun texte extrait")
                
            # Test plus détaillé par page
            print(f"   📄 Détail par page:")
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                print(f"      Page {i+1}: {len(page_text)} caractères")
                
    except Exception as e:
        print(f"   ❌ Erreur PyPDF2: {e}")
        results['pypdf2'] = 0

    # 2. Analyse métadonnées
    print("\n2️⃣ MÉTADONNÉES PDF:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            if metadata:
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            else:
                print("   Aucune métadonnée trouvée")
                
            # Infos supplémentaires
            print(f"   🔐 PDF encrypté: {pdf_reader.is_encrypted}")
            
    except Exception as e:
        print(f"   ❌ Erreur métadonnées: {e}")
    
    # 3. Test lecture raw bytes
    print("\n3️⃣ ANALYSE CONTENU BRUT:")
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
            
            # Chercher des mots-clés PDF importants
            keywords = [b'/Type', b'/Page', b'/Contents', b'/Font', b'/Text']
            found_keywords = [kw for kw in keywords if kw in raw_content]
            print(f"   📋 Mots-clés PDF trouvés: {len(found_keywords)}/{len(keywords)}")
            for kw in found_keywords:
                print(f"      ✅ {kw.decode('ascii')}")
            
            # Chercher des problèmes potentiels
            if b'/FlateDecode' in raw_content:
                print("   🗜️ Contenu compressé détecté")
            if b'/XObject' in raw_content:
                print("   🖼️ Images/objets détectés")
                
    except Exception as e:
        print(f"   ❌ Erreur analyse brute: {e}")
    
    # 4. Test méthodes alternatives PyPDF2
    print("\n4️⃣ TESTS ALTERNATIFS PyPDF2:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) > 0:
                page = pdf_reader.pages[0]
                
                # Test extract_text avec options
                try:
                    alt_text = page.extract_text(extraction_mode="layout")
                    print(f"   📝 Mode layout: {len(alt_text)} caractères")
                    results['pypdf2_layout'] = len(alt_text)
                except:
                    print("   ⚠️ Mode layout non supporté")
                
                # Test des annotations
                if '/Annots' in page:
                    print("   📝 Annotations détectées dans le PDF")
                
                # Test des champs de formulaire
                if pdf_reader.form:
                    print("   📝 Formulaire PDF détecté")
                    
    except Exception as e:
        print(f"   ❌ Erreur tests alternatifs: {e}")
    
    return results

def test_cv_parser_api(pdf_path):
    """
    Test du CV Parser API actuel
    """
    print(f"\n🔗 TEST CV PARSER API (port 5051):")
    
    try:
        with open(pdf_path, 'rb') as file:
            files = {'file': file}
            response = requests.post('http://localhost:5051/parse', files=files, timeout=15)
            
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
                print("   ❌ Aucun texte retourné par l'API")
            
            return len(text)
            
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return 0
            
    except requests.exceptions.ConnectionError:
        print("   ❌ CV Parser API non accessible (port 5051)")
        print("   💡 Vérifier que le service est démarré")
        return 0
    except Exception as e:
        print(f"   ❌ Erreur connexion API: {e}")
        return 0

def compare_with_working_cv():
    """
    Test rapide sur un autre CV pour comparaison
    """
    print("\n🔍 TEST DE COMPARAISON:")
    
    cv_folder = "/Users/baptistecomas/Desktop/CV TEST"
    if not os.path.exists(cv_folder):
        print("   ❌ Dossier CV TEST non trouvé")
        return
    
    # Chercher d'autres fichiers PDF
    try:
        pdf_files = [f for f in os.listdir(cv_folder) if f.endswith('.pdf')]
        test_files = [f for f in pdf_files if 'BATU' not in f][:2]  # 2 autres fichiers
        
        for pdf_file in test_files:
            pdf_path = os.path.join(cv_folder, pdf_file)
            print(f"\n   📄 Test: {pdf_file}")
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if len(pdf_reader.pages) > 0:
                        text = pdf_reader.pages[0].extract_text()
                        print(f"      📝 {len(text)} caractères extraits")
                        if len(text) > 0:
                            print(f"      🔍 Aperçu: {text[:50]}...")
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
                
    except Exception as e:
        print(f"   ❌ Erreur scan dossier: {e}")

def analyze_and_recommend(results, api_result):
    """
    Analyse et recommandations
    """
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ EXTRACTION:")
    
    for method, char_count in results.items():
        status = "✅" if char_count > 0 else "❌"
        print(f"   {status} {method}: {char_count} caractères")
    
    print(f"   🔗 API actuelle: {api_result} caractères")
    
    print("\n🔧 DIAGNOSTIC:")
    
    total_extracted = sum(results.values())
    
    if total_extracted == 0 and api_result == 0:
        print("   🚨 PROBLÈME CRITIQUE: Aucune extraction ne fonctionne")
        print("\n💡 CAUSES POSSIBLES:")
        print("   1. PDF scanné (image) → Nécessite OCR")
        print("   2. PDF protégé/encrypté")
        print("   3. PDF corrompu")
        print("   4. Contenu uniquement en images")
        
        print("\n🔧 SOLUTIONS:")
        print("   1. Ouvrir le PDF et vérifier s'il y a du texte sélectionnable")
        print("   2. Re-exporter le PDF depuis un lecteur")
        print("   3. Convertir en PDF/A")
        print("   4. Utiliser un outil OCR si c'est une image")
        
    elif total_extracted > 0 and api_result == 0:
        print("   ⚠️ PROBLÈME: L'extraction locale fonctionne mais pas l'API")
        print("\n🔧 SOLUTIONS:")
        print("   1. Vérifier que le CV Parser utilise la bonne méthode")
        print("   2. Checker les logs du CV Parser")
        print("   3. Tester avec un redémarrage du service")
        
    elif total_extracted == 0 and api_result > 0:
        print("   🤔 ÉTRANGE: L'API fonctionne mais pas PyPDF2 local")
        print("   💡 L'API utilise probablement une autre méthode")
        
    else:
        print("   ✅ TOUT FONCTIONNE: Extraction possible")
        if api_result < max(results.values()):
            print("   ⚠️ Mais l'API pourrait être optimisée")

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC ULTRA-SIMPLIFIÉ BATU Sam.pdf")
    print("=" * 50)
    
    # Chemin vers BATU Sam.pdf
    pdf_path = "/Users/baptistecomas/Desktop/CV TEST/BATU Sam.pdf"
    
    # Diagnostic principal
    results = diagnose_pdf_extraction(pdf_path)
    
    # Test API actuelle
    api_result = test_cv_parser_api(pdf_path)
    
    # Test de comparaison
    compare_with_working_cv()
    
    # Analyse finale
    analyze_and_recommend(results, api_result)
    
    print(f"\n🎯 PROCHAINE ÉTAPE:")
    print("   Lancer: python3 enhanced_batch_testing_fixed.py")
    print("   Pour tester le système complet")
