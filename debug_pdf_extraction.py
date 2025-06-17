#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug PDF Text Extraction - Diagnostic Enhanced Parser V3.0
Analyse du texte extrait du PDF pour identifier les problèmes de parsing
"""

import requests
import json

def debug_zachary_pdf():
    """Debug extraction texte Zachary.pdf"""
    
    print("🔍 DEBUG EXTRACTION TEXTE ZACHARY.PDF")
    print("=" * 50)
    
    # Endpoint debug à créer dans l'API
    debug_url = "http://localhost:5067/debug_pdf_text"
    
    try:
        with open("/Users/baptistecomas/Desktop/Zachary.pdf", "rb") as f:
            files = {"file": f}
            response = requests.post(debug_url, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Texte extrait du PDF:")
            print("-" * 30)
            text = data.get("extracted_text", "")
            print(text[:1000] + "..." if len(text) > 1000 else text)
            
            print(f"\n📊 Longueur texte: {len(text)} caractères")
            print(f"📄 Premières lignes:")
            lines = text.split('\n')[:10]
            for i, line in enumerate(lines, 1):
                print(f"   {i:2d}: {line.strip()}")
                
        else:
            print(f"❌ Erreur endpoint debug: {response.status_code}")
            print("Créons l'endpoint debug...")
            
    except FileNotFoundError:
        print("❌ Fichier Zachary.pdf non trouvé sur le bureau")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def compare_parsing_results():
    """Compare résultats test unitaire vs PDF"""
    
    print("\n🔍 COMPARAISON TEST UNITAIRE VS PDF")
    print("=" * 50)
    
    # Test unitaire
    try:
        response = requests.get("http://localhost:5067/test_enhanced", timeout=10)
        if response.status_code == 200:
            unit_test = response.json()
            print("✅ Test unitaire:")
            results = unit_test.get("results", {})
            print(f"   👤 Nom: {results.get('name', 'Non détecté')}")
            print(f"   ⏱️ Expérience: {results.get('experience_years', 0)} ans")
            print(f"   🎓 Compétences: {results.get('skills_count', 0)}")
        else:
            print("❌ Test unitaire échoué")
    except Exception as e:
        print(f"❌ Erreur test unitaire: {e}")
    
    # Test PDF réel (résultat précédent)
    print("\n✅ Test PDF réel:")
    print("   👤 Nom: null ❌")
    print("   ⏱️ Expérience: 6230 ans ❌") 
    print("   🎓 Compétences: 32 ✅")
    
    print("\n🎯 DIAGNOSTIC:")
    print("   📄 Extraction texte PDF: Problématique")
    print("   🔍 Patterns nom: Ne matchent pas le texte PDF réel")
    print("   📊 Calcul dates: Bug majeur (6230 ans)")
    print("   ✅ Compétences: Parfaites (32 détectées)")

def suggest_solutions():
    """Suggestions de solutions"""
    
    print("\n🔧 SOLUTIONS RECOMMANDÉES")
    print("=" * 50)
    
    solutions = [
        {
            "problème": "Nom non détecté",
            "cause": "Patterns ne matchent pas texte PDF réel",
            "solution": "Ajuster patterns extraction nom pour PDF",
            "action": "Modifier enhanced_extract_name() avec patterns PDF"
        },
        {
            "problème": "Expérience aberrante (6230 ans)",
            "cause": "Bug calcul dates depuis PDF",
            "solution": "Debug fonction _calculate_months_between()",
            "action": "Ajouter logs calcul dates + validation"
        },
        {
            "problème": "Divergence test unitaire vs PDF",
            "cause": "Texte simulé vs texte PDF différents",
            "solution": "Utiliser texte PDF réel dans test unitaire",
            "action": "Endpoint debug extraction texte"
        }
    ]
    
    for i, sol in enumerate(solutions, 1):
        print(f"{i}. {sol['problème']}")
        print(f"   🔍 Cause: {sol['cause']}")
        print(f"   💡 Solution: {sol['solution']}")
        print(f"   🔧 Action: {sol['action']}")
        print()

def main():
    """Debug principal"""
    debug_zachary_pdf()
    compare_parsing_results()
    suggest_solutions()
    
    print("🚀 PROCHAINES ÉTAPES:")
    print("1. Créer endpoint debug extraction texte")
    print("2. Ajuster patterns nom pour PDF")
    print("3. Corriger calcul dates")
    print("4. Re-tester Zachary.pdf")

if __name__ == "__main__":
    main()
