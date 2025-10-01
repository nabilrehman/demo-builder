# Vega-Lite Chart Integration Guide

This project is now configured to render **Vega-Lite** charts from the Google Conversational Analytics API.

## What Changed

### 1. Frontend Components
- **`ChartMessage.tsx`**: Now uses `vega-embed` to render Vega-Lite specifications
- **`ChatMessage.tsx`**: Updated ChartData type to accept Vega-Lite specs
- **`Index.tsx`**: Mock charts now generate Vega-Lite format

### 2. Chart Data Format

**Old Format (Recharts)**:
```typescript
{
  type: "bar",
  title: "My Chart",
  data: [{ x: 1, y: 2 }],
  xKey: "x",
  yKey: "y"
}
```

**New Format (Vega-Lite)**:
```typescript
{
  $schema: "https://vega.github.io/schema/vega-lite/v5.json",
  title: { text: "My Chart" },
  data: {
    values: [{ x: 1, y: 2 }]
  },
  mark: { type: "bar", tooltip: true },
  encoding: {
    x: { field: "x", type: "quantitative" },
    y: { field: "y", type: "quantitative" }
  }
}
```

## Backend Integration (api.py)

The `api.py` file includes detailed comments showing how to:

1. **Extract Vega-Lite from Google API response**:
```python
from google.cloud import geminidataanalytics
from google.protobuf.json_format import MessageToDict
import proto

def convert_proto_to_dict(proto_value):
    # Converts proto messages to Python dicts
    if isinstance(proto_value, proto.marshal.collections.maps.MapComposite):
        return {k: convert_proto_to_dict(v) for k, v in proto_value.items()}
    elif isinstance(proto_value, proto.marshal.collections.RepeatedComposite):
        return [convert_proto_to_dict(el) for el in proto_value]
    elif isinstance(proto_value, (int, float, str, bool)):
        return proto_value
    else:
        return MessageToDict(proto_value)

# In your API endpoint:
for reply in stream:
    if "chart" in reply.system_message:
        if "result" in reply.system_message.chart:
            vega_config = convert_proto_to_dict(
                reply.system_message.chart.result.vega_config
            )
            # Return this to frontend
            chart_data = vega_config
```

2. **Return to frontend**:
```python
return ChatResponse(
    response=response_text,
    chartData=chart_data,  # Vega-Lite spec
    sqlQuery=sql_query
)
```

## Dependencies

### Backend (`requirements.txt`):
```
fastapi
uvicorn
pydantic
google-cloud-gemini-data-analytics
google-auth
protobuf
```

### Frontend (already installed):
- `vega@5.30.0`
- `vega-lite@5.21.0`
- `vega-embed@6.26.0`

## Testing the Integration

### Current State (Mock Data)
The app currently shows mock Vega-Lite charts. Try these prompts:
- "Show me sentiment analysis" → Pie chart
- "Show conversation volume trends" → Line chart
- "Show me analytics" → Bar chart

### With Real API
Once you integrate `api.py` with your Google Conversational Analytics code:

1. The API will return real Vega-Lite specs
2. The frontend will automatically render them
3. Charts will be **publication quality** and support complex visualizations

## Advantages of Vega-Lite

✅ **Industry Standard**: Used by Tableau, Observable, Jupyter
✅ **Flexible**: Supports any chart type the AI generates
✅ **Professional**: Publication-quality graphics
✅ **Interactive**: Built-in tooltips, zoom, pan
✅ **Future-proof**: Google returns this format natively

## Next Steps

1. Copy `api.py` to your `ca-api-codelab` directory
2. Replace the TODO sections with your actual Google API calls
3. Install backend dependencies: `pip install -r requirements.txt`
4. Run the backend: `uvicorn api:app --reload`
5. The frontend will automatically work with real data!
