from flask import Blueprint, request, jsonify, current_app
import tempfile
import os

bp = Blueprint('api', __name__, url_prefix='/api/v1')

@bp.route('/parse', methods=['POST'])
def parse_cv():
    """Parse a CV file (PDF or DOCX) and extract structured information"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check supported file types
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else None
    
    if file_extension not in ['pdf', 'docx']:
        return jsonify({'error': 'Unsupported file format. Please upload PDF or DOCX files.'}), 400
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp:
        file.save(temp.name)
        file_path = temp.name
    
    try:
        # Import services based on file type to avoid circular imports
        if file_extension == 'pdf':
            from app.services.pdf_parser import parse_pdf
            result = parse_pdf(file_path)
        else:  # docx
            from app.services.docx_parser import parse_docx
            result = parse_docx(file_path)
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error parsing CV: {str(e)}")
        return jsonify({'error': 'Failed to parse CV', 'details': str(e)}), 500
    
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})
