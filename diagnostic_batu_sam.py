#!/usr/bin/env python3
"""
Script de diagnostic pour BATU Sam.pdf
Teste différentes méthodes d'extraction de texte
"""

import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
import os
import logging

def diagnose_pdf_extraction(pdf_path):
    """
    Diagnostic complet d'un fichier PDF avec différentes librairies
    """
    print(f"🔍 DIAGNOSTIC PDF: {pdf_path}")
    print("=" * 60)
    
    # Vérification existence fichier
    if not os.path.exists(pdf_path):
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return
    
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
    
    # 2. Test avec pdfplumber
    print("\n2️⃣ TEST pdfplumber:")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"   📄 Nombre de pages: {num_pages}")
            
            text_plumber = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_plumber += page_text
            
            results['pdfplumber'] = len(text_plumber)
            print(f"   📝 Caractères extraits: {len(text_plumber)}")
            if len(text_plumber) > 0:
                print(f"   🔍 Aperçu: {text_plumber[:100]}...")
                
    except Exception as e:
        print(f"   ❌ Erreur pdfplumber: {e}")
        results['pdfplumber'] = 0
    
    # 3. Test avec PyMuPDF (fitz)
    print("\n3️⃣ TEST PyMuPDF (fitz):")
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
    
    # 4. Analyse métadonnées
    print("\n4️⃣ MÉTADONNÉES PDF:")
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
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ EXTRACTION:")
    for method, char_count in results.items():
        status = "✅" if char_count > 0 else "❌"
        print(f"   {status} {method}: {char_count} caractères")
    
    # Recommandation
    best_method = max(results.items(), key=lambda x: x[1])
    print(f"\n🎯 MEILLEURE MÉTHODE: {best_method[0]} ({best_method[1]} caractères)")
    
    return results

def test_cv_parser_api(pdf_path):
    """
    Test du CV Parser API actuel
    """
    print(f"\n🔗 TEST CV PARSER API (port 5051):")
    import requests
    
    try:
        with open(pdf_path, 'rb') as file:
            files = {'file': file}
            response = requests.post('http://localhost:5051/parse', files=files)
            
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response: {response.status_code}")
            print(f"   📝 Caractères extraits: {len(data.get('text', ''))}")
            print(f"   👤 Nom: {data.get('name', 'Non trouvé')}")
            print(f"   🎯 Missions: {len(data.get('missions', []))}")
            print(f"   🏆 Score qualité: {data.get('quality_score', 0)}%")
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur connexion API: {e}")

if __name__ == "__main__":
    # Chemin vers BATU Sam.pdf
    pdf_path = "/Users/baptistecomas/Desktop/CV TEST/BATU Sam.pdf"
    
    # Diagnostic complet
    results = diagnose_pdf_extraction(pdf_path)
    
    # Test API actuelle
    test_cv_parser_api(pdf_path)
    
    print("\n🔧 ACTIONS RECOMMANDÉES:")
    if all(count == 0 for count in results.values()):
        print("   ❌ Le PDF semble corrompu ou protégé")
        print("   💡 Essayer de le réouvrir avec un lecteur PDF et le re-exporter")
    elif max(results.values()) > 0:
        best = max(results.items(), key=lambda x: x[1])
        print(f"   ✅ Utiliser {best[0]} pour ce fichier")
        print(f"   🔄 Modifier le CV Parser pour utiliser cette méthode")
    
    print("   🚀 Relancer ce script après les corrections")
