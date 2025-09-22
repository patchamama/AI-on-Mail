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
        
        # if not model:
        #     model = self.default_model
        model = self.default_model  # Force default model for now
        
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
        
        # if not model:
        #     model = self.default_model
        model = self.default_model  # Force default model for now
        
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
        self.default_model = os.getenv('OLLAMA_MODEL_DEFAULT', 'gpt-oss:20b')
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
                "num_predict": int(max_tokens)  
            }
        }
        
        try:
            print(f" Querying Ollama ({model})...")
            print(f" Context: {self.base_url}/generate Model: {model} Data: {data}  ")
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

def query_with_fallback(prompt: str, preferred_provider: str = "chatgpt", 
                       model: str = "", max_tokens: int = 2000, **kwargs) -> Dict[str, Any]:
    """
    Query AI with automatic fallback to other providers if the first one fails
    
    Args:
        prompt (str): The prompt to send
        preferred_provider (str): First provider to try
        model (str): Specific model (optional)
        max_tokens (int): Token limit
        **kwargs: Additional arguments
        
    Returns:
        Dict with 'response', 'provider_used', 'attempts', 'errors'
    """
    result = {
        'response': None,
        'provider_used': None,
        'attempts': [],
        'errors': []
    }
    
    # Check if fallback is enabled
    enable_fallback = os.getenv('ENABLE_FALLBACK', 'true').lower() in ['true', '1', 'yes']
    
    if not enable_fallback:
        # Only try the preferred provider
        provider = get_provider_by_name(preferred_provider)
        if not provider:
            result['errors'].append(f"Provider {preferred_provider} not available")
            return result
            
        try:
            response = provider.query(prompt, model=model, max_tokens=max_tokens, **kwargs)
            if response and response.strip():
                result['response'] = response
                result['provider_used'] = preferred_provider
                result['attempts'].append({
                    'provider': preferred_provider,
                    'status': 'success'
                })
            else:
                result['errors'].append(f"{preferred_provider}: Empty response")
        except Exception as e:
            result['errors'].append(f"{preferred_provider}: {str(e)}")
        
        return result
    
    # Get all available providers
    available_providers = get_available_providers()
    if not available_providers:
        result['errors'].append("No AI providers available")
        return result
    
    # Create priority order from environment variable or default
    fallback_order = os.getenv('FALLBACK_ORDER', 'chatgpt,gemini,ollama')
    preferred_order = [p.strip() for p in fallback_order.split(',')]
    
    # Get available provider names
    provider_names = [p.name for p in available_providers]
    
    # Put preferred provider first if available, then follow the configured order
    ordered_providers = []
    if preferred_provider in provider_names:
        ordered_providers.append(preferred_provider)
    
    # Add remaining providers in fallback order
    for provider_name in preferred_order:
        if provider_name in provider_names and provider_name not in ordered_providers:
            ordered_providers.append(provider_name)
    
    # Add any remaining providers not in the configured order
    for provider_name in provider_names:
        if provider_name not in ordered_providers:
            ordered_providers.append(provider_name)
    
    # Try each provider in order
    for i, provider_name in enumerate(ordered_providers):
        provider = get_provider_by_name(provider_name)
        if not provider:
            continue
            
        attempt_info = {
            'provider': provider_name,
            'model': model if model else provider.default_model,
            'status': 'attempting',
            'attempt_number': i + 1
        }
        result['attempts'].append(attempt_info)
        
        try:
            if i == 0:
                print(f"Trying {provider.display_name}...")
            else:
                print(f"Fallback {i}: Trying {provider.display_name}...")
            
            # Use provider-specific model or default
            query_model = model if model else provider.default_model
            
            response = provider.query(prompt, model=query_model, max_tokens=max_tokens, **kwargs)
            
            if response and response.strip():
                result['response'] = response
                result['provider_used'] = provider_name
                attempt_info['status'] = 'success'
                
                if i == 0:
                    print(f"Success with {provider.display_name}")
                else:
                    print(f"Fallback success with {provider.display_name}")
                break
            else:
                attempt_info['status'] = 'empty_response'
                result['errors'].append(f"{provider_name}: Empty response")
                print(f"{provider.display_name}: Empty response, trying next...")
                
        except Exception as e:
            attempt_info['status'] = 'error'
            attempt_info['error'] = str(e)
            error_msg = f"{provider_name}: {str(e)}"
            result['errors'].append(error_msg)
            
            # Check for specific error types
            error_lower = str(e).lower()
            if any(term in error_lower for term in ['rate limit', 'quota exceeded', 'billing', 'unauthorized', 'forbidden', '429', '403']):
                print(f"{provider.display_name}: Rate limit/quota error detected, trying next provider...")
            elif any(term in error_lower for term in ['timeout', 'connection', 'network']):
                print(f"{provider.display_name}: Connection error, trying next provider...")
            else:
                print(f"{provider.display_name}: Error - {str(e)}")
            continue
    
    if not result['response']:
        print("All available AI providers failed")
    
    return result