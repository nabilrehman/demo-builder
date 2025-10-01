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
        type: 'pie',
        title: 'Sentiment Distribution',
        data: [
          { name: 'Positive', value: 65 },
          { name: 'Neutral', value: 25 },
          { name: 'Negative', value: 10 }
        ],
        yKey: 'value',
        nameKey: 'name'
      };
      sqlQuery = 'SELECT sentiment, COUNT(*) as count FROM conversations GROUP BY sentiment';
    }
    // Volume/Traffic analysis
    else if (lowerQuestion.includes('volume') || lowerQuestion.includes('traffic') || lowerQuestion.includes('trend')) {
      mockResponse = 'Conversation volume has been trending upward this week, with peak activity on Friday.';
      chartData = {
        type: 'line',
        title: 'Conversation Volume Over Time',
        data: [
          { date: 'Mon', conversations: 120 },
          { date: 'Tue', conversations: 185 },
          { date: 'Wed', conversations: 210 },
          { date: 'Thu', conversations: 195 },
          { date: 'Fri', conversations: 240 },
          { date: 'Sat', conversations: 160 },
          { date: 'Sun', conversations: 145 }
        ],
        xKey: 'date',
        yKey: 'conversations'
      };
      sqlQuery = 'SELECT DATE(created_at) as date, COUNT(*) as conversations FROM conversations GROUP BY date ORDER BY date';
    }
    // Topic analysis
    else if (lowerQuestion.includes('topic') || lowerQuestion.includes('category') || lowerQuestion.includes('issue')) {
      mockResponse = 'The most common conversation topics are Support queries, followed by Billing and Feature requests.';
      chartData = {
        type: 'bar',
        title: 'Top Conversation Topics',
        data: [
          { topic: 'Billing', count: 145 },
          { topic: 'Support', count: 230 },
          { topic: 'Features', count: 180 },
          { topic: 'Technical', count: 95 },
          { topic: 'General', count: 160 }
        ],
        xKey: 'topic',
        yKey: 'count'
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
