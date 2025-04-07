#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tableau de bord de matching entre CV et offres d'emploi
Ce script crée un tableau de bord interactif pour visualiser les matchings
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
from app.nlp.matching_engine import match_cv_with_job


def create_matching_dashboard(cvs_folder="documents_a_analyser/cvs/", jobs_folder="documents_a_analyser/offres/"):
    """
    Crée un tableau de bord de matching entre CV et offres d'emploi
    
    Args:
        cvs_folder: Dossier contenant les CV
        jobs_folder: Dossier contenant les offres d'emploi
    """
    # Créer les dossiers s'ils n'existent pas
    Path(cvs_folder).mkdir(parents=True, exist_ok=True)
    Path(jobs_folder).mkdir(parents=True, exist_ok=True)
    
    # Extensions prises en charge
    extensions = [".pdf", ".docx", ".txt", ".html"]
    
    # Collecter tous les CV
    print("\n===== ANALYSE DES CV =====\n")
    cvs = []
    cv_files = []
    for ext in extensions:
        cv_files.extend(glob.glob(f"{cvs_folder}/**/*{ext}", recursive=True))
    
    if not cv_files:
        print(f"Aucun CV trouvé dans {cvs_folder}. Assurez-vous d'y placer des CV au format PDF, DOCX, TXT ou HTML.")
        return
    
    for cv_path in cv_files:
        print(f"Analyse du CV: {os.path.basename(cv_path)}...")
        try:
            result = parse_document(file_path=cv_path)
            cvs.append({
                "id": result.get("id"),
                "filename": os.path.basename(cv_path),
                "parsed_data": result,
                "name": result.get("extracted_data", {}).get("nom", "Candidat inconnu"),
                "skills": result.get("extracted_data", {}).get("competences", []),
                "experience": result.get("extracted_data", {}).get("experience", [])
            })
            print(f"  - Nom: {cvs[-1]['name']}")
            print(f"  - Compétences détectées: {len(cvs[-1]['skills'])}")
        except Exception as e:
            print(f"Erreur lors de l'analyse du CV {cv_path}: {e}")
    
    # Collecter toutes les offres
    print("\n===== ANALYSE DES OFFRES D'EMPLOI =====\n")
    jobs = []
    job_files = []
    for ext in extensions:
        job_files.extend(glob.glob(f"{jobs_folder}/**/*{ext}", recursive=True))
    
    if not job_files:
        print(f"Aucune offre trouvée dans {jobs_folder}. Assurez-vous d'y placer des offres au format PDF, DOCX, TXT ou HTML.")
        return
    
    for job_path in job_files:
        print(f"Analyse de l'offre: {os.path.basename(job_path)}...")
        try:
            result = parse_document(file_path=job_path, doc_type="job_posting")
            jobs.append({
                "id": result.get("id"),
                "filename": os.path.basename(job_path),
                "parsed_data": result,
                "title": result.get("extracted_data", {}).get("titre", "Poste inconnu"),
                "company": result.get("extracted_data", {}).get("entreprise", "Entreprise inconnue"),
                "skills": result.get("extracted_data", {}).get("competences_requises", []),
                "location": result.get("extracted_data", {}).get("lieu", "")
            })
            print(f"  - Titre: {jobs[-1]['title']}")
            print(f"  - Entreprise: {jobs[-1]['company']}")
            print(f"  - Compétences requises: {len(jobs[-1]['skills'])}")
        except Exception as e:
            print(f"Erreur lors de l'analyse de l'offre {job_path}: {e}")
    
    # Vérifier que nous avons au moins un CV et une offre
    if not cvs:
        print("Aucun CV n'a pu être analysé. Impossible de créer le tableau de bord.")
        return
    
    if not jobs:
        print("Aucune offre n'a pu être analysée. Impossible de créer le tableau de bord.")
        return
    
    # Générer une matrice de matching
    print("\n===== CALCUL DES MATCHINGS =====\n")
    matches = []
    
    # Compteurs pour le suivi
    total_matchings = len(cvs) * len(jobs)
    current_matching = 0
    
    for cv in cvs:
        for job in jobs:
            current_matching += 1
            print(f"Matching {current_matching}/{total_matchings}: {cv['name']} ↔ {job['title']}")
            
            try:
                # Calculer le matching
                match_result = match_cv_with_job(cv["parsed_data"], job["parsed_data"])
                
                # Récupérer les données de matching
                matching_skills = match_result.get("matching_skills", [])
                missing_skills = match_result.get("missing_skills", [])
                detail_scores = match_result.get("detail_scores", {})
                
                # Calculer le score global si non fourni
                overall_score = match_result.get("score", 0)
                if overall_score == 0 and detail_scores:
                    overall_score = sum(detail_scores.values()) / len(detail_scores)
                
                matches.append({
                    "cv_id": cv["id"],
                    "cv_name": cv["name"],
                    "cv_skills": cv["skills"],
                    "cv_filename": cv["filename"],
                    "job_id": job["id"],
                    "job_title": job["title"],
                    "job_company": job["company"],
                    "job_skills": job["skills"],
                    "job_filename": job["filename"],
                    "job_location": job["location"],
                    "score": overall_score,
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "detail_scores": detail_scores
                })
                
                # Afficher un résumé du matching
                print(f"  - Score: {overall_score*100:.1f}%")
                print(f"  - Compétences correspondantes: {len(matching_skills)}")
                print(f"  - Compétences manquantes: {len(missing_skills)}")
            except Exception as e:
                print(f"Erreur lors du matching: {e}")
    
    # Trier par score de matching
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    # Créer le répertoire de rapports s'il n'existe pas
    reports_dir = "rapports"
    Path(reports_dir).mkdir(exist_ok=True)
    
    # Exporter les données en JSON pour réutilisation
    json_path = os.path.join(reports_dir, "matching_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"\nDonnées de matching exportées dans {json_path}")
    
    # Générer le tableau de bord HTML
    html_path = os.path.join(reports_dir, "matching_dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(generate_dashboard_html(matches, cvs, jobs))
    
    print(f"Tableau de bord généré dans {html_path}")
    print(f"Ouvrez ce fichier dans votre navigateur pour visualiser les résultats.")


def generate_dashboard_html(matches, cvs, jobs):
    """
    Génère le HTML du tableau de bord de matching
    """
    # Statistiques globales
    top_matches = [m for m in matches if m["score"] >= 0.7]
    medium_matches = [m for m in matches if 0.5 <= m["score"] < 0.7]
    low_matches = [m for m in matches if m["score"] < 0.5]
    
    # Identifier les CV et offres sans bon matching
    cv_ids_with_good_match = set(m["cv_id"] for m in top_matches)
    job_ids_with_good_match = set(m["job_id"] for m in top_matches)
    
    cvs_without_match = [cv for cv in cvs if cv["id"] not in cv_ids_with_good_match]
    jobs_without_match = [job for job in jobs if job["id"] not in job_ids_with_good_match]
    
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tableau de bord de matching</title>
        <style>
            :root {
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --accent-color: #e74c3c;
                --light-color: #ecf0f1;
                --dark-color: #34495e;
                --success-color: #2ecc71;
                --warning-color: #f39c12;
                --danger-color: #e74c3c;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                color: var(--primary-color);
                background-color: #f5f7fa;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            header {
                background-color: var(--primary-color);
                color: white;
                padding: 15px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            header .container {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            header h1 {
                margin: 0;
                font-size: 1.8em;
            }
            
            .dashboard {
                display: flex;
                margin-top: 20px;
                gap: 20px;
                min-height: calc(100vh - 180px);
            }
            
            .matches-list {
                flex: 1;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                overflow-y: auto;
                max-height: calc(100vh - 180px);
            }
            
            .match-details {
                flex: 2;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                position: sticky;
                top: 20px;
            }
            
            .stats-container {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .stat-card {
                flex: 1;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                background-color: white;
                text-align: center;
            }
            
            .stat-card h3 {
                margin-top: 0;
                color: var(--dark-color);
                font-size: 0.9em;
                font-weight: 600;
            }
            
            .stat-card .value {
                font-size: 1.8em;
                font-weight: bold;
                margin: 10px 0;
                color: var(--secondary-color);
            }
            
            .stat-card.green .value { color: var(--success-color); }
            .stat-card.yellow .value { color: var(--warning-color); }
            .stat-card.red .value { color: var(--danger-color); }
            
            table {
                border-collapse: collapse;
                width: 100%;
            }
            
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            
            th {
                background-color: var(--light-color);
                color: var(--dark-color);
                font-weight: 600;
                position: sticky;
                top: 0;
                z-index: 10;
            }
            
            tr:hover {
                background-color: #f5f5f5;
                cursor: pointer;
            }
            
            .selected {
                background-color: rgba(52, 152, 219, 0.1);
                border-left: 4px solid var(--secondary-color);
            }
            
            .score-high { color: var(--success-color); font-weight: bold; }
            .score-medium { color: var(--warning-color); font-weight: bold; }
            .score-low { color: var(--danger-color); font-weight: bold; }
            
            .badge {
                display: inline-block;
                padding: 3px 7px;
                border-radius: 12px;
                font-size: 0.75em;
                font-weight: bold;
                margin-left: 5px;
            }
            
            .badge-success { background-color: #d5f5e3; color: #1e8449; }
            .badge-warning { background-color: #fef9e7; color: #b7950b; }
            .badge-danger { background-color: #fdedec; color: #943126; }
            
            .matching-skills, .missing-skills {
                margin-top: 15px;
            }
            
            .skill {
                display: inline-block;
                padding: 5px 10px;
                margin: 3px;
                border-radius: 15px;
                font-size: 0.9em;
            }
            
            .matching-skill {
                background-color: #d5f5e3;
                color: #1e8449;
            }
            
            .missing-skill {
                background-color: #fdedec;
                color: #943126;
            }
            
            .filters {
                background-color: white;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .filters-row {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: center;
            }
            
            .filter-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .filter-label {
                font-weight: 600;
                font-size: 0.9em;
                color: var(--dark-color);
            }
            
            input[type="range"] {
                width: 150px;
            }
            
            input[type="text"], select {
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-family: inherit;
            }
            
            .score-value {
                font-weight: bold;
                width: 50px;
                display: inline-block;
            }
            
            .actions {
                margin-top: 20px;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            
            button {
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                background-color: var(--secondary-color);
                color: white;
                cursor: pointer;
                font-family: inherit;
                transition: background-color 0.2s;
            }
            
            button:hover {
                background-color: #2980b9;
            }
            
            button.primary {
                background-color: var(--success-color);
            }
            
            button.primary:hover {
                background-color: #27ae60;
            }
            
            button.secondary {
                background-color: var(--light-color);
                color: var(--dark-color);
            }
            
            button.secondary:hover {
                background-color: #bdc3c7;
            }
            
            .match-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid #eee;
            }
            
            .match-title {
                margin: 0;
            }
            
            .match-score {
                font-size: 1.5em;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
            }
            
            .score-pill-high {
                background-color: #d5f5e3;
                color: #1e8449;
            }
            
            .score-pill-medium {
                background-color: #fef9e7;
                color: #b7950b;
            }
            
            .score-pill-low {
                background-color: #fdedec;
                color: #943126;
            }
            
            .match-content {
                display: flex;
                gap: 20px;
            }
            
            .match-column {
                flex: 1;
            }
            
            .profile-card {
                border: 1px solid #eee;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
            }
            
            .profile-card h3 {
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                color: var(--dark-color);
            }
            
            .detail-scores {
                margin-top: 20px;
            }
            
            .progress-bar {
                height: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                margin-top: 5px;
                overflow: hidden;
            }
            
            .progress-value {
                height: 100%;
                background-color: var(--secondary-color);
                border-radius: 4px;
            }
            
            .detail-item {
                margin-bottom: 10px;
            }
            
            .detail-item-label {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 0.9em;
                color: var(--dark-color);
            }
            
            .no-selection-message {
                text-align: center;
                padding: 30px;
                color: #7f8c8d;
                font-style: italic;
            }
            
            .tabs {
                display: flex;
                margin-bottom: 10px;
                border-bottom: 1px solid #ddd;
            }
            
            .tab {
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 3px solid transparent;
            }
            
            .tab.active {
                border-bottom-color: var(--secondary-color);
                font-weight: bold;
                color: var(--secondary-color);
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            @media (max-width: 768px) {
                .dashboard {
                    flex-direction: column;
                }
                
                .match-content {
                    flex-direction: column;
                }
                
                .filters-row {
                    flex-direction: column;
                    align-items: flex-start;
                }
                
                .stats-container {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>Tableau de bord de matching</h1>
                <span>Commitment</span>
            </div>
        </header>
        
        <div class="container">
            <div class="stats-container">
    """
    
    # Statistiques 
    html += f"""
                <div class="stat-card green">
                    <h3>Matchings excellents</h3>
                    <div class="value">{len(top_matches)}</div>
                    <div>Score ≥ 70%</div>
                </div>
                
                <div class="stat-card yellow">
                    <h3>Matchings moyens</h3>
                    <div class="value">{len(medium_matches)}</div>
                    <div>Score 50-69%</div>
                </div>
                
                <div class="stat-card red">
                    <h3>Matchings faibles</h3>
                    <div class="value">{len(low_matches)}</div>
                    <div>Score < 50%</div>
                </div>
                
                <div class="stat-card">
                    <h3>CV sans bon matching</h3>
                    <div class="value">{len(cvs_without_match)}</div>
                    <div>Sur {len(cvs)} CV analysés</div>
                </div>
                
                <div class="stat-card">
                    <h3>Offres sans bon matching</h3>
                    <div class="value">{len(jobs_without_match)}</div>
                    <div>Sur {len(jobs)} offres analysées</div>
                </div>
    """
    
    # Filtres
    html += """
            </div>
            
            <div class="filters">
                <div class="filters-row">
                    <div class="filter-group">
                        <label class="filter-label">Score minimum:</label>
                        <input type="range" id="minScore" min="0" max="100" value="0" oninput="filterMatches()">
                        <span class="score-value" id="scoreValue">0%</span>
                    </div>
                    
                    <div class="filter-group">
                        <label class="filter-label">Recherche:</label>
                        <input type="text" id="searchInput" placeholder="Nom, compétence..." oninput="filterMatches()">
                    </div>
                    
                    <div class="filter-group">
                        <label class="filter-label">Candidat:</label>
                        <select id="cvFilter" onchange="filterMatches()">
                            <option value="">Tous les candidats</option>
    """
    
    # Ajouter les CV au filtre
    for cv in cvs:
        html += f'<option value="{cv["id"]}">{cv["name"]}</option>'
    
    html += """
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label class="filter-label">Offre:</label>
                        <select id="jobFilter" onchange="filterMatches()">
                            <option value="">Toutes les offres</option>
    """
    
    # Ajouter les offres au filtre
    for job in jobs:
        html += f'<option value="{job["id"]}">{job["title"]} - {job["company"]}</option>'
    
    html += """
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('matchesTab')">Matchings</div>
                <div class="tab" onclick="showTab('unmatchedTab')">Sans matching</div>
            </div>
            
            <div class="dashboard">
                <div class="matches-list tab-content active" id="matchesTab">
                    <h2>Matchings (<span id="matchCount">""" + str(len(matches)) + """</span>)</h2>
                    <table id="matchesTable">
                        <tr>
                            <th>Candidat</th>
                            <th>Poste</th>
                            <th>Score</th>
                        </tr>
    """
    
    # Générer les lignes de la table de matchings
    for idx, match in enumerate(matches):
        score_class = "score-high" if match["score"] > 0.7 else "score-medium" if match["score"] > 0.5 else "score-low"
        html += f"""
                        <tr class="match-row" onclick="showMatchDetails({idx})">
                            <td>{match["cv_name"]}</td>
                            <td>{match["job_title"]} - {match["job_company"]}</td>
                            <td class="{score_class}">{match["score"]*100:.1f}%</td>
                        </tr>
        """
    
    html += """
                    </table>
                </div>
                
                <div class="matches-list tab-content" id="unmatchedTab">
                    <div class="profile-card">
                        <h3>CV sans bon matching</h3>
                        <ul>
    """
    
    # Liste des CV sans bon matching
    if cvs_without_match:
        for cv in cvs_without_match:
            html += f'<li>{cv["name"]} ({len(cv["skills"])} compétences)</li>'
    else:
        html += '<li><em>Tous les CV ont au moins un bon matching!</em></li>'
    
    html += """
                        </ul>
                    </div>
                    
                    <div class="profile-card">
                        <h3>Offres sans bon matching</h3>
                        <ul>
    """
    
    # Liste des offres sans bon matching
    if jobs_without_match:
        for job in jobs_without_match:
            html += f'<li>{job["title"]} - {job["company"]} ({len(job["skills"])} compétences)</li>'
    else:
        html += '<li><em>Toutes les offres ont au moins un bon matching!</em></li>'
    
    html += """
                        </ul>
                    </div>
                </div>
                
                <div class="match-details" id="matchDetails">
                    <div class="no-selection-message">
                        <h2>Détails du matching</h2>
                        <p>Sélectionnez un matching dans la liste pour voir les détails.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Données des matchings
            const matches = """
    
    # Ajouter les données JSON
    html += json.dumps(matches, ensure_ascii=False)
    
    html += """;
            
            // Variable pour suivre l'index de matching sélectionné
            let selectedMatchIndex = -1;
            
            function showMatchDetails(idx) {
                // Supprimer la sélection précédente
                const rows = document.querySelectorAll('.match-row');
                rows.forEach(row => row.classList.remove('selected'));
                
                // Ajouter la sélection à la ligne cliquée
                if (idx >= 0 && idx < rows.length) {
                    rows[idx].classList.add('selected');
                }
                
                selectedMatchIndex = idx;
                const match = matches[idx];
                
                // Afficher les détails
                const detailsDiv = document.getElementById('matchDetails');
                
                // Déterminer la classe de score
                let scoreClass = match.score > 0.7 ? 'score-pill-high' : match.score > 0.5 ? 'score-pill-medium' : 'score-pill-low';
                
                // Générer les compétences correspondantes
                let matchingSkillsHtml = '';
                match.matching_skills.forEach(skill => {
                    matchingSkillsHtml += `<span class="skill matching-skill">${skill}</span>`;
                });
                
                // Générer les compétences manquantes
                let missingSkillsHtml = '';
                match.missing_skills.forEach(skill => {
                    missingSkillsHtml += `<span class="skill missing-skill">${skill}</span>`;
                });
                
                // Générer les scores détaillés
                let detailScoresHtml = '';
                if (match.detail_scores && Object.keys(match.detail_scores).length > 0) {
                    detailScoresHtml += '<div class="detail-scores"><h3>Scores détaillés</h3>';
                    
                    for (const [category, score] of Object.entries(match.detail_scores)) {
                        detailScoresHtml += `
                            <div class="detail-item">
                                <div class="detail-item-label">
                                    <span>${category}</span>
                                    <span>${(score*100).toFixed(1)}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-value" style="width: ${score*100}%"></div>
                                </div>
                            </div>
                        `;
                    }
                    
                    detailScoresHtml += '</div>';
                }
                
                // Générer le contenu complet
                detailsDiv.innerHTML = `
                    <div class="match-header">
                        <h2 class="match-title">Matching: ${match.cv_name} & ${match.job_title}</h2>
                        <span class="match-score ${scoreClass}">${(match.score*100).toFixed(1)}%</span>
                    </div>
                    
                    <div class="match-content">
                        <div class="match-column">
                            <div class="profile-card">
                                <h3>Candidat</h3>
                                <p><strong>Nom:</strong> ${match.cv_name}</p>
                                <p><strong>Fichier:</strong> ${match.cv_filename}</p>
                                <p><strong>Compétences (${match.cv_skills.length}):</strong></p>
                                <div>
                                    ${match.cv_skills.map(skill => `<span class="skill">${skill}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="match-column">
                            <div class="profile-card">
                                <h3>Offre d'emploi</h3>
                                <p><strong>Poste:</strong> ${match.job_title}</p>
                                <p><strong>Entreprise:</strong> ${match.job_company}</p>
                                <p><strong>Lieu:</strong> ${match.job_location || 'Non spécifié'}</p>
                                <p><strong>Compétences requises (${match.job_skills.length}):</strong></p>
                                <div>
                                    ${match.job_skills.map(skill => `<span class="skill">${skill}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="matching-skills">
                        <h3>Compétences correspondantes (${match.matching_skills.length})</h3>
                        ${matchingSkillsHtml || '<p>Aucune compétence correspondante</p>'}
                    </div>
                    
                    <div class="missing-skills">
                        <h3>Compétences manquantes (${match.missing_skills.length})</h3>
                        ${missingSkillsHtml || '<p>Aucune compétence manquante</p>'}
                    </div>
                    
                    ${detailScoresHtml}
                    
                    <div class="actions">
                        <button class="primary" onclick="alert('Candidat contacté !')">Contacter le candidat</button>
                        <button onclick="alert('Matching enregistré !')">Enregistrer ce matching</button>
                        <button class="secondary" onclick="alert('Rapport généré !')">Générer un rapport</button>
                    </div>
                `;
            }
            
            function filterMatches() {
                const minScore = document.getElementById('minScore').value / 100;
                document.getElementById('scoreValue').textContent = minScore * 100 + '%';
                
                const searchText = document.getElementById('searchInput').value.toLowerCase();
                const cvFilter = document.getElementById('cvFilter').value;
                const jobFilter = document.getElementById('jobFilter').value;
                
                const rows = document.querySelectorAll('.match-row');
                let visibleCount = 0;
                
                // Parcourir toutes les lignes
                for (let i = 0; i < matches.length; i++) {
                    const match = matches[i];
                    let visible = true;
                    
                    // Filtre par score
                    if (match.score < minScore) {
                        visible = false;
                    }
                    
                    // Filtre par recherche
                    if (searchText && visible) {
                        const searchFields = [
                            match.cv_name.toLowerCase(),
                            match.job_title.toLowerCase(),
                            match.job_company.toLowerCase(),
                            ...match.cv_skills.map(s => s.toLowerCase()),
                            ...match.job_skills.map(s => s.toLowerCase())
                        ];
                        
                        if (!searchFields.some(field => field.includes(searchText))) {
                            visible = false;
                        }
                    }
                    
                    // Filtre par CV
                    if (cvFilter && visible) {
                        if (match.cv_id !== cvFilter) {
                            visible = false;
                        }
                    }
                    
                    // Filtre par offre
                    if (jobFilter && visible) {
                        if (match.job_id !== jobFilter) {
                            visible = false;
                        }
                    }
                    
                    // Appliquer la visibilité
                    if (i < rows.length) {
                        if (visible) {
                            rows[i].style.display = '';
                            visibleCount++;
                        } else {
                            rows[i].style.display = 'none';
                        }
                    }
                }
                
                // Mettre à jour le compteur
                document.getElementById('matchCount').textContent = visibleCount;
                
                // Si l'item sélectionné précédemment n'est plus visible, effacer les détails
                if (selectedMatchIndex >= 0 && rows[selectedMatchIndex].style.display === 'none') {
                    document.getElementById('matchDetails').innerHTML = `
                        <div class="no-selection-message">
                            <h2>Détails du matching</h2>
                            <p>Sélectionnez un matching dans la liste pour voir les détails.</p>
                        </div>
                    `;
                    selectedMatchIndex = -1;
                }
            }
            
            function showTab(tabId) {
                // Cacher tous les contenus d'onglets
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Désactiver tous les onglets
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Activer l'onglet sélectionné
                document.getElementById(tabId).classList.add('active');
                
                // Activer le bouton d'onglet correspondant
                Array.from(document.querySelectorAll('.tab')).find(tab => 
                    tab.getAttribute('onclick').includes(tabId)
                ).classList.add('active');
            }
            
            // Initialiser les filtres
            document.addEventListener('DOMContentLoaded', function() {
                filterMatches();
                
                // Sélectionner automatiquement le premier matching s'il y en a
                if (matches.length > 0) {
                    showMatchDetails(0);
                }
            });
        </script>
    </body>
    </html>
    """
    
    return html


# Point d'entrée si le script est exécuté directement
if __name__ == "__main__":
    # Vérifier les arguments
    if len(sys.argv) > 2:
        create_matching_dashboard(cvs_folder=sys.argv[1], jobs_folder=sys.argv[2])
    else:
        print("Usage: python create_matching_dashboard.py dossier_cv dossier_offres")
        print("Utilisation des dossiers par défaut...")
        create_matching_dashboard()