
"""
Main script for AI Email Processor
System entry point
"""

import os
import argparse
from typing import Optional

from ai_email_processor.ai_providers import query_with_fallback
from ai_email_processor import __version__
from ai_email_processor.prompt_templates import PromptTemplateManager

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env")
except ImportError:
    print("python-dotenv not installed, using system variables")

# Add current directory to Python path to resolve module imports
import sys
from pathlib import Path
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from ai_email_processor import EmailAIProcessor
    from ai_email_processor.ai_providers import get_available_providers
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running the script from the project root directory")
    print("Project structure should be:")
    print("  ai_email_processor_project/")
    print("    ├── ai_email_processor/")
    print("    ├── main.py")
    print("    └── .env")
    sys.exit(1)


def create_env_template() -> bool:
    """
    Create example .env file with all necessary variables
    
    Returns:
        bool: True if created successfully
    """
    env_template = """# ================================
# AI EMAIL PROCESSOR - CONFIGURATION
# ================================

# Artificial Intelligence APIs
# Configure at least one of these options:

# OpenAI ChatGPT API
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-key-here

# Google Gemini API  
# Get your key at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-key-here

# ================================
# EMAIL CONFIGURATION
# ================================

# Your email account credentials
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Email servers (default values for Gmail)
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com  
SMTP_PORT=587

# ================================
# OPTIONAL CONFIGURATION
# ================================

# Keywords to detect AI emails (comma-separated)
AI_KEYWORDS=AI,IA,Artificial Intelligence,Inteligencia Artificial,Machine Learning,ChatGPT,Gemini,Ollama

# Maximum text size to extract from documents (characters)
MAX_DOCUMENT_SIZE=10000

# Interval between email checks (seconds)
CHECK_INTERVAL=300

# Token limits for AI responses (optional)
DEFAULT_MAX_TOKENS=2000
CHAT_MAX_TOKENS=4000
EMAIL_MAX_TOKENS=3000

# Default AI provider when multiple are available (optional)
# Options: chatgpt, gemini, ollama
DEFAULT_AI_PROVIDER=chatgpt

# Fallback system configuration (optional)
ENABLE_FALLBACK=true
FALLBACK_ORDER=chatgpt,gemini,ollama

# ================================
# WORD DOCUMENT EXPORT
# ================================

# Enable Word document generation from AI responses
ENABLE_WORD_EXPORT=true

# Directory to save Word documents
WORD_EXPORT_DIR=ai_responses

# ================================
# IMPORTANT NOTES
# ================================

# 1. For Gmail, use app passwords, not your regular password
#    Guide: https://support.google.com/accounts/answer/185833
#
# 2. Install optional dependencies for document processing:
#    pip install PyPDF2 python-docx pymupdf
#
# 3. To use local Ollama, install from: https://ollama.ai
#    No additional configuration variables needed
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_template)
        print(".env file created successfully")
        print("Edit the .env file with your actual credentials")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def get_default_provider() -> str:
    """
    Get the best available AI provider based on configuration priority
    Priority order: ChatGPT -> Gemini -> Ollama
    """
    try:
        from ai_email_processor.ai_providers import get_available_providers
        
        providers = get_available_providers()
        if not providers:
            return 'chatgpt'  # fallback
        
        # Priority order for default selection
        priority_order = ['chatgpt', 'gemini', 'ollama']
        
        for preferred in priority_order:
            for provider in providers:
                if provider.name == preferred:
                    return preferred
        
        # If none match, return first available
        return providers[0].name
    except:
        return 'chatgpt'  # safe fallback
    
    

def show_prompt_templates():
    """Show available prompt templates and their information"""
    print("=" * 60)
    print("AVAILABLE PROMPT TEMPLATES")
    print("=" * 60)
    
    try:        
        template_manager = PromptTemplateManager()
        templates_info = template_manager.list_templates()
        
        print(f"\nTotal templates: {len(templates_info)}")
        print("\nTemplate Details:")
        print("-" * 50)
        
        for template in templates_info:
            print(f"\nName: {template['name'].upper()}")
            print(f"Priority: {template['priority']}")
            print(f"Keywords ({template['keywords_count']}): {', '.join(template['sample_keywords'])}")
            if len(template['sample_keywords']) < template['keywords_count']:
                remaining = template['keywords_count'] - len(template['sample_keywords'])
                print(f"... and {remaining} more keywords")
        
        print("\nHow it works:")
        print("1. System analyzes email content for keywords")
        print("2. Selects the highest priority matching template")
        print("3. Generates specialized prompt for that content type")
        print("4. Falls back to generic template if no matches")
        
    except ImportError as e:
        print(f"Could not load template information: {e}")

def show_fallback_info():
    """Show current fallback system configuration"""
    print("\nFallback System Configuration:")
    print("-" * 40)
    
    enable_fallback = os.getenv('ENABLE_FALLBACK', 'true').lower() in ['true', '1', 'yes']
    fallback_order = os.getenv('FALLBACK_ORDER', 'chatgpt,gemini,ollama')
    
    print(f"   Fallback enabled: {enable_fallback}")
    if enable_fallback:
        print(f"   Fallback order: {fallback_order}")
        print("   If first provider fails, system will try others automatically")
    else:
        print("   Only the requested provider will be used")
    
    print("\nConfigurable via .env:")
    print("   ENABLE_FALLBACK=true")
    print("   FALLBACK_ORDER=chatgpt,gemini,ollama")
    """Show information about available providers and current selection"""
    try:
        from ai_email_processor.ai_providers import get_available_providers
        
        providers = get_available_providers()
        if not providers:
            print("No AI providers configured")
            return
        
        default_provider = get_default_provider()
        
        print("AI Provider Information:")
        print("-" * 40)
        for provider in providers:
            status = " [DEFAULT]" if provider.name == default_provider else ""
            print(f"   • {provider.display_name}{status}")
            if provider.name == 'ollama':
                try:
                    models = provider.get_models()
                    if models:
                        print(f"     Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                except:
                    pass
        
        print(f"\nDefault provider: {default_provider}")
        print("Change with --provider argument")
        
    except ImportError:
        print("Cannot load provider information")

def show_provider_selection_info():
    """Show information about available providers and current selection"""
    try:
        from ai_email_processor.ai_providers import get_available_providers
        
        providers = get_available_providers()
        if not providers:
            print("No AI providers configured")
            return
        
        default_provider = get_default_provider()
        
        print("AI Provider Information:")
        print("-" * 40)
        for provider in providers:
            status = " [DEFAULT]" if provider.name == default_provider else ""
            print(f"   • {provider.display_name}{status}")
            if provider.name == 'ollama':
                try:
                    models = provider.get_models()
                    if models:
                        print(f"     Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                except:
                    pass
        
        print(f"\nDefault provider: {default_provider}")
        print("Change with --provider argument")
        
    except ImportError:
        print("Cannot load provider information")
        
def check_configuration() -> bool:
    """
    Check if configuration is valid
    
    Returns:
        bool: True if configuration is valid
    """
    # Check email variables
    required_email_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD']
    missing_vars = []
    
    for var in required_email_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing email variables:")
        for var in missing_vars:
            print(f"   • {var}")
        return False
    
    # Check AI providers
    providers = get_available_providers()
    if not providers:
        print("No AI providers configured")
        print("   Configure at least one of:")
        print("   • OPENAI_API_KEY (ChatGPT)")
        print("   • GEMINI_API_KEY (Google Gemini)")
        print("   • Local Ollama running")
        return False
    
    print("Configuration valid")
    print(f"Email: {os.getenv('EMAIL_ADDRESS')}")
    
    # Show provider info with priorities
    show_provider_selection_info()
    
    return True


def show_system_info():
    """Show system information"""
    print("=" * 60)
    print("AI EMAIL PROCESSOR v2.0")
    print("=" * 60)
    
    # Library status
    print("\nLibrary status:")
    
    try:
        import PyPDF2
        print("   OK PyPDF2 - PDF processing")
    except ImportError:
        try:
            import fitz
            print("   OK PyMuPDF - PDF processing (better)")
        except ImportError:
            print("   ERROR No PDF support")
            print("      Install: pip install PyPDF2 or pip install pymupdf")
    
    try:
        import docx
        print("   OK python-docx - Word document processing")
    except ImportError:
        print("   ERROR No Word document support") 
        print("      Install: pip install python-docx")
    
    try:
        from dotenv import load_dotenv
        print("   OK python-dotenv - Environment variables loading")
    except ImportError:
        print("   WARNING python-dotenv not installed (optional)")
        print("      Install: pip install python-dotenv")
    
    # Show provider info
    show_provider_selection_info()
    
    # Show fallback configuration
    show_fallback_info()



def interactive_ai_chat():
    """Interactive chat mode to test AI providers"""
    print("=" * 60)
    print("AI CHAT INTERACTIVE MODE")
    print("=" * 60)
    
    try:
        from ai_email_processor.ai_providers import get_available_providers, get_provider_by_name
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the correct directory")
        return
    
    # Get available providers
    providers = get_available_providers()
    if not providers:
        print("No AI providers configured")
        print("\nConfigure at least one of:")
        print("   • OPENAI_API_KEY (ChatGPT)")
        print("   • GEMINI_API_KEY (Google Gemini)")
        print("   • Local Ollama running")
        return
    
    # Show available providers
    print("Available AI providers:")
    for i, provider in enumerate(providers, 1):
        print(f"   {i}. {provider.display_name}")
        if provider.name == 'ollama':
            try:
                models = provider.get_models()
                if models:
                    print(f"      Models: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
            except:
                pass
    
    # Select provider
    while True:
        try:
            choice = input(f"\nSelect AI provider (1-{len(providers)}): ").strip()
            provider_index = int(choice) - 1
            if 0 <= provider_index < len(providers):
                selected_provider = providers[provider_index]
                break
            else:
                print("Invalid selection")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting chat mode")
            return
    
    print(f"\nSelected: {selected_provider.display_name}")
    
    # Select model if Ollama
    selected_model = ""
    if selected_provider.name == 'ollama':
        try:
            models = selected_provider.get_models()
            if models:
                print("\nAvailable Ollama models:")
                for i, model in enumerate(models, 1):
                    print(f"   {i}. {model}")
                
                model_choice = input(f"Select model (1-{len(models)}) or press Enter for default: ").strip()
                if model_choice and model_choice.isdigit():
                    model_index = int(model_choice) - 1
                    if 0 <= model_index < len(models):
                        selected_model = models[model_index]
        except Exception as e:
            print(f"Could not get Ollama models: {e}")
    
    print(f"\nStarting chat with {selected_provider.display_name}")
    if selected_model:
        print(f"Using model: {selected_model}")
    print("Type 'quit', 'exit', or 'bye' to end chat")
    print("Type 'help' for commands")
    print("-" * 60)
    
    # Chat loop
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("Goodbye!")
                break
            
            # Help command
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("   help     - Show this help")
                print("   quit     - Exit chat")
                print("   history  - Show conversation history")
                print("   clear    - Clear conversation history")
                print("   switch   - Switch AI provider")
                print("   test     - Run predefined test")
                print("   templates - List available templates")
                continue
            
             # Templates list command
            if user_input.lower() == 'templates':
                templates = template_manager.list_templates()
                print("\nAvailable templates:")
                for template in templates:
                    print(f"   • {template['name']} (priority: {template['priority']})")
                continue
            
            # History command
            if user_input.lower() == 'history':
                if conversation_history:
                    print("\nConversation History:")
                    for i, (user_msg, ai_msg) in enumerate(conversation_history, 1):
                        print(f"   {i}. You: {user_msg[:50]}{'...' if len(user_msg) > 50 else ''}")
                        print(f"      AI: {ai_msg[:50]}{'...' if len(ai_msg) > 50 else ''}")
                else:
                    print("No conversation history")
                continue
            
            # Clear history
            if user_input.lower() == 'clear':
                conversation_history.clear()
                print("Conversation history cleared")
                continue
            
            # Switch provider
            if user_input.lower() == 'switch':
                interactive_ai_chat()  # Restart provider selection
                return
            
            # Test command
            if user_input.lower() == 'test':
                test_prompts = [
                    "Hello, how are you?",
                    "What is artificial intelligence?",
                    "Explain quantum computing in simple terms",
                    "Write a short poem about technology"
                ]
                print("\nRunning predefined tests:")
                for prompt in test_prompts:
                    print(f"\nTest: {prompt}")
                    response = selected_provider.query(prompt, model=selected_model, max_tokens=4000)
                    if response:
                        print(f"AI: {response}")
                    else:
                        print("AI: [No response]")
                continue
            
            # Query AI
            print(f"{selected_provider.display_name}: Thinking...")
            
            # Add conversation context for better responses
            context_prompt = user_input
            if conversation_history:
                # Include last 2 exchanges for context
                recent_history = conversation_history[-2:]
                context_parts = []
                for user_msg, ai_msg in recent_history:
                    context_parts.append(f"Previous - User: {user_msg}\nAI: {ai_msg}")
                context_prompt = "\n".join(context_parts) + f"\n\nCurrent question: {user_input}"
                
                
            # Initialize prompt template manager
            template_manager = PromptTemplateManager()

            # Use template manager to create specialized prompt
            specialized_prompt = template_manager.generate_prompt(context_prompt)
            
            # Detect which template was used for display
            content_type, _ = template_manager.detect_content_type(user_input)
            last_template_used = content_type
            
            # Use fallback system with the selected provider as preferred
            ai_result = query_with_fallback(
                prompt=specialized_prompt, #context_prompt,
                preferred_provider=selected_provider.name,
                model=selected_model,
                max_tokens=os.getenv('CHAT_MAX_TOKENS',  4000) 
            )
            
            if ai_result['response']:
                response = ai_result['response']
                provider_used = ai_result['provider_used']
                
                # Show which provider was actually used
                if provider_used != selected_provider.name:
                    print(f"Note: Used {provider_used} (fallback from {selected_provider.name})")
                
                # print(f"{provider_used.upper()}: {response}")
                conversation_history.append((user_input, response))
                
                # Limit history size
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
            else:
                print("Sorry, all AI providers failed:")
                for error in ai_result['errors']:
                    print(f"  - {error}")
                print("Please try again or check your API configurations")
            
            # # Add conversation context for better responses
            # context_prompt = user_input
            # if conversation_history:
            #     # Include last 2 exchanges for context
            #     recent_history = conversation_history[-2:]
            #     context_parts = []
            #     for user_msg, ai_msg in recent_history:
            #         context_parts.append(f"Previous - User: {user_msg}\nAI: {ai_msg}")
            #     context_prompt = "\n".join(context_parts) + f"\n\nCurrent question: {user_input}"
            
            # # print(f"Context:\n{context_prompt}\n")
            
            # response = selected_provider.query(context_prompt, model=selected_model)
            
            # if response:
            #     print(f"{selected_provider.display_name}: {response}")
            #     conversation_history.append((user_input, response))
                
            #     # Limit history size
            #     if len(conversation_history) > 10:
            #         conversation_history = conversation_history[-10:]
            # else:
            #     print(f"{selected_provider.display_name}: Sorry, I couldn't generate a response.")
        except KeyboardInterrupt:
            print("\n\nChat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error during chat: {e}")
            continue


def test_ai_providers():
    """Test all available AI providers with sample questions"""
    print("=" * 60)
    print("TESTING ALL AI PROVIDERS")
    print("=" * 60)
    
    try:
        from ai_email_processor.ai_providers import get_available_providers
    except ImportError as e:
        print(f"Import error: {e}")
        return
    
    providers = get_available_providers()
    if not providers:
        print("No AI providers configured")
        return
    
    test_questions = [
        "What is artificial intelligence?",
        "Explain machine learning in simple terms",
        "List 3 benefits of automation"
    ]
    
    for provider in providers:
        print(f"\nTesting {provider.display_name}")
        print("-" * 40)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\nTest {i}: {question}")
            try:
                response = provider.query(question, max_tokens=4000)
                if response:
                    # Truncate long responses for testing
                    display_response = response[:300] + "..." if len(response) > 300 else response
                    print(f"Response: {display_response}")
                else:
                    print("Response: [No response received]")
            except Exception as e:
                print(f"Error: {e}")
        
        print("-" * 40)
        
def main():
    """Main function"""
            
    parser = argparse.ArgumentParser(
        description="AI Email Processor - Automated email processing with AI"
    )
    parser.add_argument(
        '--provider', 
        choices=['chatgpt', 'gemini', 'ollama'],
        default=os.getenv('DEFAULT_AI_PROVIDER', 'chatgpt'),
        help='AI provider to use (default: chatgpt, configurable via DEFAULT_AI_PROVIDER env var)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='',
        help='Specific model to use (optional)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Process emails once and exit'
    )
    parser.add_argument(
        '--monitor',
        action='store_true', 
        help='Monitor emails continuously'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Interval between checks in seconds (default: 300)'
    )
    parser.add_argument(
        '--max-emails',
        type=int,
        default=10,
        help='Maximum number of emails per check (default: 10)'
    )
    parser.add_argument(
        '--create-env',
        action='store_true',
        help='Create example .env file'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information'
    )
    
    
    
    args = parser.parse_args()
    
    # Show system information
    if args.info:
        show_system_info()
        return
    
    # Create .env file
    if args.create_env:
        create_env_template()
        return
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("No .env file found")
        create_choice = input("Create example .env file? (y/n): ").strip().lower()
        if create_choice in ['y', 'yes']:
            if create_env_template():
                print("\nEdit the .env file and run the script again")
                return
        else:
            print("Continuing with system environment variables...")
    
    # Check configuration
    if not check_configuration():
        print("\nHelp:")
        print("   • Run --create-env to create configuration template")
        print("   • Run --info to check system status")
        return
    
    try:
        # Initialize processor
        processor = EmailAIProcessor()
        
        # Execution mode
        if args.once:
            print(f"\nProcessing emails once...")
            processed = processor.process_emails(
                ai_provider=args.provider,
                ai_model=args.model, 
                max_emails=args.max_emails
            )
            print(f"Processing completed: {processed} emails processed")
            
        elif args.monitor:
            processor.monitor_emails(
                ai_provider=args.provider,
                ai_model=args.model,
                check_interval=args.interval,
                max_emails=args.max_emails
            )
        
        else:
            # Interactive mode by default
            print(f"\n\nVersion: {__version__}")
            print(f"\nINTERACTIVE MODE")
            print("Available options:")
            print("1. Process emails once")
            print("2. Monitor emails continuously") 
            print("3. Show available providers")
            print("4. Start interactive AI chat")
            print("5. Exit")

            while True:
                try:
                    choice = input("\nSelect an option (1-5): ").strip()
                    
                    if choice == '1':
                        processed = processor.process_emails(
                            ai_provider=args.provider,
                            max_emails=args.max_emails
                        )
                        print(f"{processed} emails processed")
                        
                    elif choice == '2':
                        processor.monitor_emails(
                            ai_provider=args.provider,
                            check_interval=args.interval,
                            max_emails=args.max_emails
                        )
                        break
                        
                    elif choice == '3':
                        providers = processor.get_available_ai_providers()
                        print("\nAvailable AI providers:")
                        for provider in providers:
                            print(f"   • {provider['display_name']}")
                            
                    elif choice == '4':
                        interactive_ai_chat()
                        break
                            
                    elif choice == '5':
                        print("Goodbye!")
                        break
                        
                    else:
                        print("Invalid option")
                        
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
    
    except Exception as e:
        print(f"Critical error: {e}")
        print("\nTips:")
        print("   • Check your email configuration")
        print("   • Ensure AI providers are available")
        print("   • Run --info for system diagnosis")


if __name__ == "__main__":
    main()
    