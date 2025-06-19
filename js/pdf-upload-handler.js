// PDF Upload Handler v2.13.2 - Extraction texte améliorée
class PDFUploadHandler {
    constructor() {
        this.pdfjsLib = window.pdfjsLib;
        if (this.pdfjsLib) {
            this.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        }
    }
    
    async extractTextFromPDF(file) {
        if (!this.pdfjsLib) {
            console.error('❌ PDF.js not loaded');
            return null;
        }
        
        try {
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await this.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
            let fullText = '';
            
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const textContent = await page.getTextContent();
                const pageText = textContent.items.map(item => item.str).join(' ');
                fullText += pageText + '\n';
            }
            
            console.log('✅ PDF text extracted:', fullText.length, 'characters');
            return fullText;
        } catch (error) {
            console.error('❌ PDF extraction error:', error);
            return null;
        }
    }
}

window.PDFUploadHandler = PDFUploadHandler;
