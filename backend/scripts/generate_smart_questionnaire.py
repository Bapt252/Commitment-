#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Générateur de questionnaires intelligents adaptés aux résultats du parsing
Ce script génère des questionnaires personnalisés basés sur les informations manquantes
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# Import des modules nécessaires
from app.nlp.enhanced_parsing_system import parse_document


def generate_questionnaire(document_path=None, document_id=None):
    """
    Génère un questionnaire intelligent basé sur un document
    
    Args:
        document_path: Chemin vers le document à analyser (optionnel)
        document_id: ID d'un document déjà parsé (optionnel)
        
    Note: Il faut fournir soit document_path, soit document_id
    """
    if not document_path and not document_id:
        print("Erreur: Vous devez fournir soit le chemin d'un document, soit l'ID d'un document déjà parsé.")
        return
    
    result = None
    
    # Charger depuis un fichier
    if document_path:
        if not os.path.exists(document_path):
            print(f"Erreur: Le fichier {document_path} n'existe pas.")
            return
            
        print(f"Analyse du document {document_path}...")
        result = parse_document(file_path=document_path)
    
    # Charger depuis un ID (implémentation future)
    elif document_id:
        print(f"Récupération du document avec l'ID {document_id}...")
        # Note: Dans une implémentation réelle, vous récupéreriez les données depuis une base de données
        print("Fonctionnalité non implémentée: utilisez un chemin de fichier à la place.")
        return
    
    # Si nous n'avons pas pu récupérer les données
    if not result:
        print("Erreur: Impossible d'analyser le document.")
        return
    
    # Extraire les informations nécessaires
    extracted_data = result.get('extracted_data', {})
    doc_type = result.get('doc_type', 'unknown')
    confidence_scores = result.get('confidence_scores', {})
    
    # Générer les questions de base selon le type de document
    if doc_type == 'cv':
        questionnaire = generate_cv_questionnaire(extracted_data, confidence_scores)
    elif doc_type == 'job_posting':
        questionnaire = generate_job_questionnaire(extracted_data, confidence_scores)
    else:
        questionnaire = generate_generic_questionnaire(extracted_data, confidence_scores)
    
    # Créer le répertoire de questionnaires s'il n'existe pas
    questionnaires_dir = "questionnaires"
    Path(questionnaires_dir).mkdir(exist_ok=True)
    
    # Déterminer le nom de fichier
    if document_path:
        base_name = os.path.splitext(os.path.basename(document_path))[0]
    else:  # document_id
        base_name = f"document_{document_id}"
    
    # Enregistrer le questionnaire en JSON
    json_path = os.path.join(questionnaires_dir, f"{base_name}_questionnaire.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(questionnaire, f, indent=2, ensure_ascii=False)
    
    # Générer un fichier HTML de questionnaire
    html_path = os.path.join(questionnaires_dir, f"{base_name}_questionnaire.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generate_questionnaire_html(questionnaire, result))
    
    print(f"\nQuestionnaire généré dans {html_path}")
    print(f"Ouvrez ce fichier dans votre navigateur pour visualiser et remplir le questionnaire.")
    print(f"Données JSON exportées dans {json_path}")


def generate_cv_questionnaire(extracted_data, confidence_scores):
    """
    Génère un questionnaire spécifique aux CV
    """
    questions = [
        {
            "id": "q1", 
            "text": "Êtes-vous disponible immédiatement ?", 
            "type": "boolean",
            "required": True
        },
        {
            "id": "q2", 
            "text": "Quel est votre salaire attendu ?", 
            "type": "number",
            "required": False
        },
        {
            "id": "q3", 
            "text": "Préférez-vous travailler en équipe ou en autonomie ?", 
            "type": "choice", 
            "options": ["Équipe", "Autonomie", "Les deux"],
            "required": True
        }
    ]
    
    # Vérifier si les compétences sont extraites avec une confiance suffisante
    if 'competences' not in extracted_data or len(extracted_data.get('competences', [])) < 3 or \
       confidence_scores.get('competences', 0) < 0.7:
        questions.append({
            "id": "q4", 
            "text": "Quelles sont vos principales compétences techniques ?", 
            "type": "text",
            "placeholder": "Ex: Python, Java, SQL, Management d'équipe...",
            "required": True
        })
    
    # Vérifier si les préférences de télétravail sont détectées
    has_remote_preferences = False
    if 'preferences' in extracted_data and 'environment' in extracted_data['preferences']:
        if 'remote' in extracted_data['preferences']['environment'] or \
           'office' in extracted_data['preferences']['environment'] or \
           'hybrid' in extracted_data['preferences']['environment']:
            has_remote_preferences = True
    
    if not has_remote_preferences:
        questions.append({
            "id": "q5", 
            "text": "Préférez-vous travailler en télétravail ou au bureau ?", 
            "type": "choice",
            "options": ["Télétravail", "Bureau", "Hybride"],
            "required": True
        })
    
    # Vérifier si la mobilité est indiquée
    if 'mobilite' not in extracted_data:
        questions.append({
            "id": "q6", 
            "text": "Êtes-vous ouvert à des déplacements professionnels ?", 
            "type": "choice",
            "options": ["Pas de déplacement", "Déplacements occasionnels", "Déplacements fréquents"],
            "required": False
        })
    
    # Vérifier si les langues sont indiquées
    if 'langues' not in extracted_data:
        questions.append({
            "id": "q7", 
            "text": "Quelles langues parlez-vous et à quel niveau ?", 
            "type": "text",
            "placeholder": "Ex: Français (natif), Anglais (courant), Espagnol (notions)...",
            "required": False
        })
    
    return questions


def generate_job_questionnaire(extracted_data, confidence_scores):
    """
    Génère un questionnaire spécifique aux offres d'emploi
    """
    questions = [
        {
            "id": "q1", 
            "text": "Quelle est la date de début souhaitée ?", 
            "type": "date",
            "required": True
        },
        {
            "id": "q2", 
            "text": "Le poste est-il ouvert aux débutants ?", 
            "type": "boolean",
            "required": True
        }
    ]
    
    # Vérifier si le salaire est indiqué
    if 'salaire' not in extracted_data:
        questions.append({
            "id": "q3", 
            "text": "Quelle est la fourchette de salaire pour ce poste ?", 
            "type": "range",
            "required": False
        })
    
    # Vérifier si le mode de travail est indiqué
    if 'mode_travail' not in extracted_data:
        questions.append({
            "id": "q4", 
            "text": "Quel est le mode de travail prévu ?", 
            "type": "choice",
            "options": ["Présentiel", "Télétravail", "Hybride"],
            "required": True
        })
    
    # Vérifier si la durée du contrat est indiquée
    if 'type_contrat' not in extracted_data:
        questions.append({
            "id": "q5", 
            "text": "Quel est le type de contrat ?", 
            "type": "choice",
            "options": ["CDI", "CDD", "Freelance", "Stage", "Alternance"],
            "required": True
        })
    
    # Vérifier si les avantages sont indiqués
    if 'avantages' not in extracted_data:
        questions.append({
            "id": "q6", 
            "text": "Quels sont les avantages proposés avec ce poste ?", 
            "type": "text",
            "placeholder": "Ex: Tickets restaurant, mutuelle, intéressement...",
            "required": False
        })
    
    return questions


def generate_generic_questionnaire(extracted_data, confidence_scores):
    """
    Génère un questionnaire générique pour les types de documents non reconnus
    """
    return [
        {
            "id": "g1", 
            "text": "De quel type de document s'agit-il ?", 
            "type": "choice",
            "options": ["CV", "Offre d'emploi", "Questionnaire", "Autre"],
            "required": True
        },
        {
            "id": "g2", 
            "text": "Quelles sont les informations importantes dans ce document ?", 
            "type": "text",
            "required": True
        }
    ]


def generate_questionnaire_html(questions, result):
    """
    Génère un fichier HTML pour le questionnaire
    """
    doc_type = result.get('doc_type', 'document')
    extracted_data = result.get('extracted_data', {})
    
    # Déterminer le titre du questionnaire
    if doc_type == 'cv':
        title = "Questionnaire complémentaire - CV"
        if 'nom' in extracted_data:
            title += f" de {extracted_data['nom']}"
    elif doc_type == 'job_posting':
        title = "Questionnaire complémentaire - Offre d'emploi"
        if 'titre' in extracted_data:
            title += f" : {extracted_data['titre']}"
    else:
        title = "Questionnaire complémentaire"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .question {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select, textarea {{ padding: 8px; width: 100%; box-sizing: border-box; }}
            .range-inputs {{ display: flex; gap: 10px; }}
            .required {{ color: red; }}
            button {{ padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; border-radius: 3px; }}
            button:hover {{ background: #45a049; }}
            .extracted {{ background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
            .extracted h3 {{ margin-top: 0; color: #555; }}
            .extracted-item {{ margin-bottom: 10px; }}
            .extracted-item strong {{ font-weight: bold; }}
            .info-row {{ display: flex; flex-wrap: wrap; gap: 20px; }}
            .info-col {{ flex: 1; min-width: 200px; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        
        <div class="extracted">
            <h3>Informations déjà extraites</h3>
            <div class="info-row">
    """
    
    # Afficher les informations déjà extraites en deux colonnes
    items = list(extracted_data.items())
    col1_items = items[:len(items)//2 + len(items)%2]
    col2_items = items[len(items)//2 + len(items)%2:]
    
    html += '<div class="info-col">'
    for key, value in col1_items:
        # Ignorer les objets complexes comme les préférences pour simplifier l'affichage
        if isinstance(value, dict):
            continue
            
        # Formater les listes
        if isinstance(value, list):
            value_display = ", ".join(value) if value else "Non spécifié"
        else:
            value_display = value if value else "Non spécifié"
            
        html += f'<div class="extracted-item"><strong>{key}:</strong> {value_display}</div>'
    html += '</div>'
    
    html += '<div class="info-col">'
    for key, value in col2_items:
        # Ignorer les objets complexes comme les préférences pour simplifier l'affichage
        if isinstance(value, dict):
            continue
            
        # Formater les listes
        if isinstance(value, list):
            value_display = ", ".join(value) if value else "Non spécifié"
        else:
            value_display = value if value else "Non spécifié"
            
        html += f'<div class="extracted-item"><strong>{key}:</strong> {value_display}</div>'
    html += '</div>'
    
    html += """
            </div>
        </div>
        
        <h2>Questions complémentaires</h2>
        <p>Merci de compléter les informations suivantes pour améliorer l'analyse.</p>
        
        <form id="questionnaire">
    """
    
    # Générer les questions
    for q in questions:
        required_mark = '<span class="required">*</span>' if q.get('required', False) else ''
        required_attr = 'required' if q.get('required', False) else ''
        placeholder = q.get('placeholder', '')
        
        html += f"""
        <div class="question">
            <label for="{q['id']}">{q['text']} {required_mark}</label>
        """
        
        if q['type'] == 'text':
            html += f'<textarea id="{q["id"]}" name="{q["id"]}" placeholder="{placeholder}" rows="3" {required_attr}></textarea>'
        elif q['type'] == 'number':
            html += f'<input type="number" id="{q["id"]}" name="{q["id"]}" placeholder="{placeholder}" {required_attr}>'
        elif q['type'] == 'boolean':
            html += f'''
            <select id="{q["id"]}" name="{q["id"]}" {required_attr}>
                <option value="">-- Sélectionnez --</option>
                <option value="true">Oui</option>
                <option value="false">Non</option>
            </select>
            '''
        elif q['type'] == 'choice':
            html += f'<select id="{q["id"]}" name="{q["id"]}" {required_attr}><option value="">-- Sélectionnez --</option>'
            for option in q['options']:
                html += f'<option value="{option}">{option}</option>'
            html += '</select>'
        elif q['type'] == 'date':
            html += f'<input type="date" id="{q["id"]}" name="{q["id"]}" {required_attr}>'
        elif q['type'] == 'range':
            html += f'''
            <div class="range-inputs">
                <input type="number" id="{q["id"]}_min" name="{q["id"]}_min" placeholder="Minimum" {required_attr}>
                <input type="number" id="{q["id"]}_max" name="{q["id"]}_max" placeholder="Maximum" {required_attr}>
            </div>
            '''
            
        html += '</div>'
    
    html += """
        <button type="submit">Enregistrer</button>
        </form>
        
        <script>
            document.getElementById('questionnaire').addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Collecter les données du formulaire
                const formData = new FormData(this);
                const data = {};
                
                for (const [key, value] of formData.entries()) {
                    // Traitement spécial pour les booléens
                    if (value === 'true') {
                        data[key] = true;
                    } else if (value === 'false') {
                        data[key] = false;
                    } else {
                        data[key] = value;
                    }
                }
                
                // Afficher les données pour démo
                console.log('Données du questionnaire:', data);
                alert('Questionnaire enregistré !\n\nDans une implémentation réelle, ces données seraient envoyées à un serveur.\n\nConsultez la console pour voir les données.');
                
                // Dans une implémentation réelle
                // fetch('/api/questionnaire', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //     },
                //     body: JSON.stringify(data),
                // });
            });
        </script>
    </body>
    </html>
    """
    
    return html


# Point d'entrée si le script est exécuté directement
if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_questionnaire(document_path=sys.argv[1])
    else:
        print("Erreur: Veuillez fournir le chemin d'un document.")
        print("Usage: python generate_smart_questionnaire.py chemin/vers/document.pdf")
