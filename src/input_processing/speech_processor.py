"""Speech-to-math conversion"""
import speech_recognition as sr

class SpeechProcessor:
    """Convert spoken math to text"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def speech_to_math(self, audio_file):
        """Convert spoken math to text"""
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
        
        text = self.recognizer.recognize_google(audio)
        # "integral of x squared plus three x from zero to five"
        
        # Convert to math notation
        math_text = self.natural_language_to_math(text)
        return math_text
    
    def natural_language_to_math(self, text):
        """Convert natural language to mathematical notation"""
        replacements = {
            'squared': '^2',
            'cubed': '^3',
            'integral of': 'integrate(',
            'from': ',',
            'to': ',',
            'plus': '+',
            'minus': '-',
            'times': '*',
            'divided by': '/',
        }
        
        for phrase, symbol in replacements.items():
            text = text.replace(phrase, symbol)
        
        return text