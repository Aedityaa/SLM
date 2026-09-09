"""Output formatting for mathematical results"""
import re

class OutputFormatter:
    """Formats and cleans mathematical answers from LLM output"""
    
    def __init__(self):
        # Pattern to find 'Final Answer: ...' text tag (boxed LaTeX is
        # extracted separately -- see _extract_boxed -- because \boxed{}
        # content routinely contains nested braces, e.g. \boxed{\frac{3}{4}},
        # which a regex like \boxed\{(.*?)\} cannot correctly balance).
        self.final_answer_pattern = r'Final Answer:\s*(.*)'
        self.boxed_marker = r'\boxed{'

    def format(self, text: str) -> str:
        """Add structural formatting (markdown) to the solution text"""
        # Standardize whitespace and markdown. Only split on 'Step' when
        # it starts a step marker (e.g. "Step 1:"), not on any substring
        # match, to avoid mangling words like "Stepping"/"stepwise".
        formatted = re.sub(r'(?<!\n)\bStep(?=\s*\d)', '\n### Step', text)
        return formatted.strip()

    def _extract_boxed(self, text: str):
        """Find the first \\boxed{...} and return its content, correctly
        handling nested braces (fractions, exponents, etc.) by scanning for
        the matching closing brace instead of using a non-greedy regex."""
        idx = text.find(self.boxed_marker)
        if idx == -1:
            return None
        start = idx + len(self.boxed_marker)
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        if depth != 0:
            # Unbalanced braces (truncated generation) -- don't guess.
            return None
        return text[start:i - 1]

    def extract_final_answer(self, text: str) -> str:
        """Extract only the numeric or symbolic result"""
        # 1. Try boxed LaTeX output (common in math models)
        boxed_content = self._extract_boxed(text)
        if boxed_content is not None:
            return boxed_content
            
        # 2. Try 'Final Answer' text tag
        final_match = re.search(self.final_answer_pattern, text)
        if final_match:
            return final_match.group(1).strip()
            
        # 3. Fallback to the last sentence
        sentences = text.split('.')
        return sentences[-1].strip() if sentences else "Unknown"

def clean_latex(text: str) -> str:
    """Standalone function to clean LaTeX delimiters for the Agent"""
    if not text: return ""
    # Convert \[ \] to $$ $$
    text = re.sub(r'\\\[', '$$', text)
    text = re.sub(r'\\\]', '$$', text)
    # Convert \( \) to $ $
    text = re.sub(r'\\\(', '$', text)
    text = re.sub(r'\\\)', '$', text)
    return text