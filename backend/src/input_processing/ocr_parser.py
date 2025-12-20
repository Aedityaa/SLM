"""OCR processing for mathematical images"""
import pytesseract
from PIL import Image, ImageEnhance

class OCRParser:
    """Optical Character Recognition for math notation"""
    
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\mappr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        self.config = r'--oem 3 --psm 6'
    
    def ocr_math_advanced(self, image):
        """Better OCR specifically for mathematical notation"""
        img = Image.open(image)
        
        # Preprocessing for better accuracy
        img = img.convert('L')  # Convert to grayscale
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # Increase contrast
        
        # Use special config for math symbols
        text = pytesseract.image_to_string(img, config=self.config)
        
        return text
    
    def recognize_handwriting(self, image):
        """Specialized handwriting recognition"""
        # Could integrate with Google Vision API or Azure Computer Vision
        # For now, use enhanced OCR
        return self.ocr_math_advanced(image)