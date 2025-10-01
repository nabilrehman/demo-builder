from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# NOTE: This API uses user credentials for BigQuery authentication
# No service account required - authentication is handled via user's gcloud credentials
# Import your existing chat functionality that uses user auth
# from chat import send_message  # Make sure this uses user credentials, not service accounts

app = FastAPI()

# CORS middleware to allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    message: str
    agentId: Optional[str] = None
    conversationId: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chartData: Optional[ChartData] = None
    sqlQuery: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "BigQuery Conversational Analytics API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that integrates with Google Conversational Analytics API.
    
    Integration steps:
    1. Call your existing chat function that uses the Google API
    2. Extract Vega-Lite spec from the response
    3. Return it to the frontend
    """
    try:
        # TODO: Replace with your actual Google Conversational Analytics API integration
        # 
        # Example integration:
        # from google.cloud import geminidataanalytics
        # from google.protobuf.json_format import MessageToDict
        # import proto
        #
        # def convert_proto_to_dict(proto_value):
        #     """Helper to convert proto to dict for Vega-Lite spec"""
        #     if isinstance(proto_value, proto.marshal.collections.maps.MapComposite):
        #         return {k: convert_proto_to_dict(v) for k, v in proto_value.items()}
        #     elif isinstance(proto_value, proto.marshal.collections.RepeatedComposite):
        #         return [convert_proto_to_dict(el) for el in proto_value]
        #     elif isinstance(proto_value, (int, float, str, bool)):
        #         return proto_value
        #     else:
        #         return MessageToDict(proto_value)
        #
        # client = geminidataanalytics.DataChatServiceClient()
        # stream = client.chat(request=your_request)
        #
        # chart_data = None
        # sql_query = None
        # response_text = ""
        #
        # for reply in stream:
        #     if "chart" in reply.system_message:
        #         if "result" in reply.system_message.chart:
        #             # Extract Vega-Lite spec from the API response
        #             vega_config = convert_proto_to_dict(
        #                 reply.system_message.chart.result.vega_config
        #             )
        #             chart_data = vega_config  # Pass directly to frontend
        #         if "query" in reply.system_message.chart:
        #             sql_query = reply.system_message.chart.query
        #     if "text" in reply.system_message:
        #         response_text += reply.system_message.text
        
        # MOCK RESPONSE (remove when integrating real API)
        response_text = f"Received your message: {request.message}"
        chart_data = None
        sql_query = None
        
        return ChatResponse(
            response=response_text,
            chartData=chart_data,
            sqlQuery=sql_query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
