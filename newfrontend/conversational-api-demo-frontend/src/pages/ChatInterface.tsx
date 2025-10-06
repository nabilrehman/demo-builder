import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2, Database, Code, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  chartData?: any;
}

interface GoldenQuery {
  id: string;
  question: string;
  sql: string;
  businessValue: string;
  complexity: string;
}

const ChatInterface = () => {
  const [searchParams] = useSearchParams();
  const datasetId = searchParams.get('dataset_id');
  const agentId = searchParams.get('agent_id');
  const jobId = searchParams.get('job_id');

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [goldenQueries, setGoldenQueries] = useState<GoldenQuery[]>([]);
  const [loadingQueries, setLoadingQueries] = useState(false);

  // Fetch golden queries on mount if job_id is provided
  useEffect(() => {
    const fetchGoldenQueries = async () => {
      if (!jobId) return;

      setLoadingQueries(true);
      try {
        const response = await fetch(`/api/provision/assets/${jobId}`);
        if (response.ok) {
          const data = await response.json();
          setGoldenQueries(data.golden_queries || []);
        }
      } catch (err) {
        console.error('Failed to fetch golden queries:', err);
      } finally {
        setLoadingQueries(false);
      }
    };

    fetchGoldenQueries();
  }, [jobId]);

  const handleQueryClick = (question: string) => {
    setInput(question);
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: textToSend
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          dataset_id: datasetId,
          agent_id: agentId
        })
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response || 'No response',
        sql: data.sqlQuery,
        chartData: data.chartData
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      toast.error('Failed to get response from chat API');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-5xl mx-auto space-y-4">
        {/* Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Conversational Analytics Chat
              </CardTitle>
              <div className="text-sm text-gray-600">
                Dataset: <code className="bg-gray-100 px-2 py-1 rounded">{datasetId || 'N/A'}</code>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Chat Messages */}
        <Card className="h-[600px] flex flex-col">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-400 text-lg mb-6">👋 Start asking questions about your data...</p>

                  {/* Golden Query Suggestions */}
                  {loadingQueries ? (
                    <div className="flex justify-center items-center gap-2 text-gray-400">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Loading suggested queries...</span>
                    </div>
                  ) : goldenQueries.length > 0 ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-center gap-2 text-indigo-600 font-semibold mb-4">
                        <Sparkles className="h-5 w-5" />
                        <span>Suggested Questions</span>
                      </div>
                      <div className="flex flex-wrap gap-3 justify-center max-w-3xl mx-auto">
                        {goldenQueries.map((query, idx) => (
                          <button
                            key={query.id || idx}
                            onClick={() => handleQueryClick(query.question)}
                            className="group relative px-4 py-3 bg-white border-2 border-indigo-200 hover:border-indigo-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 text-left max-w-md"
                          >
                            <div className="flex items-start gap-2">
                              <Sparkles className="h-4 w-4 text-indigo-500 mt-1 flex-shrink-0" />
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-800 group-hover:text-indigo-600 transition-colors">
                                  {query.question}
                                </p>
                                {query.businessValue && (
                                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                    {query.businessValue}
                                  </p>
                                )}
                              </div>
                              <div className="text-xs px-2 py-1 bg-indigo-50 text-indigo-600 rounded-md font-semibold">
                                {query.complexity}
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                      <p className="text-xs text-gray-400 mt-4">
                        💡 Click a suggestion above or type your own question below
                      </p>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 space-y-1">
                      <p>Example: "What is the total revenue?"</p>
                      <p>Example: "Show me top 10 customers by orders"</p>
                      <p>Example: "What are the sales trends by month?"</p>
                    </div>
                  )}
                </div>
              )}

              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white border shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {msg.sql && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-gray-600">
                          <Code className="h-3 w-3" />
                          Generated SQL
                        </div>
                        <pre className="p-3 bg-gray-50 rounded text-xs overflow-x-auto font-mono text-gray-800">
                          {msg.sql}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <CardContent className="border-t p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your data..."
                disabled={loading}
                className="flex-1"
              />
              <Button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                size="lg"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {!datasetId && (
              <p className="text-sm text-amber-600 mt-2">
                ⚠️ No dataset ID provided. Chat may not work correctly.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatInterface;
