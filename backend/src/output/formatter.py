"""Output formatting for mathematical results"""
import re

class OutputFormatter:
    """Formats and cleans mathematical answers from LLM output"""
    
    def __init__(self):
        # Pattern to find 'Final Answer: ...' or boxed results
        self.final_answer_pattern = r'Final Answer:\s*(.*)'
        self.boxed_pattern = r'\\boxed\{(.*?)\}'

    def format(self, text: str) -> str:
        """Add structural formatting (markdown) to the solution text"""
        # Standardize whitespace and markdown
        formatted = text.replace('Step', '\n### Step')
        return formatted.strip()

    def extract_final_answer(self, text: str) -> str:
        """Extract only the numeric or symbolic result"""
        # 1. Try boxed LaTeX output (common in math models)
        boxed_match = re.search(self.boxed_pattern, text)
        if boxed_match:
            return boxed_match.group(1)
            
        # 2. Try 'Final Answer' text tag
        final_match = re.search(self.final_answer_pattern, text)
        if final_match:
            return final_match.group(1).strip()
            
        # 3. Fallback to the last sentence
        sentences = text.split('.')
        return sentences[-1].strip() if sentences else "Unknown"