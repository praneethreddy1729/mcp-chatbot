import os
import json
import re
import asyncio
import gradio as gr
from dotenv import load_dotenv
import httpx
import openai

# Load environment variables
load_dotenv()

# Configuration
MCP_SERVER_URL = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-4o-mini"

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in environment variables.")

# Custom MCP Client for Streamable HTTP
class MCPClient:
    def __init__(self, url):
        self.url = url
        self.client = None
        self.request_id = 0
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
        
    async def _call(self, method, params):
        self.request_id += 1
        response = await self.client.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def list_tools(self):
        result = await self._call("tools/list", {})
        if "result" in result and "tools" in result["result"]:
            return result["result"]["tools"]
        return []
    
    async def call_tool(self, name, arguments):
        result = await self._call("tools/call", {
            "name": name,
            "arguments": arguments
        })
        return result.get("result", {})


# Initialize OpenAI Client (via OpenRouter)
client = openai.AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


# Session state to track verified customer
class SessionState:
    def __init__(self):
        self.customer_id = None
        self.customer_name = None
        self.customer_email = None
    
    def extract_customer_id(self, tool_result):
        """Extract customer_id from verify_customer_pin result."""
        if isinstance(tool_result, dict) and "content" in tool_result:
            for content in tool_result["content"]:
                if content.get("type") == "text":
                    text = content.get("text", "")
                    match = re.search(r'Customer ID:\s*([a-f0-9-]{36})', text)
                    if match:
                        self.customer_id = match.group(1)
                        return self.customer_id
        return None
    
    def clear(self):
        self.customer_id = None
        self.customer_name = None
        self.customer_email = None


async def interact_with_agent(message, history, state):
    """Main interaction function with state tracking."""
    try:
        async with MCPClient(MCP_SERVER_URL) as mcp:
            try:
                tools_list = await mcp.list_tools()
            except Exception as e:
                return f"Connection Failed: {e}"

            tools = []
            for tool in tools_list:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["inputSchema"]
                    }
                })
            
            # System prompt
            system_content = """You are a helpful customer support chatbot for a computer products store.

WORKFLOW:
1. When customer wants to order or view orders, first ask for email and 4-digit PIN
2. Call verify_customer_pin with their email and PIN
3. After verification, proceed with their request using create_order or list_orders

PRIVACY:
- Say "Your identity has been verified" instead of showing internal IDs
- Present information in a user-friendly way"""

            if state.customer_id:
                system_content += f"\n\nIMPORTANT: Customer is already verified. Use customer_id: {state.customer_id} for all operations."
            
            messages = [{"role": "system", "content": system_content}]
            
            for item in history:
                if isinstance(item, dict):
                    messages.append(item)
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    user_msg, bot_msg = item
                    if user_msg:
                        messages.append({"role": "user", "content": user_msg})
                    if bot_msg:
                        messages.append({"role": "assistant", "content": bot_msg})
            
            messages.append({"role": "user", "content": message})

            # Call LLM in a loop until we get a final text response
            max_iterations = 10
            
            for iteration in range(max_iterations):
                response = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=tools,
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message)
                
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Inject verified customer_id if available
                        if state.customer_id and tool_name in ["list_orders", "create_order", "get_customer"]:
                            if "customer_id" in tool_args:
                                tool_args["customer_id"] = state.customer_id
                        
                        result = await mcp.call_tool(tool_name, tool_args)
                        
                        # Extract customer_id from verify_customer_pin
                        if tool_name == "verify_customer_pin":
                            state.extract_customer_id(result)
                        
                        tool_output = json.dumps(result) 
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_output
                        })
                else:
                    final_content = assistant_message.content
                    return final_content if final_content else "I apologize, I couldn't generate a response. Please try again."
            
            return "I apologize, the request took too many steps. Please try a simpler query."

    except Exception as e:
        return f"System Error: {str(e)}"


# Session state instance
session_state = SessionState()

async def chat_wrapper(message, history):
    return await interact_with_agent(message, history, session_state)


# Gradio UI
demo = gr.ChatInterface(
    fn=chat_wrapper,
    title="Customer Support Chatbot (MCP Demo)",
    description="Ask about products, orders, or your account. Try 'Where is my order?' or 'List monitors'.",
    examples=[
        "find monitors",
        "what is the status of my last order?",
        "create an order for a monitor"
    ]
)

if __name__ == "__main__":
    demo.launch()
