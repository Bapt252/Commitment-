#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Traitement par lots des documents pour le parsing
Ce script analyse plusieurs documents en une seule fois et génère un rapport HTML
"""

import sys
import os
import glob
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# Import des modules nécessaires
from app.nlp.enhanced_parsing_system import parse_document

def batch_parsing(docs_folder="documents_a_analyser/"):
    """
    Traite tous les documents dans un dossier et génère un rapport HTML
    
    Args:
        docs_folder: Chemin vers le dossier contenant les documents à analyser
    """
    # Créer le dossier s'il n'existe pas
    Path(docs_folder).mkdir(parents=True, exist_ok=True)
    
    # Créer un rapport consolidé
    results = []
    
    # Extensions prises en charge
    extensions = [".pdf", ".docx", ".txt", ".html"]
    
    # Collecter tous les fichiers avec les extensions supportées
    all_files = []
    for ext in extensions:
        all_files.extend(glob.glob(f"{docs_folder}/**/*{ext}", recursive=True))
    
    if not all_files:
        print(f"Aucun document trouvé dans {docs_folder}. Assurez-vous d'y placer des documents PDF, DOCX, TXT ou HTML.")
        return
    
    # Traiter tous les documents d'un coup
    for doc_path in all_files:
        print(f"Traitement de {os.path.basename(doc_path)}...")
        try:
            result = parse_document(file_path=doc_path)
            
            # Extraire les informations essentielles uniquement
            summary = {
                "filename": os.path.basename(doc_path),
                "doc_type": result.get("doc_type", "inconnu"),
                "confiance_globale": sum(result.get("confidence_scores", {}).values()) / max(1, len(result.get("confidence_scores", {}))),
                "nb_competences": len(result.get("extracted_data", {}).get("competences", [])),
                "competences": result.get("extracted_data", {}).get("competences", []),
                "chemin_complet": doc_path,
                "id": result.get("id")
            }
            results.append(summary)
        except Exception as e:
            print(f"Erreur lors du traitement de {doc_path}: {e}")
    
    if not results:
        print("Aucun document n'a pu être traité correctement.")
        return
    
    # Trier par confiance (pour corriger les plus problématiques en premier)
    results.sort(key=lambda x: x["confiance_globale"])
    
    # Créer le répertoire de rapports s'il n'existe pas
    reports_dir = "rapports"
    Path(reports_dir).mkdir(exist_ok=True)
    
    # Nom du fichier de rapport
    report_file = os.path.join(reports_dir, "rapport_parsing.html")
    
    # Exporter un rapport HTML interactif
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rapport de Parsing</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                tr:hover { background-color: #f5f5f5; }
                .low { background-color: #ffcccc; }
                .medium { background-color: #ffffcc; }
                .high { background-color: #ccffcc; }
                .button { padding: 5px 10px; cursor: pointer; }
                .skills { font-size: 0.9em; color: #555; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                #detailsPanel { display: none; position: fixed; top: 10%; left: 10%; right: 10%; bottom: 10%; background: white; padding: 20px; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0,0,0,0.2); overflow: auto; z-index: 1000; }
                .close-btn { float: right; padding: 5px 10px; cursor: pointer; }
                pre { background: #f5f5f5; padding: 10px; overflow: auto; }
            </style>
        </head>
        <body>
            <h1>Rapport de Parsing (Traités: """ + str(len(results)) + """)</h1>
            <p>Cliquez sur une ligne pour voir les détails du document.</p>
            <table id="resultsTable">
                <tr>
                    <th>Document</th>
                    <th>Type</th>
                    <th>Confiance</th>
                    <th>Compétences</th>
                    <th>Compétences détectées</th>
                </tr>
        """)
        
        for idx, r in enumerate(results):
            confidence_class = "high" if r["confiance_globale"] > 0.7 else "medium" if r["confiance_globale"] > 0.5 else "low"
            
            # Formatage des compétences pour l'affichage
            skills_display = ", ".join(r["competences"]) if r["competences"] else "Aucune compétence détectée"
            
            f.write(f"""
                <tr class="{confidence_class}" onclick="showDocument('{r['chemin_complet']}')">
                    <td>{r["filename"]}</td>
                    <td>{r["doc_type"]}</td>
                    <td>{r["confiance_globale"]*100:.1f}%</td>
                    <td>{r["nb_competences"]}</td>
                    <td class="skills">{skills_display}</td>
                </tr>
            """)
        
        f.write("""
            </table>
            
            <div id="detailsPanel">
                <button class="close-btn" onclick="closeDetailsPanel()">✕</button>
                <h2>Détails du document</h2>
                <div id="documentDetails"></div>
            </div>
            
            <script>
                // Stocker les chemins de fichiers pour les réutiliser
                const filePaths = {};
                
                function showDocument(path) {
                    const detailsPanel = document.getElementById('detailsPanel');
                    const documentDetails = document.getElementById('documentDetails');
                    
                    // Afficher un message de chargement
                    documentDetails.innerHTML = '<p>Chargement des détails...</p>';
                    detailsPanel.style.display = 'block';
                    
                    // Si nous avons déjà les détails dans le cache
                    if (filePaths[path]) {
                        documentDetails.innerHTML = filePaths[path];
                        return;
                    }
                    
                    // Simuler une requête API pour obtenir les détails complets
                    // Note: Dans une implémentation réelle, vous feriez une vraie requête AJAX
                    setTimeout(() => {
                        const content = generateMockDetails(path);
                        documentDetails.innerHTML = content;
                        filePaths[path] = content;
                    }, 500);
                }
                
                function closeDetailsPanel() {
                    document.getElementById('detailsPanel').style.display = 'none';
                }
                
                function generateMockDetails(path) {
                    // Dans une implémentation réelle, cette fonction ferait une requête AJAX
                    // pour obtenir les détails du document depuis le serveur
                    return `
                        <p><strong>Fichier:</strong> ${path}</p>
                        <p><strong>Note:</strong> Cette fonctionnalité simule l'affichage des détails. Pour une véritable analyse, implémentez une API de récupération des résultats complets.</p>
                        <p>Pour une analyse complète, exécutez cette commande dans votre terminal:</p>
                        <pre>python -m app.scripts.document_details "${path}"</pre>
                    `;
                }
            </script>
        </body>
        </html>
        """)
    
    print(f"\nRapport généré dans {report_file}")
    print(f"Ouvrez ce fichier dans votre navigateur pour visualiser les résultats.")
    
    # Exporter également les données en JSON pour utilisation ultérieure
    json_file = os.path.join(reports_dir, "rapport_parsing.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Données exportées en JSON dans {json_file}")
    
    # Affiche les résultats dans la console pour un meilleur retour visuel
    print("\n=== RÉSUMÉ DES DOCUMENTS ANALYSÉS ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("\nNombre total de documents traités:", len(results))
    return results

# Point d'entrée si le script est exécuté directement
if __name__ == "__main__":
    # Utiliser le dossier en argument ou un dossier par défaut
    folder = sys.argv[1] if len(sys.argv) > 1 else "documents_a_analyser"
    batch_parsing(folder)