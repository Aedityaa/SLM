"""LaTeX parsing and conversion utilities"""
class LaTeXParser:
    """Converts LaTeX mathematical notation to plain text"""
    
    def __init__(self):
        self.latex_mappings = {
            '\\int': 'integrate',
            '\\sum': 'sum',
            '\\prod': 'product',
            '\\partial': 'partial',
            '\\sqrt': 'sqrt',
            # Add more mappings
        }
    
    def parse_latex(self, text):
        """Convert LaTeX symbols to plain math"""
        text = text.replace('\\int', 'integrate')
        text = text.replace('\\frac{a}{b}', '(a)/(b)')
        text = text.replace('\\sum', 'sum')
        return text
    
    def extract_latex_blocks(self, text):
        """Extract LaTeX from $ $ or $$ $$ delimiters"""
        import re
        # Find inline math: $...$
        inline = re.findall(r'\$(.+?)\$', text)
        # Find display math: $$...$$
        display = re.findall(r'\$\$(.+?)\$\$', text)
        return {'inline': inline, 'display': display}