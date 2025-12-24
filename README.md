# Customer Support Chatbot (MCP Demo)

A customer support chatbot that integrates with a Model Context Protocol (MCP) server using Streamable HTTP transport.

## Features

- Product catalog browsing and search
- Order creation and history
- Secure PIN-based customer verification
- Session state tracking for consistent experience

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/praneethreddy1729/mcp-chatbot.git
   cd mcp-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   
   Edit `.env` and add your `OPENROUTER_API_KEY`

5. **Run the application**
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:7860 in your browser

## Tech Stack

- **Gradio** - Web UI
- **OpenAI SDK** - LLM client (via OpenRouter)
- **httpx** - HTTP client for MCP
- **GPT-4o-mini** - LLM model

## License

MIT
