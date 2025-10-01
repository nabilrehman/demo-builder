import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { question } = await req.json();
    
    if (!question) {
      throw new Error('Question is required');
    }

    console.log('Processing chat request for question:', question);

    // Generate mock analytics based on the question
    const lowerQuestion = question.toLowerCase();
    let mockResponse = '';
    let chartData = null;
    let sqlQuery = '';

    // Sentiment analysis
    if (lowerQuestion.includes('sentiment') || lowerQuestion.includes('emotion')) {
      mockResponse = 'Based on the conversation data, the sentiment distribution shows mostly positive feedback from customers.';
      chartData = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Customer sentiment distribution",
        "data": {
          "name": "sentiment_data",
          "values": [
            { "category": "Positive", "value": 65 },
            { "category": "Neutral", "value": 25 },
            { "category": "Negative", "value": 10 }
          ]
        },
        "mark": "arc",
        "encoding": {
          "theta": { "field": "value", "type": "quantitative" },
          "color": {
            "field": "category",
            "type": "nominal",
            "scale": {
              "domain": ["Positive", "Neutral", "Negative"],
              "range": ["#22c55e", "#3b82f6", "#ef4444"]
            }
          },
          "tooltip": [
            { "field": "category", "type": "nominal", "title": "Sentiment" },
            { "field": "value", "type": "quantitative", "title": "Count" }
          ]
        },
        "title": {
          "text": "Customer Sentiment Distribution",
          "fontSize": 16
        }
      };
      sqlQuery = 'SELECT sentiment, COUNT(*) as count FROM conversations GROUP BY sentiment';
    }
    // Volume/Traffic analysis
    else if (lowerQuestion.includes('volume') || lowerQuestion.includes('traffic') || lowerQuestion.includes('trend')) {
      mockResponse = 'Conversation volume has been trending upward this week, with peak activity on Friday.';
      chartData = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Conversation volume trends",
        "data": {
          "name": "volume_data",
          "values": [
            { "day": "Monday", "conversations": 120 },
            { "day": "Tuesday", "conversations": 185 },
            { "day": "Wednesday", "conversations": 210 },
            { "day": "Thursday", "conversations": 195 },
            { "day": "Friday", "conversations": 240 },
            { "day": "Saturday", "conversations": 160 },
            { "day": "Sunday", "conversations": 145 }
          ]
        },
        "mark": {
          "type": "line",
          "point": true,
          "tooltip": true
        },
        "encoding": {
          "x": {
            "field": "day",
            "type": "ordinal",
            "axis": { "title": "Day of Week", "labelAngle": 0 }
          },
          "y": {
            "field": "conversations",
            "type": "quantitative",
            "axis": { "title": "Number of Conversations" }
          },
          "color": { "value": "#6366f1" }
        },
        "title": {
          "text": "Conversation Volume Over Time",
          "fontSize": 16
        }
      };
      sqlQuery = 'SELECT DATE(created_at) as date, COUNT(*) as conversations FROM conversations GROUP BY date ORDER BY date';
    }
    // Topic analysis
    else if (lowerQuestion.includes('topic') || lowerQuestion.includes('category') || lowerQuestion.includes('issue')) {
      mockResponse = 'The most common conversation topics are Support queries, followed by Billing and Feature requests.';
      chartData = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Top conversation topics",
        "data": {
          "name": "topics_data",
          "values": [
            { "topic": "Support", "count": 230 },
            { "topic": "Features", "count": 180 },
            { "topic": "Billing", "count": 145 },
            { "topic": "General", "count": 160 },
            { "topic": "Technical", "count": 95 }
          ]
        },
        "mark": {
          "type": "bar",
          "tooltip": true
        },
        "encoding": {
          "x": {
            "field": "topic",
            "type": "nominal",
            "axis": { "title": "Topic Category", "labelAngle": 0 }
          },
          "y": {
            "field": "count",
            "type": "quantitative",
            "axis": { "title": "Number of Conversations" }
          },
          "color": { "value": "#6366f1" }
        },
        "title": {
          "text": "Top Conversation Topics",
          "fontSize": 16
        }
      };
      sqlQuery = 'SELECT topic, COUNT(*) as count FROM conversations GROUP BY topic ORDER BY count DESC LIMIT 5';
    }
    // Default response
    else {
      mockResponse = 'I can help you analyze conversation data. Try asking about sentiment, volume trends, or common topics.';
    }

    console.log('Generated chart data:', chartData);
    console.log('Generated SQL query:', sqlQuery);

    const responseText = `${mockResponse} This analysis is based on mock data for demonstration purposes.`;

    console.log('Response generated successfully');

    return new Response(
      JSON.stringify({
        success: true,
        response: responseText,
        chartData,
        sqlQuery,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );

  } catch (error) {
    console.error('Error in chat-analytics function:', error);
    return new Response(
      JSON.stringify({ 
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error' 
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
});
