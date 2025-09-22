
"""
Core Email AI Processor Module
Orchestrates all system components
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .ai_providers import get_available_providers, get_provider_by_name
from .document_parser import DocumentParser
from .email_client import EmailClient


class EmailAIProcessor:
    """Main email processor with AI integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize email AI processor
        
        Args:
            config (Dict): Custom configuration (optional)
        """
        self.config = config or self._load_default_config()
        
        # Initialize components
        self.email_client = EmailClient(self.config)
        self.document_parser = DocumentParser(
            max_size=self.config.get('max_document_size', 10000)
        )
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from environment variables"""
        # Customizable keywords
        custom_keywords = os.getenv('AI_KEYWORDS')
        if custom_keywords:
            ai_keywords = [keyword.strip() for keyword in custom_keywords.split(',')]
        else:
            ai_keywords = [
                'AI', 'ai', 'IA', 'ia',
                'Artificial Intelligence', 'artificial intelligence',
                'Inteligencia Artificial', 'inteligencia artificial',
                'Machine Learning', 'machine learning',
                'ChatGPT', 'chatgpt', 'GPT', 'gpt',
                'Gemini', 'gemini', 'Ollama', 'ollama'
            ]
        
        return {
            # Email configuration
            'imap_server': os.getenv('IMAP_SERVER', 'imap.gmail.com'),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_ADDRESS'),
            'password': os.getenv('EMAIL_PASSWORD'),
            
            # Processing configuration
            'ai_keywords': ai_keywords,
            'max_document_size': int(os.getenv('MAX_DOCUMENT_SIZE', '10000')),
            'check_interval': int(os.getenv('CHECK_INTERVAL', '300')),
        }
    
    def _validate_configuration(self):
        """Validate system configuration"""
        if not self.email_client.is_configured():
            raise ValueError(
                "Incomplete email configuration. "
                "Check EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER"
            )
        
        available_providers = get_available_providers()
        if not available_providers:
            raise ValueError(
                "No AI providers configured. "
                "Configure at least OPENAI_API_KEY, GEMINI_API_KEY or local Ollama"
            )
    
    def get_available_ai_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of available AI providers
        
        Returns:
            List[Dict]: Available providers information
        """
        providers = get_available_providers()
        return [provider.get_info() for provider in providers]
    
    def prepare_ai_prompt(self, email_body: str, 
                         attachments: List[Dict[str, Any]] = None) -> str:
        """
        Prepare AI prompt combining email and attachments
        
        Args:
            email_body (str): Email body
            attachments (List[Dict]): List of processed attachments
            
        Returns:
            str: Combined prompt for AI
        """
        prompt_parts = []
        
        # Base instructions
        prompt_parts.append(
            "You are an AI assistant that responds helpful and professionally and can help to answer questions and correct grammar and literature texts. "
            "If there are attached documents, include them in your analysis.\n\n"
            "If there are options in the answers, you may provide them, but always provide at least one complete answer to each question. The answer text is not in markdown and is in plain text. Always answer in the language of the questionnaire that follows.\n\n"
        )
        
        # Email body
        if email_body.strip():
            # prompt_parts.append(f"RECEIVED EMAIL:\n{email_body}\n\n")
            prompt_parts.append(f"{email_body}\n\n")
        
        # Attachment content
        if attachments:
            prompt_parts.append("ATTACHED DOCUMENTS:\n")
            for attachment in attachments:
                prompt_parts.append(
                    f"Document: {attachment['filename']} ({attachment['type'].upper()}):\n"
                    f"{attachment['content']}\n\n"
                )
        
        # Final instructions
        # prompt_parts.append(
        #     "Please provide a professional and helpful response "
        #     "based on the email content and attached documents. "
        #     "Maintain a friendly but professional tone."
        # )
        
        return "".join(prompt_parts)
    
    def process_single_email(self, mail, email_id: bytes, 
                           ai_provider_name: str, ai_model: str = "") -> bool:
        """
        Process individual email
        
        Args:
            mail: Active IMAP connection
            email_id (bytes): Email ID
            ai_provider_name (str): AI provider name
            ai_model (str): Specific model (optional)
            
        Returns:
            bool: True if processed successfully
        """
        try:
            # Get message
            msg = self.email_client.fetch_email(mail, email_id)
            if not msg:
                return False
            
            # Extract email information
            subject = self.email_client.decode_subject(msg.get('Subject', ''))
            sender = msg.get('From', '')
            
            print(f"\nProcessing email:")
            print(f"   From: {sender}")
            print(f"   Subject: {subject}")
            
            # Check AI keywords
            if not self.email_client.has_ai_keywords(subject):
                print("   No AI keywords found, skipping...")
                return False
            
            print("   AI keywords detected!")
            
            # Extract email body
            body = self.email_client.get_email_body(msg)
            
            # Process attachments
            print("   Checking attachments...")
            attachments = self.document_parser.process_email_attachments(msg)
            
            if attachments:
                print(f"   {len(attachments)} attachment(s) processed")
                for att in attachments:
                    print(f"      • {att['filename']} ({att['size']} characters)")
            
            # Check if there is content to process
            if not body.strip() and not attachments:
                print("   No content to process")
                return False
            
            # Prepare AI prompt
            ai_prompt = self.prepare_ai_prompt(body, attachments)
            print(f"   Prompt prepared ({len(ai_prompt)} characters)")
            
            # Get AI provider
            ai_provider = get_provider_by_name(ai_provider_name)
            if not ai_provider:
                print(f"   AI provider '{ai_provider_name}' not available")
                return False
            
            # Query AI
            ai_response = ai_provider.query(ai_prompt, model=ai_model)
            if not ai_response:
                print("   No AI response obtained")
                return False
            else:
                print(f"   AI response obtained ({len(ai_response)} characters)")
                # Debug: print AI response (optional)
                ai_response += f"\n\n\n Model used: {ai_provider_name} {ai_model if ai_model else ''}\n"
                print(f"\nAI RESPONSE:\n{ai_response}\n")

            # Send response
            sender_email = self.email_client.extract_sender_email(sender)
            if self.email_client.send_response(
                sender_email, subject, body, ai_response, attachments
            ):
                # Mark as read
                self.email_client.mark_as_read(mail, email_id)
                print(f"   Email processed and response sent")
                return True
            else:
                print("   Error sending response")
                return False
                
        except Exception as e:
            print(f"   Error processing email: {e}")
            return False
    
    def process_emails(self, ai_provider: str = "gemini", 
                      ai_model: str = "", max_emails: int = 10) -> int:
        """
        Process unread emails once
        
        Args:
            ai_provider (str): AI provider name
            ai_model (str): Specific model (optional)
            max_emails (int): Maximum number of emails to process
            
        Returns:
            int: Number of successfully processed emails
        """
        print(f"Connecting to email server...")
        mail = self.email_client.connect_imap()
        if not mail:
            return 0
        
        processed_count = 0
        
        try:
            # Search for unread emails
            email_ids = self.email_client.search_unread_emails(mail)
            
            if not email_ids:
                print("   No unread emails")
                return 0
            
            print(f"   {len(email_ids)} unread email(s) found")
            
            # Process emails (limited by max_emails)
            for email_id in email_ids[:max_emails]:
                if self.process_single_email(mail, email_id, ai_provider, ai_model):
                    processed_count += 1
            
            print(f"\nProcessing completed: {processed_count}/{len(email_ids[:max_emails])} emails")
            
        except Exception as e:
            print(f"Error during processing: {e}")
        
        finally:
            self.email_client.close_connection(mail)
        
        return processed_count
    
    def monitor_emails(self, ai_provider: str = "gemini", ai_model: str = "",
                      check_interval: int = None, max_emails: int = 10):
        """
        Monitor emails continuously
        
        Args:
            ai_provider (str): AI provider to use
            ai_model (str): Specific model (optional)
            check_interval (int): Interval between checks in seconds
            max_emails (int): Maximum emails per check
        """
        if check_interval is None:
            check_interval = self.config.get('check_interval', 300)
        
        # Validate provider
        available_providers = self.get_available_ai_providers()
        provider_names = [p['name'] for p in available_providers]
        
        if ai_provider not in provider_names:
            print(f"Provider '{ai_provider}' not available")
            print("Available providers:")
            for provider in available_providers:
                print(f"   • {provider['display_name']}")
            return
        
        print(f"Starting email monitoring...")
        print(f"   Server: {self.config['imap_server']}")
        print(f"   AI Provider: {ai_provider}")
        if ai_model:
            print(f"   Model: {ai_model}")
        print(f"   Interval: {check_interval} seconds")
        print(f"   Max emails/check: {max_emails}")
        print(f"   Keywords: {', '.join(self.config['ai_keywords'][:5])}...")
        print("\nPress Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] Checking emails...")
                
                processed = self.process_emails(ai_provider, ai_model, max_emails)
                
                if processed > 0:
                    print(f"   {processed} email(s) processed")
                else:
                    print("   No emails with AI keywords")
                
                print(f"   Waiting {check_interval} seconds...\n")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"\nMonitoring error: {e}")