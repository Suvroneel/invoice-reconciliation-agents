from huggingface_hub import InferenceClient
from config import Config
import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LLMClient:
    def __init__(self):
        self.client = InferenceClient(token=Config.HF_TOKEN)
        self.model = Config.HF_MODEL
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Generate text using Hugging Face Inference API"""
        try:
            response = self.client.text_generation(
                prompt,
                model=self.model,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False
            )
            return response
        except Exception as e:
            print(f"LLM Error: {e}")
            return ""
    
    def extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"JSON extraction error: {e}")
            return {}
    
    def generate_structured(self, prompt: str, max_tokens: int = 2000) -> dict:
        """Generate and return structured JSON response"""
        response = self.generate(prompt, max_tokens, temperature=0.1)
        return self.extract_json(response)
