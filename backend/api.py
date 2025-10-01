import os
import uuid
from fastapi import FastAPI
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

# --- FastAPI App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https://.*-cs-300251561534-default.cs-us-central1-pits.cloudshell.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# --- Data Agent ---
def create_data_agent():
    """Creates a data agent if it doesn't already exist."""
    client = geminidataanalytics.DataAgentServiceClient()

    published_context = geminidataanalytics.Context()
    published_context.system_instruction = system_instruction

    agent = geminidataanalytics.DataAgent()
    agent.data_analytics_agent.published_context = published_context
    agent.display_name = display_name
    agent.data_analytics_agent.datasource_references = [
        geminidataanalytics.DataAnalyticsAgent.DatasourceReference(
            bigquery_datasource=geminidataanalytics.BigQueryDatasource(
                dataset=f"projects/{billing_project}/datasets/{dataset_id}",
                table=f"projects/{billing_project}/datasets/{dataset_id}/tables/{table_name}"
            )
        ) for table_name in table_names
    ]


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

    frontend_chart_data = {
        "type": "bar",  # Default to bar, can be inferred from mark type if needed
        "title": vega_spec.get("title", {}).get("text", "Chart"),
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

    return aggregated_response

def stream_chat_response(question: str, conversation_id: str, data_chat_client: geminidataanalytics.DataChatServiceClient):
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
                billing_project, location, data_agent_id
            ),
        ),
    )
    request = geminidataanalytics.ChatRequest(
        parent=f"projects/{billing_project}/locations/{location}",
        messages=messages,
        conversation_reference=conversation_reference,
    )
    return data_chat_client.chat(request=request)

# --- API Endpoints ---
@app.on_event("startup")
def startup_event():
    create_data_agent()

@app.post("/api/chat")
def chat_endpoint(chat_request: ChatRequest):
    logging.info(f'Received request: {chat_request.message}')
    data_chat_client = geminidataanalytics.DataChatServiceClient()
    conversation_id = str(uuid.uuid4())

    conversation = geminidataanalytics.Conversation()
    conversation.agents = [f'projects/{billing_project}/locations/global/dataAgents/{data_agent_id}']
    conversation.name = f"projects/{billing_project}/locations/global/conversations/{conversation_id}"

    create_conversation_request = geminidataanalytics.CreateConversationRequest(
        parent=f"projects/{billing_project}/locations/global",
        conversation_id=conversation_id,
        conversation=conversation,
    )

    data_chat_client.create_conversation(request=create_conversation_request)

    stream = stream_chat_response(chat_request.message, conversation_id, data_chat_client)
    response = process_chat_response(stream)
    logging.info(f'Sending response: {response}')
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)