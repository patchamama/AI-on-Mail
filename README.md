# AIOnMail

AIOnMail is a project that enables access to artificial intelligence models (such as OpenAI’s ChatGPT or local Ollama instances) **using only email**. It is designed especially for people and communities living in areas with poor Internet connectivity or without direct web access, but who still have access to email services.

## Why AIOnMail?
In many countries and regions, Internet access is limited, expensive, or unreliable. However, email remains a widely accessible and lightweight service. AIOnMail aims to reduce the digital divide by providing an alternative way to interact with AI without requiring heavy applications, modern browsers, or stable connections.

With AIOnMail, you simply send an email with your query and receive an AI-generated response directly in your inbox.

## How does it work?
1. A server with Internet access runs the AIOnMail script.
2. The script periodically (every 15 minutes, configurable) checks a dedicated email account.
3. If it finds emails with a subject containing **“IA”** or **“artificial intelligence”**, it processes their content.
4. The email text is sent to the configured AI (OpenAI or local Ollama).
5. The server generates a reply and sends it back via email to the original sender.

## Key Features
- **IMAP and SMTP support:** works with most email providers.
- **Supports OpenAI and Ollama:** use either cloud-based or local AI models.
- **Automatic processing every 15 minutes** (adjustable).
- **Replies in the same email thread**, keeping the conversation organized.
- **Designed for low bandwidth:** only requires sending and receiving emails.

## Requirements
- Python 3.8+
- Access to an email account with IMAP and SMTP enabled.
- An OpenAI API key **or** a local Ollama installation.

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/AIOnMail.git
cd AIOnMail

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Create a `.env` file with your credentials and configuration:
```env
IMAP_HOST=imap.example.com
IMAP_PORT=993
IMAP_USER=user@example.com
IMAP_PASS=password

SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=user@example.com
SMTP_PASS=password

AI_MODE=openai  # or "ollama"
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# For local Ollama
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Execution
```bash
python AIOnMail.py
```

The script will enter a loop, checking the inbox and automatically replying to new queries.

## Use Cases
- **Rural communities** with limited Internet access but satellite email services.
- **Humanitarian organizations** providing AI access in disconnected regions.
- **Mobile users** who prefer sending a quick email query without opening an app.

## Limitations
- Response time depends on the check interval (default: 15 minutes).
- Requires an intermediate server running the script.
- Emails must contain the configured keywords in the subject.

## Contributing
Contributions are welcome! Feel free to open issues or pull requests to improve the project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by the need to bridge the digital divide and make AI accessible to all.
