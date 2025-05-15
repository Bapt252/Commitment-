"""
Module de visualisation pour le système Nexten SmartMatch.
Ce module permet de générer des tableaux de bord visuels pour les résultats de matching.
"""

import os
import json
from typing import List, Dict, Any

class MatchVisualizer:
    """
    Classe principale pour visualiser les résultats de matching.
    Génère des tableaux de bord HTML et des rapports sur les matches.
    """
    
    def __init__(self, output_dir: str = "output/dashboard"):
        """
        Initialise le visualiseur de matching.
        
        Args:
            output_dir (str): Répertoire où les fichiers de visualisation seront générés
        """
        self.output_dir = output_dir
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Charger les templates
        self.templates = {
            "dashboard": self._load_template("dashboard"),
            "match_card": self._load_template("match_card"),
            "skills_section": self._load_template("skills_section"),
            "location_section": self._load_template("location_section")
        }
    
    def _load_template(self, template_name: str) -> str:
        """
        Charge un template HTML.
        Si le template n'existe pas, retourne un template par défaut.
        
        Args:
            template_name (str): Nom du template à charger
            
        Returns:
            str: Contenu du template
        """
        # Templates par défaut
        default_templates = {
            "dashboard": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexten SmartMatch - Tableau de bord</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                    .dashboard { max-width: 1200px; margin: 0 auto; }
                    .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
                    .summary { background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .matches-container { display: flex; flex-wrap: wrap; gap: 20px; }
                    .filters { background-color: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                    .filter-group { margin-bottom: 10px; }
                    .filter-label { font-weight: bold; margin-right: 10px; }
                    .filter-options { display: flex; gap: 10px; }
                    .filter-option { cursor: pointer; padding: 5px 10px; border-radius: 3px; background-color: #eee; }
                    .filter-option.active { background-color: #3498db; color: white; }
                </style>
            </head>
            <body>
                <div class="dashboard">
                    <div class="header">
                        <h1>Nexten SmartMatch - Tableau de bord</h1>
                        <p>Résultats de matching bidirectionnel entre candidats et entreprises</p>
                    </div>
                    
                    <div class="summary">
                        <h2>Résumé</h2>
                        <p>Nombre total de matches: {{total_matches}}</p>
                        <p>Score moyen: {{average_score}}</p>
                        <p>Meilleur match: {{best_match}}</p>
                    </div>
                    
                    <div class="filters">
                        <h2>Filtres</h2>
                        <div class="filter-group">
                            <span class="filter-label">Score minimum:</span>
                            <div class="filter-options">
                                <span class="filter-option active" data-value="0">Tous</span>
                                <span class="filter-option" data-value="0.7">70%+</span>
                                <span class="filter-option" data-value="0.8">80%+</span>
                                <span class="filter-option" data-value="0.9">90%+</span>
                            </div>
                        </div>
                    </div>
                    
                    <h2>Résultats de matching</h2>
                    <div class="matches-container">
                        {{match_cards}}
                    </div>
                </div>
                
                <script>
                    // JavaScript pour filtres interactifs
                    document.querySelectorAll('.filter-option').forEach(option => {
                        option.addEventListener('click', function() {
                            // Activer l'option sélectionnée
                            const filterGroup = this.closest('.filter-group');
                            filterGroup.querySelectorAll('.filter-option').forEach(opt => {
                                opt.classList.remove('active');
                            });
                            this.classList.add('active');
                            
                            // Appliquer les filtres
                            applyFilters();
                        });
                    });
                    
                    function applyFilters() {
                        const minScore = document.querySelector('.filter-option.active[data-value]').dataset.value;
                        
                        document.querySelectorAll('.match-card').forEach(card => {
                            const score = parseFloat(card.dataset.score);
                            if (score >= minScore) {
                                card.style.display = 'block';
                            } else {
                                card.style.display = 'none';
                            }
                        });
                    }
                </script>
            </body>
            </html>
            """,
            
            "match_card": """
            <div class="match-card" data-score="{{score}}">
                <style>
                    .match-card { 
                        background-color: white; 
                        border-radius: 5px; 
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
                        padding: 20px;
                        width: 100%;
                        max-width: 350px;
                    }
                    .score-container { 
                        display: flex; 
                        align-items: center; 
                        margin-bottom: 15px;
                    }
                    .score-circle {
                        width: 60px;
                        height: 60px;
                        border-radius: 50%;
                        background-color: {{score_color}};
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 20px;
                        font-weight: bold;
                        margin-right: 15px;
                    }
                    .score-details {
                        flex: 1;
                    }
                    .match-title {
                        font-size: 18px;
                        font-weight: bold;
                        margin: 0 0 5px 0;
                    }
                    .match-subtitle {
                        color: #666;
                        margin: 0;
                    }
                    .details-section {
                        margin-top: 15px;
                        border-top: 1px solid #eee;
                        padding-top: 15px;
                    }
                    .detail-item {
                        display: flex;
                        margin-bottom: 10px;
                    }
                    .detail-label {
                        width: 40%;
                        font-weight: bold;
                        color: #555;
                    }
                    .detail-value {
                        width: 60%;
                    }
                    .detail-value.good {
                        color: #27ae60;
                    }
                    .detail-value.medium {
                        color: #f39c12;
                    }
                    .detail-value.poor {
                        color: #e74c3c;
                    }
                    .skill-tag {
                        display: inline-block;
                        background-color: #f0f0f0;
                        padding: 3px 8px;
                        border-radius: 3px;
                        margin: 2px;
                        font-size: 12px;
                    }
                    .skill-match {
                        background-color: #d5f5e3;
                    }
                    .skill-missing {
                        background-color: #fadbd8;
                    }
                </style>
                
                <div class="score-container">
                    <div class="score-circle">{{score_percentage}}</div>
                    <div class="score-details">
                        <h3 class="match-title">{{candidate_name}} ↔ {{company_name}}</h3>
                        <p class="match-subtitle">Match #{{match_id}}</p>
                    </div>
                </div>
                
                <div class="details-section">
                    <div class="detail-item">
                        <div class="detail-label">Compétences:</div>
                        <div class="detail-value {{skills_class}}">{{skills_score}}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Localisation:</div>
                        <div class="detail-value {{location_class}}">{{location_score}}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Télétravail:</div>
                        <div class="detail-value {{remote_class}}">{{remote_score}}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Expérience:</div>
                        <div class="detail-value {{experience_class}}">{{experience_score}}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Salaire:</div>
                        <div class="detail-value {{salary_class}}">{{salary_score}}</div>
                    </div>
                </div>
                
                {{skills_section}}
                {{location_section}}
            </div>
            """,
            
            "skills_section": """
            <div class="details-section">
                <h4>Compétences</h4>
                <div>
                    <p><strong>Communes:</strong></p>
                    <div>
                        {{matched_skills}}
                    </div>
                    <p><strong>Manquantes:</strong></p>
                    <div>
                        {{missing_skills}}
                    </div>
                </div>
            </div>
            """,
            
            "location_section": """
            <div class="details-section">
                <h4>Informations de localisation</h4>
                <div class="detail-item">
                    <div class="detail-label">Adresse candidat:</div>
                    <div class="detail-value">{{candidate_location}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Adresse entreprise:</div>
                    <div class="detail-value">{{company_location}}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Temps de trajet:</div>
                    <div class="detail-value">{{travel_time}}</div>
                </div>
            </div>
            """
        }
        
        # Retourner le template par défaut
        return default_templates.get(template_name, "")
    
    def generate_dashboard(self, match_results: List[Dict[str, Any]]) -> str:
        """
        Génère un tableau de bord HTML avec les résultats de matching.
        
        Args:
            match_results (list): Liste des résultats de matching
            
        Returns:
            str: Chemin vers le fichier HTML généré
        """
        if not match_results:
            return ""
        
        # Trier les résultats par score décroissant
        match_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Générer les cartes de match
        match_cards = ""
        for i, match in enumerate(match_results):
            match_cards += self._generate_match_card(match, i + 1)
        
        # Calculer les statistiques
        total_matches = len(match_results)
        average_score = sum(match["score"] for match in match_results) / total_matches if total_matches > 0 else 0
        best_match = f"{match_results[0]['candidate_id']} ↔ {match_results[0]['company_id']} ({match_results[0]['score']:.2f})" if total_matches > 0 else "Aucun"
        
        # Générer le tableau de bord
        dashboard_html = self.templates["dashboard"]
        dashboard_html = dashboard_html.replace("{{total_matches}}", str(total_matches))
        dashboard_html = dashboard_html.replace("{{average_score}}", f"{average_score:.2f}")
        dashboard_html = dashboard_html.replace("{{best_match}}", best_match)
        dashboard_html = dashboard_html.replace("{{match_cards}}", match_cards)
        
        # Enregistrer le tableau de bord
        output_path = os.path.join(self.output_dir, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dashboard_html)
        
        return output_path
    
    def _generate_match_card(self, match: Dict[str, Any], match_id: int) -> str:
        """
        Génère une carte HTML pour un match spécifique.
        
        Args:
            match (dict): Résultat de matching
            match_id (int): ID unique du match
            
        Returns:
            str: HTML de la carte de match
        """
        score = match["score"]
        details = match["details"]
        
        # Calculer la couleur du score
        if score >= 0.8:
            score_color = "#27ae60"  # Vert
        elif score >= 0.6:
            score_color = "#f39c12"  # Orange
        else:
            score_color = "#e74c3c"  # Rouge
        
        # Convertir les scores en classes CSS
        def get_class(score):
            if score >= 0.8:
                return "good"
            elif score >= 0.6:
                return "medium"
            else:
                return "poor"
        
        # Générer la section des compétences
        skills_section = self.templates["skills_section"]
        
        # Compétences communes et manquantes
        matched_skills_html = ""
        for skill in details.get("matched_skills", []):
            matched_skills_html += f'<span class="skill-tag skill-match">{skill}</span>'
        
        missing_skills_html = ""
        for skill in details.get("missing_skills", []):
            missing_skills_html += f'<span class="skill-tag skill-missing">{skill}</span>'
        
        skills_section = skills_section.replace("{{matched_skills}}", matched_skills_html or "Aucune")
        skills_section = skills_section.replace("{{missing_skills}}", missing_skills_html or "Aucune")
        
        # Générer la section de localisation
        location_section = self.templates["location_section"]
        location_section = location_section.replace("{{candidate_location}}", match.get("candidate_location", "Non spécifié"))
        location_section = location_section.replace("{{company_location}}", match.get("company_location", "Non spécifié"))
        
        travel_time = details.get("travel_time_minutes", "N/A")
        if travel_time != "N/A":
            travel_time = f"{travel_time} minutes"
        location_section = location_section.replace("{{travel_time}}", str(travel_time))
        
        # Générer la carte complète
        card_html = self.templates["match_card"]
        card_html = card_html.replace("{{score}}", str(score))
        card_html = card_html.replace("{{score_percentage}}", f"{int(score * 100)}%")
        card_html = card_html.replace("{{score_color}}", score_color)
        card_html = card_html.replace("{{candidate_name}}", f"Candidat {match['candidate_id']}")
        card_html = card_html.replace("{{company_name}}", f"Entreprise {match['company_id']}")
        card_html = card_html.replace("{{match_id}}", str(match_id))
        
        # Remplacer les détails des scores
        card_html = card_html.replace("{{skills_score}}", f"{details.get('skills_score', 0):.2f}")
        card_html = card_html.replace("{{location_score}}", f"{details.get('location_score', 0):.2f}")
        card_html = card_html.replace("{{remote_score}}", f"{details.get('remote_score', 0):.2f}")
        card_html = card_html.replace("{{experience_score}}", f"{details.get('experience_score', 0):.2f}")
        card_html = card_html.replace("{{salary_score}}", f"{details.get('salary_score', 0):.2f}")
        
        # Remplacer les classes CSS
        card_html = card_html.replace("{{skills_class}}", get_class(details.get("skills_score", 0)))
        card_html = card_html.replace("{{location_class}}", get_class(details.get("location_score", 0)))
        card_html = card_html.replace("{{remote_class}}", get_class(details.get("remote_score", 0)))
        card_html = card_html.replace("{{experience_class}}", get_class(details.get("experience_score", 0)))
        card_html = card_html.replace("{{salary_class}}", get_class(details.get("salary_score", 0)))
        
        # Remplacer les sections
        card_html = card_html.replace("{{skills_section}}", skills_section)
        card_html = card_html.replace("{{location_section}}", location_section)
        
        return card_html
    
    def export_json(self, match_results: List[Dict[str, Any]], filename: str = "matches.json") -> str:
        """
        Exporte les résultats de matching au format JSON.
        
        Args:
            match_results (list): Liste des résultats de matching
            filename (str): Nom du fichier JSON
            
        Returns:
            str: Chemin vers le fichier JSON généré
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(match_results, f, indent=2)
        
        return output_path
    
    def generate_report(self, match_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un rapport statistique sur les résultats de matching.
        
        Args:
            match_results (list): Liste des résultats de matching
            
        Returns:
            dict: Statistiques sur les matches
        """
        if not match_results:
            return {
                "total_matches": 0,
                "average_score": 0,
                "score_distribution": {},
                "top_skills_gaps": []
            }
        
        # Statistiques générales
        total_matches = len(match_results)
        average_score = sum(match["score"] for match in match_results) / total_matches
        
        # Distribution des scores
        score_distribution = {
            "excellent": len([m for m in match_results if m["score"] >= 0.8]),
            "good": len([m for m in match_results if 0.7 <= m["score"] < 0.8]),
            "average": len([m for m in match_results if 0.6 <= m["score"] < 0.7]),
            "poor": len([m for m in match_results if m["score"] < 0.6])
        }
        
        # Compétences manquantes les plus fréquentes
        missing_skills_count = {}
        for match in match_results:
            for skill in match["details"].get("missing_skills", []):
                missing_skills_count[skill] = missing_skills_count.get(skill, 0) + 1
        
        top_skills_gaps = sorted(
            [{"skill": skill, "count": count} for skill, count in missing_skills_count.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]  # Top 10
        
        return {
            "total_matches": total_matches,
            "average_score": average_score,
            "score_distribution": score_distribution,
            "top_skills_gaps": top_skills_gaps
        }
