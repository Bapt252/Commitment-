#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch Debug Endpoint - Enhanced Parser V3.0
Ajout endpoint debug pour diagnostic extraction PDF
"""

debug_endpoint_code = '''
@app.post("/debug_pdf_text")
async def debug_pdf_text_extraction(file: UploadFile = File(...)):
    """🔍 Debug extraction texte PDF pour diagnostic parser"""
    try:
        # Lecture fichier
        content = await file.read()
        filename = file.filename.lower()
        
        # Extraction texte
        if filename.endswith('.pdf'):
            text = DocumentParser.extract_text_from_pdf(content)
        else:
            raise HTTPException(status_code=400, detail="Seuls les PDF sont supportés pour debug")
        
        # Analyse du texte extrait
        lines = text.split('\\n')
        first_lines = lines[:20]  # Premières 20 lignes
        
        return {
            "success": True,
            "filename": file.filename,
            "extracted_text": text,
            "text_length": len(text),
            "lines_count": len(lines),
            "first_20_lines": first_lines,
            "contains_zachary": "zachary" in text.lower() or "pardo" in text.lower(),
            "contains_dates": any(pattern in text for pattern in ["2023", "2024", "2020", "2021", "2022"]),
            "contains_experience": "expérience" in text.lower() or "experience" in text.lower()
        }
        
    except Exception as e:
        logger.error(f"Erreur debug PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''

print("🔧 CODE ENDPOINT DEBUG À AJOUTER:")
print("=" * 50)
print("Ajoutez ce code dans app_simple_fixed.py avant la ligne:")
print("@app.get('/test_enhanced')")
print()
print(debug_endpoint_code)
print()
print("🚀 INSTRUCTIONS PATCH:")
print("1. Ouvrez app_simple_fixed.py")
print("2. Trouvez la ligne: @app.get('/test_enhanced')")  
print("3. Ajoutez le code debug_endpoint juste AVANT")
print("4. Redémarrez l'API: python app_simple_fixed.py")
print("5. Testez: curl -X POST 'http://localhost:5067/debug_pdf_text' -F 'file=@/Users/baptistecomas/Desktop/Zachary.pdf'")
