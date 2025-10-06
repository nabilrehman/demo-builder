import os
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import geminidataanalytics
import proto

# --- Configuration ---
location = "global"
billing_project = os.environ.get('DEVSHELL_PROJECT_ID')
if not billing_project:
    billing_project = "bq-demos-469816"
data_agent_id = os.environ.get('DATA_AGENT_ID', 'default_agent')
dataset_id = os.environ.get('DATASET_ID', 'leagueapps_demo')
default_table_names = [
    "facilities", "organizations", "payments", "programs", "registrations",
    "roles", "schedule", "team_members", "teams", "user_roles", "users"
]
table_names_str = os.environ.get('TABLE_NAMES', ','.join(default_table_names))
table_names = table_names_str.split(',')
system_instruction = os.environ.get('SYSTEM_INSTRUCTION', 'You are a helpful assistant for a sports organization.')
display_name = os.environ.get('DISPLAY_NAME', 'Default Demo Agent')

import logging

# --- Logging ---
logging.basicConfig(filename='backend.log', level=logging.INFO)

from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# --- Absolute Path Configuration for Static Files ---
# The root of the application in the container is the directory where this file lives.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# In Docker container: /app/api.py → FRONTEND_DIST_DIR = /app/newfrontend/...
# Locally: .../backend/api.py → FRONTEND_DIST_DIR = .../backend/newfrontend/... (fallback to parent)
# Try container path first, then fall back to local development path
if os.path.exists(os.path.join(APP_ROOT, "newfrontend", "conversational-api-demo-frontend", "dist")):
    # Docker container structure
    FRONTEND_DIST_DIR = os.path.join(APP_ROOT, "newfrontend", "conversational-api-demo-frontend", "dist")
else:
    # Local development structure (go up one level from backend/)
    PROJECT_ROOT = os.path.dirname(APP_ROOT)
    FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "newfrontend", "conversational-api-demo-frontend", "dist")

# --- FastAPI App ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Provisioning API Routes ---
from routes.provisioning import router as provisioning_router
app.include_router(provisioning_router)

# --- Serve Frontend (MUST COME LAST) ---
# Serve the static assets from the React build directory
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")), name="assets")


class ChatRequest(BaseModel):
    message: str
    dataset_id: str | None = None  # Optional: use provisioned dataset
    agent_id: str | None = None    # Optional: use provisioned agent

# --- Data Agent ---
def create_data_agent():
    """Creates a data agent if it doesn't already exist."""
    client = geminidataanalytics.DataAgentServiceClient()

    published_context = geminidataanalytics.Context()
    published_context.system_instruction = system_instruction

    agent = geminidataanalytics.DataAgent()
    agent.data_analytics_agent.published_context = published_context
    agent.display_name = display_name
    # Build the list of table references as dictionaries
    table_references = [
        {"project_id": billing_project, "dataset_id": dataset_id, "table_id": table_name}
        for table_name in table_names
    ]

    # Create the datasource_references dictionary in the correct structure
    datasource_references = {"bq": {"table_references": table_references}}

    # Assign this dictionary to the agent's published context
    agent.data_analytics_agent.published_context.datasource_references = datasource_references


    try:
        request = geminidataanalytics.CreateDataAgentRequest(
            parent=f"projects/{billing_project}/locations/{location}",
            data_agent_id=data_agent_id,
            data_agent=agent,
        )
        client.create_data_agent(request=request)
        print(f"Data agent '{data_agent_id}' created.")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Data agent '{data_agent_id}' already exists.")
        else:
            raise e

# --- Chat Logic ---
def _transform_vega_to_frontend_chart_data(vega_spec):
    """Transforms a Vega-Lite spec into the frontend's expected chartData format."""
    if not vega_spec or "data" not in vega_spec or "values" not in vega_spec["data"]:
        return None

    # Handle title - it can be a string or a dict
    title_value = vega_spec.get("title", "Chart")
    if isinstance(title_value, dict):
        title_value = title_value.get("text", "Chart")
    elif not isinstance(title_value, str):
        title_value = "Chart"

    frontend_chart_data = {
        "type": "bar",  # Default to bar, can be inferred from mark type if needed
        "title": title_value,
        "data": vega_spec["data"]["values"],
        "xKey": None,
        "yKey": None,
        "nameKey": None,
    }

    # Infer chart type and keys from Vega-Lite encoding
    if "mark" in vega_spec and isinstance(vega_spec["mark"], dict):
        if vega_spec["mark"].get("type") == "line":
            frontend_chart_data["type"] = "line"
        elif vega_spec["mark"].get("type") == "arc": # For pie charts
            frontend_chart_data["type"] = "pie"

    if "encoding" in vega_spec:
        encoding = vega_spec["encoding"]
        if "x" in encoding and "field" in encoding["x"]:
            frontend_chart_data["xKey"] = encoding["x"]["field"]
        if "y" in encoding and "field" in encoding["y"]:
            frontend_chart_data["yKey"] = encoding["y"]["field"]
        if "theta" in encoding and "field" in encoding["theta"]:
            frontend_chart_data["yKey"] = encoding["theta"]["field"]
        if "color" in encoding and "field" in encoding["color"]:
            frontend_chart_data["nameKey"] = encoding["color"]["field"]

    return frontend_chart_data

def process_chat_response(stream):
    """Processes the chat stream and returns a single response object."""
    import re

    aggregated_response = {
        "response": "",
        "chartData": None,
        "sqlQuery": None,
    }

    for response in stream:
        m = response.system_message
        if "text" in m:
            aggregated_response["response"] += "".join(m.text.parts)
        elif "data" in m:
            if "generated_sql" in m.data:
                aggregated_response["sqlQuery"] = m.data.generated_sql
        elif "chart" in m:
            def _value_to_dict(v):
                if isinstance(v, proto.marshal.collections.maps.MapComposite):
                    return {k: _value_to_dict(v[k]) for k in v}
                elif isinstance(v, proto.marshal.collections.RepeatedComposite):
                    return [_value_to_dict(el) for el in v]
                elif isinstance(v, (str, int, float, bool)):
                    return v
                elif hasattr(v, '_pb'): # Check if it's a proto message
                    return MessageToDict(v)
                else:
                    return str(v) # Fallback for other types
            if "result" in m.chart:
                logging.info(f'Type of m.chart.result: {type(m.chart.result)}')
                logging.info(f'Value of m.chart.result: {m.chart.result}')
                logging.info(f'Type of m.chart.result.vega_config: {type(m.chart.result.vega_config)}')
                logging.info(f'Value of m.chart.result.vega_config: {m.chart.result.vega_config}')
                vega_config_dict = _value_to_dict(m.chart.result.vega_config)
                # Transform Vega-Lite to frontend's expected format
                aggregated_response["chartData"] = _transform_vega_to_frontend_chart_data(vega_config_dict)

    # Remove JSON code blocks from the response text (they're redundant since we display charts)
    if aggregated_response["response"]:
        # Remove ```json ... ``` blocks
        aggregated_response["response"] = re.sub(r'```json\s*\{.*?\}\s*```', '', aggregated_response["response"], flags=re.DOTALL)
        # Clean up any extra whitespace
        aggregated_response["response"] = re.sub(r'\n\n\n+', '\n\n', aggregated_response["response"]).strip()

    return aggregated_response

def stream_chat_response(question: str, conversation_id: str, data_chat_client: geminidataanalytics.DataChatServiceClient, agent_id: str):
    """Sends a chat request and returns the streaming response."""
    messages = [
        geminidataanalytics.Message(
            user_message=geminidataanalytics.UserMessage(text=question)
        )
    ]
    conversation_reference = geminidataanalytics.ConversationReference(
        conversation=data_chat_client.conversation_path(
            billing_project, location, conversation_id
        ),
        data_agent_context=geminidataanalytics.DataAgentContext(
            data_agent=data_chat_client.data_agent_path(
                billing_project, location, agent_id  # FIX: Use passed agent_id parameter
            ),
        ),
    )
    request = geminidataanalytics.ChatRequest(
        parent=f"projects/{billing_project}/locations/{location}",
        messages=messages,
        conversation_reference=conversation_reference,
    )
    return data_chat_client.chat(request=request, timeout=300)

# --- API Endpoints ---
@app.on_event("startup")
def startup_event():
    # Skip CAPI agent creation in local development mode
    if os.getenv('ENVIRONMENT') == 'local':
        logging.warning("⚠️  LOCAL MODE: Skipping CAPI agent creation (ADC not required)")
        logging.info("✅ Server ready for local development")
    else:
        logging.info("🔧 Creating CAPI Data Agent...")
        create_data_agent()

class BrandingRequest(BaseModel):
    websiteUrl: str

# Import Crazy Frog components
from agentic_service.models.crazy_frog_request import CrazyFrogProvisioningRequest
from agentic_service.utils.prompt_enhancer import build_crazy_frog_context_block
from agentic_service.demo_orchestrator import DemoOrchestrator

@app.post("/api/extract-branding")
def extract_branding(branding_request: BrandingRequest):
    """Extract branding information from a website URL"""
    import requests
    from urllib.parse import urlparse

    try:
        url = branding_request.websiteUrl.strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        parsed_url = urlparse(url)
        domain = parsed_url.hostname.replace('www.', '') if parsed_url.hostname else ''

        # Extract brand name from domain
        brand_name = domain.split('.')[0].replace('-', ' ').title()

        logo_url = ''
        favicon_url = f"{parsed_url.scheme}://{parsed_url.hostname}/favicon.ico"

        try:
            # Fetch the website HTML (server-side, so no CORS issues)
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.ok:
                html = response.text

                # Extract logo using regex patterns
                import re
                logo_patterns = [
                    r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
                    r'<meta\s+name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']',
                    r'<link\s+rel=["\']apple-touch-icon["\'][^>]*href=["\']([^"\']+)["\']',
                    r'<img[^>]*(?:class|id)=["\'][^"\']*logo[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                    r'<link\s+rel=["\'](?:icon|shortcut icon)["\'][^>]*href=["\']([^"\']+)["\']',
                ]

                for pattern in logo_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        extracted_url = match.group(1)
                        # Make URL absolute
                        if extracted_url.startswith('//'):
                            extracted_url = parsed_url.scheme + ':' + extracted_url
                        elif extracted_url.startswith('/'):
                            extracted_url = f"{parsed_url.scheme}://{parsed_url.hostname}{extracted_url}"
                        elif not extracted_url.startswith('http'):
                            extracted_url = f"{parsed_url.scheme}://{parsed_url.hostname}/{extracted_url}"

                        if not logo_url:
                            logo_url = extracted_url
                        if 'icon' in pattern or 'apple' in pattern:
                            favicon_url = extracted_url
                        if logo_url:
                            break
        except Exception as fetch_error:
            logging.warning(f"Could not fetch website: {fetch_error}")

        # Fallback to favicon if no logo found
        if not logo_url:
            logo_url = favicon_url

        return {
            "brandName": brand_name,
            "logoUrl": logo_url,
            "websiteUrl": url,
            "faviconUrl": favicon_url,
            "primaryColor": "#8b5cf6"
        }
    except Exception as e:
        logging.error(f"Error extracting branding: {e}")
        return {
            "error": str(e)
        }

# Crazy Frog endpoint moved to routes/provisioning.py
# Keeping this comment as a reference

@app.post("/api/chat")
def chat_endpoint(chat_request: ChatRequest):
    logging.info(f'Received request: {chat_request.message}')

    # Validate agent_id to prevent fallback when provisioning failed
    # None = not provided, use fallback OK
    # "" = explicitly empty, ERROR - CAPI agent creation failed
    if chat_request.agent_id is not None and chat_request.agent_id == "":
        raise HTTPException(
            status_code=400,
            detail="CAPI Data Agent was not created during provisioning. Check Infrastructure Agent logs for errors. Cannot use chat without a valid agent_id."
        )

    # Use provided agent_id or fall back to environment variable (for manual testing)
    active_agent_id = chat_request.agent_id or data_agent_id
    active_dataset_id = chat_request.dataset_id or dataset_id

    logging.info(f'Using agent: {active_agent_id}, dataset: {active_dataset_id}')

    try:
        data_chat_client = geminidataanalytics.DataChatServiceClient()
        conversation_id = str(uuid.uuid4())

        conversation = geminidataanalytics.Conversation()
        conversation.agents = [f'projects/{billing_project}/locations/global/dataAgents/{active_agent_id}']
        conversation.name = f"projects/{billing_project}/locations/global/conversations/{conversation_id}"

        create_conversation_request = geminidataanalytics.CreateConversationRequest(
            parent=f"projects/{billing_project}/locations/global",
            conversation_id=conversation_id,
            conversation=conversation,
        )

        data_chat_client.create_conversation(request=create_conversation_request)

        stream = stream_chat_response(chat_request.message, conversation_id, data_chat_client, active_agent_id)
        response = process_chat_response(stream)
        logging.info(f'Sending response: {response}')
        return response
    except Exception as e:
        error_message = str(e)
        logging.error(f'Error processing chat request: {error_message}')
        # Return a user-friendly error response
        return {
            "response": f"I encountered an error processing your question. The query may be too complex or have invalid syntax. Please try rephrasing your question. Error: {error_message}",
            "chartData": None,
            "sqlQuery": None
        }

# Health check endpoint
@app.get("/health")
def health():
    """Health check endpoint for local testing and Cloud Run health checks."""
    return {
        "status": "healthy",
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "timestamp": datetime.now().isoformat()
    }

# Serve the index.html for any other route (CATCH-ALL - MUST BE LAST)
# Exclude /api/ paths to prevent intercepting API routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend for all non-API routes."""
    # Don't intercept API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)