"""
AI Providers Module

This module contains all AI provider integrations including OpenAI ChatGPT,
Google Gemini, and Ollama local models.
"""

import os
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from openai import OpenAI
from ai_email_processor.constants import GEMINI_URL, OLLAMA_URL, OPENAI_URL


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self):
        self.name = ""
        self.display_name = ""
        self.default_model = ""
    
    @abstractmethod
    def query(self, prompt: str, model: str = "", max_tokens: int = 4000, **kwargs) -> Optional[str]:
        """Query the AI provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Return provider information"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'default_model': self.default_model,
            'available': self.is_available()
        }


class ChatGPTProvider(AIProvider):
    """Provider for OpenAI ChatGPT"""
    
    def __init__(self):
        super().__init__()
        self.name = "chatgpt"
        self.display_name = "ChatGPT (OpenAI)"
        self.default_model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = OPENAI_URL
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.api_key)
    
    def query(self, prompt: str, model: str = "", max_tokens: int = 4000, **kwargs) -> Optional[str]:
        """Query ChatGPT API"""
        if not self.is_available():
            print("Error: OpenAI API key not configured")
            return None
        
        if not model:
            model = self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            # "max_tokens": max_tokens,
            "temperature": kwargs.get('temperature', 0.7)
        }
        
        try:
            print(f" Querying ChatGPT ({model})...")
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Error in ChatGPT request: {e}")
            return None
        except KeyError as e:
            print(f"Error processing ChatGPT response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


class GeminiProvider(AIProvider):
    """Provider for Google Gemini"""
    
    from ai_email_processor.constants import GEMINI_URL
    
    def __init__(self):
        super().__init__()
        self.name = "gemini"
        self.display_name = "Gemini (Google)"
        self.default_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = GEMINI_URL

    def is_available(self) -> bool:
        """Check if Gemini API is configured"""
        return bool(self.api_key)
    
    def query(self, prompt: str, model: str = "", max_tokens: int = 4000, **kwargs) -> Optional[str]:
        """Query Gemini API"""
        if not self.is_available():
            print("Error: Gemini API key not configured")
            return None
        
        if not model:
            model = self.default_model
        
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": kwargs.get('temperature', 0.7),
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 10
            }
        }
        
        try:
            print(f" Querying Gemini ({model})...")
            print(f" Context: {url} Model: {model} Header: {headers} Data: {data}  ")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            print(f" Result: {result} ")
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text'].strip()
            
            print("Unexpected Gemini response format")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error in Gemini request: {e}")
            return None
        except KeyError as e:
            print(f"Error processing Gemini response: {e}")
            return None


class OllamaProvider(AIProvider):
    """Provider for local Ollama"""
    
    def __init__(self):
        super().__init__()
        self.name = "ollama"
        self.display_name = "Ollama (Local)"
        self.default_model = "llama2"
        self.base_url = OLLAMA_URL
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            response.raise_for_status()
            result = response.json()
            return [model['name'] for model in result.get('models', [])]
        except:
            return []
    
    def query(self, prompt: str, model: str = "", max_tokens: int = 4000, **kwargs) -> Optional[str]:
        """Query local Ollama"""
        if not self.is_available():
            print("Error: Ollama not available at localhost:11434")
            return None
        
        if not model:
            model = self.default_model
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": max_tokens
            }
        }
        
        try:
            print(f" Querying Ollama ({model})...")
            response = requests.post(f"{self.base_url}/generate", json=data)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Error in Ollama request: {e}")
            return None


def get_available_providers() -> List[AIProvider]:
    """Return list of available AI providers"""
    providers = [
        ChatGPTProvider(),
        GeminiProvider(),
        OllamaProvider()
    ]
    
    return [provider for provider in providers if provider.is_available()]


def get_provider_by_name(name: str) -> Optional[AIProvider]:
    """Get provider by name"""
    providers = {
        'chatgpt': ChatGPTProvider(),
        'gemini': GeminiProvider(),
        'ollama': OllamaProvider()
    }
    
    provider = providers.get(name.lower())
    if provider and provider.is_available():
        return provider
    return None