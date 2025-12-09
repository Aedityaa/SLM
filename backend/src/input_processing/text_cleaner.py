"""Text normalization and cleaning utilities"""

class TextCleaner:
    """Normalize and clean mathematical text"""
    
    def __init__(self):
        self.unicode_replacements = {
            '∫': 'integrate',
            '∂': 'partial',
            '∑': 'sum',
            '√': 'sqrt',
            '²': '^2',
            '³': '^3',
            '×': '*',
            '÷': '/',
            'π': 'pi',
            '∞': 'infinity',
        }
    
    def normalize_unicode(self, text):
        """Convert Unicode math symbols to ASCII"""
        for unicode_char, replacement in self.unicode_replacements.items():
            text = text.replace(unicode_char, replacement)
        return text
    
    def clean_whitespace(self, text):
        """Remove extra whitespace"""
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_special_chars(self, text):
        """Remove non-mathematical special characters"""
        # Keep only alphanumeric, math operators, and parentheses
        import re
        text = re.sub(r'[^a-zA-Z0-9+\-*/^()=\s.,]', '', text)
        return text