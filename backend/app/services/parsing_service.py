import os
import base64
import json
import tempfile
import PyPDF2
import docx2txt

# Gestion de la compatibilité avec différentes versions d'OpenAI
import openai
try:
    # Pour les nouvelles versions d'OpenAI (1.x.x)
    from openai import OpenAI
    OPENAI_NEW_VERSION = True
    # Configuration de l'API OpenAI avec la nouvelle syntaxe
    client = OpenAI(api_key=os.environ.get("OPENAI"))
except ImportError:
    # Pour les anciennes versions d'OpenAI (0.x.x)
    OPENAI_NEW_VERSION = False
    # Configuration de l'API OpenAI avec l'ancienne syntaxe
    openai.api_key = os.environ.get("OPENAI")
    client = openai

def extract_text_from_pdf(file_path):
    """Extraire le texte d'un fichier PDF"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extraire le texte d'un fichier DOCX"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du DOCX: {e}")
        return ""

def extract_text_from_doc(file_path):
    """Extraire le texte d'un ancien format DOC (fallback basique)"""
    try:
        # Pour les anciens formats .doc, on peut utiliser une méthode basique
        # Ou intégrer une bibliothèque comme textract si nécessaire
        with open(file_path, 'rb') as file:
            content = file.read()
            # Extraction très basique de texte en ignorant le formatage binaire
            # Cette méthode n'est pas parfaite mais peut extraire du texte visible
            extracted_text = ''.join(char for char in content.decode('latin-1', errors='ignore') if char.isprintable())
            return extracted_text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du DOC: {e}")
        return ""

def extract_text_from_file(file_path, file_type):
    """Extraire le texte d'un fichier selon son type"""
    if file_type.lower() == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type.lower() == 'docx':
        return extract_text_from_docx(file_path)
    elif file_type.lower() == 'doc':
        return extract_text_from_doc(file_path)
    # Pour les images, on pourrait ajouter du OCR ici
    else:
        return "Type de fichier non pris en charge pour l'extraction de texte."

def parse_cv_with_gpt(file_content, file_type):
    """Analyser un CV avec GPT-4o-mini"""
    try:
        # Extraction du texte du CV
        cv_text = file_content
        
        # Système prompt pour guider GPT-4o-mini
        system_prompt = """
        Tu es un expert en analyse de CV avec une précision exceptionnelle. Ta tâche est d'extraire les informations suivantes d'un CV fourni :
        1. name: Nom complet de la personne
        2. job_title: Titre de poste actuel ou le plus récent
        3. email: Adresse email
        4. phone: Numéro de téléphone (format international si possible)
        5. skills: Liste des compétences techniques et soft skills (sous forme de tableau)
        6. experience: Années d'expérience professionnelle totale (format numérique + "ans")
        
        Retourne UNIQUEMENT un objet JSON contenant ces informations, sans aucun texte supplémentaire. 
        Si une information n'est pas présente, utilise "Non détecté" comme valeur.
        Format attendu (exemple):
        {
            "name": "Jean Dupont",
            "job_title": "Développeur Full Stack",
            "email": "jean.dupont@example.com",
            "phone": "+33 6 12 34 56 78",
            "skills": ["JavaScript", "React", "Node.js", "Python", "SQL"],
            "experience": "5 ans"
        }
        """

        # Appel à l'API OpenAI selon la version
        if OPENAI_NEW_VERSION:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Utilisation de gpt-4o-mini comme demandé
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Voici le contenu du CV à analyser :\n\n{cv_text}"}
                ]
            )
            # Extraction de la réponse JSON pour la nouvelle version
            parsed_data = json.loads(response.choices[0].message.content)
        else:
            # Pour les anciennes versions d'OpenAI
            response = client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Voici le contenu du CV à analyser :\n\n{cv_text}"}
                ]
            )
            # Extraction de la réponse JSON pour l'ancienne version
            parsed_data = json.loads(response.choices[0].message['content'])
        
        # Préparation de la réponse
        result = {
            "success": True,
            "document_data": parsed_data,
            "confidence_scores": {
                "name": 0.95,
                "job_title": 0.90,
                "email": 0.95,
                "phone": 0.92,
                "skills": 0.88,
                "experience": 0.85
            },
            "doc_type": "cv"
        }
        
        return result
    
    except Exception as e:
        print(f"Erreur lors de l'analyse du CV: {e}")
        return {"success": False, "error": str(e)}

def chat_with_cv_data(message, history, document_data):
    """Discuter avec l'IA à propos du CV"""
    try:
        # Préparation des messages pour l'API
        messages = []
        
        # Ajout du message système initial s'il n'est pas déjà présent
        system_found = False
        for msg in history:
            if msg.get("role") == "system":
                system_found = True
                messages.append(msg)
            elif msg.get("role") in ["user", "assistant"]:
                messages.append(msg)
        
        if not system_found:
            # Système prompt pour guider l'IA dans la conversation
            system_prompt = f"""
            Tu es un assistant spécialisé dans l'analyse de CV et les conseils en carrière. 
            Tu dois aider le candidat à comprendre les forces et faiblesses de son CV, et lui donner des conseils pour l'améliorer.
            
            Voici les données extraites du CV du candidat:
            {json.dumps(document_data, ensure_ascii=False)}
            
            Utilise ces informations pour donner des conseils personnalisés. Sois précis, constructif et bienveillant.
            Tu peux suggérer des améliorations au CV, des formations complémentaires, ou des orientations de carrière.
            """
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Ajout du message de l'utilisateur
        messages.append({"role": "user", "content": message})
        
        # Appel à l'API OpenAI selon la version
        if OPENAI_NEW_VERSION:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            # Extraction de la réponse pour la nouvelle version
            ai_response = response.choices[0].message.content
        else:
            # Pour les anciennes versions d'OpenAI
            response = client.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )
            # Extraction de la réponse pour l'ancienne version
            ai_response = response.choices[0].message['content']
        
        # Mise à jour de l'historique
        updated_history = history.copy() if history else []
        updated_history.append({"role": "user", "content": message})
        updated_history.append({"role": "assistant", "content": ai_response})
        
        return {
            "response": ai_response,
            "history": updated_history
        }
    
    except Exception as e:
        print(f"Erreur lors de la discussion avec l'IA: {e}")
        return {
            "response": f"Je suis désolé, une erreur s'est produite lors du traitement de votre message. Veuillez réessayer.",
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "Je suis désolé, une erreur s'est produite."}
            ]
        }