"""PDF extraction and processing"""
import PyPDF2
from pdf2image import convert_from_path

class PDFProcessor:
    """Extract math problems from PDF documents"""
    
    def __init__(self, ocr_parser=None):
        self.ocr_parser = ocr_parser
    
    def process_pdf(self, pdf_path):
        """Extract math problems from PDF"""
        
        # Method 1: Extract text directly (if PDF has selectable text)
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # Method 2: Convert to images and OCR (if scanned PDF)
        if not text.strip() and self.ocr_parser:
            images = convert_from_path(pdf_path)
            text = ""
            for img in images:
                text += self.ocr_parser.ocr_math_advanced(img)
        
        return text