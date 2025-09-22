"""
Email Client Module

This module handles all email operations including IMAP/POP3 for reading emails
and SMTP for sending responses.
"""

    
import imaplib
import smtplib
import email
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import Optional, List, Dict, Any, Tuple


class EmailClient:
    """Client for email handling via IMAP/SMTP"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email client
        
        Args:
            config (Dict): Email configuration with keys:
                - imap_server, smtp_server, smtp_port
                - email, password
        """
        self.config = config
        self.imap_connection = None
        
        # Keywords for filtering AI emails
        self.ai_keywords = config.get('ai_keywords', [
            'AI', 'ai', 'IA', 'ia',
            'Artificial Intelligence', 'artificial intelligence',
            'Inteligencia Artificial', 'inteligencia artificial',
            'Machine Learning', 'machine learning',
            'ChatGPT', 'chatgpt', 'GPT', 'gpt'
        ])
    
    def is_configured(self) -> bool:
        """Check if client is properly configured"""
        required_keys = ['email', 'password', 'imap_server', 'smtp_server']
        return all(self.config.get(key) for key in required_keys)
    
    def decode_subject(self, subject: str) -> str:
        """
        Decode email subject with special characters
        
        Args:
            subject (str): Raw email subject
            
        Returns:
            str: Decoded subject
        """
        try:
            decoded = decode_header(subject)
            subject_parts = []
            for part, encoding in decoded:
                if isinstance(part, bytes):
                    if encoding:
                        subject_parts.append(part.decode(encoding))
                    else:
                        subject_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    subject_parts.append(part)
            return ''.join(subject_parts)
        except:
            return subject
    
    def has_ai_keywords(self, subject: str) -> bool:
        """
        Check if subject contains AI-related keywords
        
        Args:
            subject (str): Email subject
            
        Returns:
            bool: True if contains AI keywords
        """
        subject_lower = subject.lower()
        return any(keyword.lower() in subject_lower for keyword in self.ai_keywords)
    
    def get_email_body(self, msg) -> str:
        """
        Extract text body from email message
        
        Args:
            msg: Email message object
            
        Returns:
            str: Plain text email body
        """
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                        except:
                            continue
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(msg.get_payload())
        except Exception as e:
            print(f"Error extracting email body: {e}")
            
        return body.strip()
    
    def connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Establish IMAP connection
        
        Returns:
            IMAP connection or None if error
        """
        try:
            mail = imaplib.IMAP4_SSL(self.config['imap_server'])
            mail.login(self.config['email'], self.config['password'])
            mail.select('INBOX')
            return mail
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return None
    
    def search_unread_emails(self, mail) -> List[bytes]:
        """
        Search for unread emails
        
        Args:
            mail: Active IMAP connection
            
        Returns:
            List[bytes]: List of unread email IDs
        """
        try:
            status, messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                return messages[0].split()
            return []
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def fetch_email(self, mail, email_id: bytes) -> Optional[email.message.EmailMessage]:
        """
        Fetch specific email by ID
        
        Args:
            mail: Active IMAP connection
            email_id (bytes): Email ID to fetch
            
        Returns:
            Email message or None if error
        """
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status == 'OK':
                return email.message_from_bytes(msg_data[0][1])
            return None
        except Exception as e:
            print(f"Error fetching email {email_id}: {e}")
            return None
    
    def mark_as_read(self, mail, email_id: bytes) -> bool:
        """
        Mark email as read
        
        Args:
            mail: Active IMAP connection
            email_id (bytes): Email ID
            
        Returns:
            bool: True if marked successfully
        """
        try:
            mail.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False
    
    def extract_sender_email(self, from_field: str) -> str:
        """
        Extract email address from From field
        
        Args:
            from_field (str): Email From field
            
        Returns:
            str: Clean email address
        """
        sender_match = re.search(r'<(.+?)>', from_field)
        if sender_match:
            return sender_match.group(1)
        return from_field.strip()
    
    def send_response(self, to_email: str, original_subject: str, 
                     original_body: str, ai_response: str,
                     attachments_info: List[Dict[str, Any]] = None) -> bool:
        """
        Send automatic response with AI answer
        
        Args:
            to_email (str): Recipient
            original_subject (str): Original subject
            original_body (str): Original email body
            ai_response (str): AI-generated response
            attachments_info (List[Dict]): Processed attachments info
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to_email
            msg['Subject'] = f"AI Response: {original_subject}"
            
            # Email body
            email_body = self._format_response_body(
                original_body, ai_response, attachments_info
            )
            
            msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            
            # Connect to SMTP
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.config['email'], to_email, text)
            server.quit()
            
            print(f"Response sent to: {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending response: {e}")
            return False
    
    def _format_response_body(self, original_body: str, ai_response: str, 
                             attachments_info: List[Dict[str, Any]] = None) -> str:
        """
        Format automatic response body
        
        Args:
            original_body (str): Original body
            ai_response (str): AI response
            attachments_info (List[Dict]): Attachments info
            
        Returns:
            str: Formatted response body
        """
        # Processed attachments info
        attachments_section = ""
        if attachments_info:
            attachments_section = "\nProcessed documents:\n"
            for att in attachments_info:
                attachments_section += f"   • {att['filename']} ({att['type'].upper()}, {att['size']} characters)\n"
        
        email_body = f"""AI AUTOMATED RESPONSE
{'=' * 50}

Original Message:
{original_body[:500]}{'...' if len(original_body) > 500 else ''}
{attachments_section}
AI Response:
{ai_response}

{'-' * 50}
This response was generated automatically by an AI assistant.
If you need further assistance, please reply to this email.

System: AI Email Processor v2.0 
Generated with: AIOnMail - https://github.com/your-repo/AIOnMail 
        """.strip()
        
        return email_body
    
    def close_connection(self, mail):
        """
        Close IMAP connection safely
        
        Args:
            mail: IMAP connection to close
        """
        try:
            if mail:
                mail.close()
                mail.logout()
        except:
            pass