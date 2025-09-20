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
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip3 install -r requirements.txt
```

## Configuration
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
# AI_KEYWORDS=AI,IA,Artificial Intelligence,Machine Learning,ChatGPT, Bot, Inteligencia Artificial
```

### API Keys

For OpenAI, you can use models like `gpt-3.5-turbo` or `gpt-4`. For Gemini, ensure you have access to the appropriate model as per your subscription level but for basic usage, the default settings should suffice and work well with the gratis tier.

To generate an Api key for OpenAI, visit [OpenAI's API page](https://platform.openai.com/account/api-keys).
To generate an Api key for Gemini, visit [Gemini's API page](https://makersuite.google.com/app/apikey).

## Execution
```bash
# Activate the virtual environment
source env/bin/activate  # On Windows use `env\Scripts\activate`
# Run the script
python3 AIOnMail.py
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
