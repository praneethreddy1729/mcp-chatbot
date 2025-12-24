# Customer Support Chatbot (MCP Demo)

A customer support chatbot prototype that integrates with a Model Context Protocol (MCP) server using Streamable HTTP transport. Built with Gradio for the UI and OpenRouter for LLM access.

## Features

- **Product Catalog**: Browse and search products by category
- **Order Management**: Create orders and view order history
- **Customer Verification**: Secure PIN-based identity verification
- **State Tracking**: Maintains customer session for consistent experience
- **Multi-step Tool Calling**: Handles complex workflows requiring multiple MCP tool calls

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Gradio    │────▶│   LLM via    │────▶│ MCP Server  │
│     UI      │◀────│  OpenRouter  │◀────│ (HTTP/JSON) │
└─────────────┘     └──────────────┘     └─────────────┘
```

- **LLM**: OpenAI GPT-4o-mini via OpenRouter
- **MCP Transport**: Streamable HTTP with JSON-RPC 2.0
- **UI**: Gradio ChatInterface

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `verify_customer_pin` | Verify customer identity with email and PIN |
| `get_customer` | Get customer details by ID |
| `list_products` | List products by category |
| `search_products` | Search products by query |
| `get_product` | Get product details by SKU |
| `create_order` | Create a new order |
| `list_orders` | List orders for a customer |
| `get_order` | Get order details by ID |

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
   
   # Edit .env and add your OPENROUTER_API_KEY

5. **Run the application**
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:7860 in your browser

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |

## Example Conversations

**Browse Products:**
```
User: find monitors
Bot: Here are the available monitors: [list of monitors]
```

**Place an Order:**
```
User: I want to buy a monitor
Bot: Please provide your email and 4-digit PIN to verify your identity.
User: john@example.com, 1234
Bot: Your identity has been verified. Which monitor would you like?
User: The 27-inch Model A
Bot: How many units would you like?
User: 2
Bot: Order created successfully! Order ID: xxx-xxx
```

## Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Push your code to the Space
3. Add `OPENROUTER_API_KEY` as a secret in Space settings

## Tech Stack

- **Python 3.10+**
- **Gradio** - Web UI framework
- **OpenAI SDK** - LLM client (via OpenRouter)
- **httpx** - HTTP client for MCP
- **python-dotenv** - Environment variable management

## License

MIT
