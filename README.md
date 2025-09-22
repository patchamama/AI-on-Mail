# AIOnMail

**AIOnMail** is a project that enables access to artificial intelligence models (such as OpenAI’s ChatGPT, Gemini or local Ollama instances) **using only email**. Automated email processing system using artificial intelligence. Detects emails with specific keywords, processes document attachments, and responds automatically using ChatGPT, Gemini, or Ollama.

It is designed especially for people and communities living in areas with poor Internet connectivity or without direct web access, but who still have access to email services.

## Why AIOnMail?

In many countries and regions, Internet access is limited, expensive, or unreliable. However, email remains a widely accessible and lightweight service. AIOnMail aims to reduce the digital divide by providing an alternative way to interact with AI without requiring heavy applications, modern browsers, or stable connections.

With AIOnMail, you simply send an email with your query and subject: AI and receive an AI-generated response directly in your inbox. In the background, a server processes the email, interacts with the AI model, and sends back the answer.

## Features

- **Multiple AI providers**: ChatGPT, Google Gemini, local Ollama
- **Attachment processing**: PDFs and Word documents
- **Smart filtering**: Based on customizable keywords
- **Automatic responses**: Professional AI-generated emails
- **Continuous monitoring**: Automatic inbox surveillance
- **Flexible configuration**: Environment variables and CLI arguments

## Architecture

```
ai_email_processor_project/
├── ai_email_processor/
│   ├── __init__.py              # Package initialization
│   ├── core.py                  # Main EmailAIProcessor class
│   ├── document_parser.py       # PDF/Word text extraction
│   ├── email_client.py          # IMAP/SMTP client
│   └── ai_providers.py          # AI APIs
├── .env                         # Environment variables
├── requirements.txt             # Dependencies
├── main.py                      # Main script
└── README.md                    # This documentation
```

## How does it work?
1. A server with Internet access runs the AIOnMail script.
2. The script periodically (every 5 minutes, configurable) checks a dedicated email account.
3. If it finds emails with a subject containing **“IA”** or **“artificial intelligence”**, it processes their content.
4. The email text is sent to the configured AI (OpenAI or local Ollama) to be processed and a response is generated.
5. The server (AIOnMail) generates a reply and sends it back via email to the original sender.

## Key Features
- **IMAP and SMTP support:** works with most email providers.
- **Supports OpenAI, Gemini and Ollama:** use either cloud-based or local AI models.
- **Automatic processing every 5 minutes** (adjustable).
- **Replies in the same email thread**, keeping the conversation organized.
- **Designed for low bandwidth:** only requires sending and receiving emails.

## Requirements
- Python 3.8+
- Access to an email account with IMAP and SMTP enabled.
- An OpenAI API/Gemini key **or** a local Ollama installation.

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/AIOnMail.git
cd AIOnMail

# Install dependencies
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip3 install -r requirements.txt
```

### 2. Configure environment variables

```bash
# Create configuration file
python3 main.py --create-env

# Edit .env with your credentials
nano .env  # or your preferred editor
```

## Example `.env` file:
Create a `.env` file with your credentials and configuration:
```env
# AI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here

# Optional Email Server Settings (defaults provided)
IMAP_SERVER=imap.gmail.com
POP3_SERVER=pop.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: Customize AI keywords (comma-separated)
AI_KEYWORDS=AI,IA,Artificial Intelligence,Machine Learning,ChatGPT, Bot, Inteligencia Artificial

# Default AI provider when multiple are available (optional)
# Options: chatgpt, gemini, ollama
DEFAULT_AI_PROVIDER=chatgpt
```

### API Keys
 
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Ollama**: Install locally from https://ollama.ai

### Setting Up Ollama
1. Install Ollama by following the instructions at [Ollama's official site](https://ollama.com/docs/installation).
2. Download and set up your preferred models (e.g., `llama2`, `gpt-oss:20b`, etc.) using the Ollama CLI. For example:
   ```bash
   ollama pull llama2
   ollama pull gpt-oss:20b
   ```
3. Ensure your Ollama server is running and accessible. `ollama serve` should be active.
4. You can specify the Ollama model in the script (e.g., `llama2`, `gpt-oss:20b`, etc.).    

## Execution
```bash
# Activate the virtual environment
source env/bin/activate  # On Windows use `env\Scripts\activate`
# Run the script
python3 main.py
```

The script will enter a loop, checking the inbox and automatically replying to new queries.

## Use Cases
- **Rural communities** with limited Internet access but satellite email services.
- **Humanitarian organizations** providing AI access in disconnected regions.
- **Mobile users** who prefer sending a quick email query without opening an app.

## Limitations
- Response time depends on the check interval (default: 5 minutes).
- Requires an intermediate server running the script.
- Emails must contain the configured keywords in the subject.

## Usage

### Command line

```bash
# Process emails once
python3 main.py --once

# Continuous monitoring every 5 minutes (default)
python3 main.py --monitor

# Use specific provider
python3 main.py --provider gemini --monitor

# Custom interval
python3 main.py --monitor --interval 600  # 10 minutes

# Show system information
python3 main.py --info

# Full help
python3 main.py --help
```

### Interactive mode

```bash
python3 main.py
```

Presents an interactive menu with options to:
1. Process emails once
2. Monitor continuously
3. View available providers
4. Chat with AI
5. Exit

### Programmatic usage

```python
from ai_email_processor import EmailAIProcessor

# Initialize processor
processor = EmailAIProcessor()

# Process emails once
processed = processor.process_emails(
    ai_provider="gemini",
    max_emails=5
)

# Continuous monitoring
processor.monitor_emails(
    ai_provider="chatgpt",
    check_interval=300,  # 5 minutes
    max_emails=10
)
```

## Detailed Features

### Supported AI providers

1. **ChatGPT (OpenAI)**
   - Models: gpt-3.5-turbo, gpt-4, etc.
   - Requires: `OPENAI_API_KEY`

2. **Gemini (Google)**
   - Models: gemini-1.5-flash, gemini-1.5-pro
   - Requires: `GEMINI_API_KEY`

3. **Ollama (Local)**
   - Any locally installed model
   - Requires: Ollama running on port 11434

### Document processing

- **PDFs**: Text extraction with PyPDF2 or PyMuPDF
- **Word**: .docx documents with python-docx
- **Limits**: Configurable via `MAX_DOCUMENT_SIZE`
- **Error handling**: Robust with fallbacks

### Email filtering

The system searches for these keywords by default in the email subject:
- AI, IA
- Artificial Intelligence / Inteligencia Artificial
- Machine Learning
- ChatGPT, Gemini, Ollama

Customizable via `AI_KEYWORDS` variable.

### Automatic responses

- **Professional format**: Includes original email and AI response
- **Attachment info**: Lists processed documents
- **Auto-marking**: Processed emails marked as read
- **Encoding**: Full UTF-8 and special characters support

## Development

### Code structure

- **Modular**: Each component in its own module
- **Extensible**: Easy to add new AI providers
- **Testable**: Independent components
- **Documented**: English docstrings

### Adding new AI provider

```python
# In ai_providers.py
class NewProvider(AIProvider):
    def __init__(self):
        super().__init__()
        self.name = "new"
        self.display_name = "New Provider"
        self.default_model = "default-model"
    
    def is_available(self) -> bool:
        return bool(os.getenv('NEW_API_KEY'))
    
    def query(self, prompt: str, model: str = "", **kwargs) -> Optional[str]:
        # Implement query logic
        pass
```

### Testing

```bash
# Check configuration
python3 main.py --info

# Test email connection
python3 main.py --once --max-emails 1

# Test AI providers
python3 -c "from ai_email_processor.ai_providers import get_available_providers; print([p.display_name for p in get_available_providers()])"
```

## Security

- **Secure credentials**: Environment variables only
- **File validation**: Allowed types and sizes
- **Error handling**: No sensitive information exposure
- **Timeouts**: Protection against hanging connections

## Troubleshooting

### Common issues

1. **"No AI providers configured"**
   - Check API keys in `.env`
   - For Ollama, ensure it's running

2. **"IMAP connection error"**
   - Verify email credentials
   - For Gmail, use app passwords
   - Check server configuration

3. **"Cannot extract text from PDF"**
   - Install dependencies: `pip3 install PyPDF2 pymupdf`
   - Some PDFs may be protected or image-based

4. **"No emails with keywords"**
   - Check `AI_KEYWORDS` configuration
   - Keywords are searched in email subject

5. **"SMTP send error"**
   - Verify SMTP server and port
   - Check email credentials

6. **"Rate limit exceeded" or Error in ChatGPT request: 429 Client Error: Too Many Requests for url: https://api.openai.com/v1/chat/completions**
   - For OpenAI/Gemini, check usage limits or quotas on your account
   - Maybe you are sending too many requests in a short period
   - The credits in your account may be exhausted
   - Reduce frequency of email checks
   - Use lower-capacity models if available
   - Implement backoff strategies if needed

### Diagnostic logs

The system prints detailed logs for each operation:
- OK: Successful operations
- ERROR: Errors with description
- WARNING: Warnings
- Clear operation type indicators


## Support
- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions

## TODO
- [x] Initial implementation with OpenAI and Ollama
- [x] Add Google Gemini support
- [x] Document attachment processing (PDF, Word)
- [x] Interactive CLI mode
- [x] Environment variable configuration
- [x] Email threading support
- [x] Robust error handling and logging
- [x] Unit tests for core components
- [x] Support for multiple AI providers and fallback
- [x] Email filtering based on customizable keywords
- [x] Automatic marking of processed emails as read
- [x] UTF-8 and special character support
- [ ] Implement advanced AI prompt customization
- [ ] Add more AI providers (e.g., Hugging Face, Cohere) 
- [ ] Web dashboard for configuration and monitoring
- [ ] Unit tests and CI/CD integration
- [ ] Docker containerization for easy deployment
- [ ] Rate limiting and retry logic for AI API calls
- [ ] Support for email threading and conversation history
- [ ] Implement a web interface for users to submit queries directly

## Contributing
Contributions are welcome! Feel free to open issues or pull requests to improve the project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by the need to bridge the digital divide and make AI accessible to all.
