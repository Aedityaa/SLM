"""Universal input processor that handles all modalities"""
from .latex_parser import LaTeXParser
from .ocr_parser import OCRParser
from .speech_processor import SpeechProcessor
from .pdf_processor import PDFProcessor
from .text_cleaner import TextCleaner

class UniversalMathInputProcessor:
    """Handles all input modalities"""
    
    def __init__(self):
        self.latex_parser = LaTeXParser()
        self.ocr_parser = OCRParser()
        self.speech_processor = SpeechProcessor()
        self.pdf_processor = PDFProcessor(self.ocr_parser)
        self.text_cleaner = TextCleaner()
    
    def process(self, input_data):
        """Universal input handler"""
        
        # Detect input type
        input_type = self.detect_input_type(input_data)
        
        if input_type == "text":
            return self.process_text(input_data)
        
        elif input_type == "latex":
            return self.latex_parser.parse_latex(input_data)
        
        elif input_type == "image":
            text = self.ocr_parser.ocr_math_advanced(input_data)
            return self.process_text(text)
        
        elif input_type == "handwriting":
            text = self.ocr_parser.recognize_handwriting(input_data)
            return self.process_text(text)
        
        elif input_type == "audio":
            text = self.speech_processor.speech_to_math(input_data)
            return self.process_text(text)
        
        elif input_type == "pdf":
            text = self.pdf_processor.process_pdf(input_data)
            return self.process_text(text)
        
        elif input_type == "json":
            return self.parse_structured_input(input_data)
        
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    def detect_input_type(self, data):
        """Auto-detect what kind of input this is"""
        if isinstance(data, str):
            if data.endswith(('.jpg', '.png', '.jpeg')):
                return "image"
            elif data.endswith('.pdf'):
                return "pdf"
            elif data.endswith(('.wav', '.mp3', '.ogg')):
                return "audio"
            elif '\\' in data or '$' in data:
                return "latex"
            else:
                return "text"
        elif isinstance(data, dict):
            return "json"
        else:
            return "unknown"
    
    def process_text(self, text):
        """Process plain text input"""
        text = self.text_cleaner.normalize_unicode(text)
        text = self.text_cleaner.clean_whitespace(text)
        return text
    
    def parse_structured_input(self, data):
        """Parse JSON/dict input"""
        # Expected format: {"problem": "...", "type": "calculus"}
        if isinstance(data, dict) and 'problem' in data:
            return self.process_text(data['problem'])
        return str(data)