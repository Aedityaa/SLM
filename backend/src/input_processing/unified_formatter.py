"""Universal input processor that handles all modalities"""
import re
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
            # Run the same unicode/whitespace normalization plain text
            # gets, in addition to LaTeX-specific conversion -- previously
            # latex-classified input skipped normalize_unicode/
            # clean_whitespace entirely, so things like doubled spaces or
            # stray unicode math symbols passed straight through untouched.
            cleaned = self.text_cleaner.normalize_unicode(input_data)
            cleaned = self.text_cleaner.clean_whitespace(cleaned)
            return self.latex_parser.parse_latex(cleaned)
        
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
            elif self._looks_like_latex(data):
                return "latex"
            else:
                return "text"
        elif isinstance(data, dict):
            return "json"
        else:
            return "unknown"
    
    def _looks_like_latex(self, text):
        """Decide whether text contains real LaTeX, as opposed to just
        happening to contain a backslash or dollar sign.

        The previous check (`'\\' in data or '$' in data`) misrouted very
        common inputs -- e.g. any word problem mentioning money ("a shirt
        costs $20") -- into the LaTeX path, which skips normal text
        cleaning and (before this fix) barely understood real LaTeX either.
        This version requires either:
          - an actual LaTeX command (backslash + letters, e.g. \\frac,
            \\sqrt, \\int), or
          - a $...$ / $$...$$ math delimiter pair whose content isn't just
            a plain dollar amount (a lone '$' followed by a digit, as in
            "$20", is almost always money, not opening math mode).
        """
        if re.search(r'\\[a-zA-Z]+', text):
            return True
        if re.search(r'\$\$.+?\$\$', text, re.DOTALL):
            return True
        if re.search(r'\$(?!\d)[^$\n]+\$', text):
            return True
        return False

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