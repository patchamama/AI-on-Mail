"""
AI Email Processor Package
Automated email processing with AI
"""

__version__ = "0.0.5"
__author__ = "AI Email Processor Team"

from .core import EmailAIProcessor
from .ai_providers import ChatGPTProvider, GeminiProvider, OllamaProvider
from .document_parser import DocumentParser
from .email_client import EmailClient
from .prompt_templates import PromptTemplateManager

__all__ = [
    'EmailAIProcessor',
    'ChatGPTProvider',
    'GeminiProvider', 
    'OllamaProvider',
    'DocumentParser',
    'EmailClient',
    'PromptTemplateManager'
]