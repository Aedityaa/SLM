"""LaTeX parsing and conversion utilities"""
import re


class LaTeXParser:
    """Converts LaTeX mathematical notation to plain text"""
    
    def __init__(self):
        self.latex_mappings = {
            '\\int': 'integrate',
            '\\sum': 'sum',
            '\\prod': 'product',
            '\\partial': 'partial',
            '\\sqrt': 'sqrt',
            '\\cdot': '*',
            '\\times': '*',
            '\\div': '/',
            '\\pi': 'pi',
            '\\infty': 'infinity',
            # Add more mappings
        }

    def _consume_brace_group(self, text, start):
        """Given `text[start] == '{'`, return (content, index_after_closing_brace),
        correctly handling nested braces. Returns (None, start) if there is
        no brace at `start` or it's never closed."""
        if start >= len(text) or text[start] != '{':
            return None, start
        depth = 0
        i = start
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return text[start + 1:i], i + 1
            i += 1
        return None, start  # unbalanced

    def _convert_frac(self, text):
        """Convert \\frac{a}{b} -> ((a)/(b)), handling nested braces (e.g.
        \\frac{a+\\sqrt{b}}{c}) and nested fracs, unlike the previous
        implementation which only matched the literal placeholder text
        "\\frac{a}{b}" and therefore never converted a real fraction."""
        marker = '\\frac{'
        out = []
        i = 0
        changed = True
        # Re-run until no \frac remains, so nested fracs get fully unwound.
        while changed:
            changed = False
            out = []
            i = 0
            while i < len(text):
                if text.startswith(marker, i):
                    num, after_num = self._consume_brace_group(text, i + len(marker) - 1)
                    if num is not None and after_num < len(text) and text[after_num] == '{':
                        den, after_den = self._consume_brace_group(text, after_num)
                        if den is not None:
                            out.append(f'(({num})/({den}))')
                            i = after_den
                            changed = True
                            continue
                out.append(text[i])
                i += 1
            text = ''.join(out)
        return text

    def _convert_sqrt(self, text):
        """Convert \\sqrt{x} -> sqrt(x), brace-aware (handles nested content
        like \\sqrt{a+b} correctly, unlike a naive string replace)."""
        marker = '\\sqrt{'
        out = []
        i = 0
        while i < len(text):
            if text.startswith(marker, i):
                content, after = self._consume_brace_group(text, i + len(marker) - 1)
                if content is not None:
                    out.append(f'sqrt({content})')
                    i = after
                    continue
            out.append(text[i])
            i += 1
        return ''.join(out)

    def parse_latex(self, text):
        """Convert LaTeX symbols to plain math"""
        text = self._convert_frac(text)
        text = self._convert_sqrt(text)
        # Simple 1:1 command replacements. Use a negative lookahead so
        # "\int" doesn't also eat the start of a longer, unrelated command.
        for command, replacement in self.latex_mappings.items():
            if command == '\\sqrt':
                continue  # handled by _convert_sqrt above (needs braces)
            pattern = re.escape(command) + r'(?![a-zA-Z])'
            text = re.sub(pattern, replacement, text)
        return text
    
    def extract_latex_blocks(self, text):
        """Extract LaTeX from $ $ or $$ $$ delimiters"""
        import re
        # Find inline math: $...$
        inline = re.findall(r'\$(.+?)\$', text)
        # Find display math: $$...$$
        display = re.findall(r'\$\$(.+?)\$\$', text)
        return {'inline': inline, 'display': display}