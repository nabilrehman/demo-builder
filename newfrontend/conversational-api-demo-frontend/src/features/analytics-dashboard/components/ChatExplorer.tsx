/**
 * ChatExplorer Component
 *
 * Left panel with conversational interface
 * Users ask questions and can pin responses with charts to dashboard
 */

import { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2, Pin, Database, Lightbulb } from 'lucide-react';
import { toast } from 'sonner';
import { ChatMessage as ChatMsg, ChartData, GoldenQuery } from '../types';
import { ChartMessage } from '@/components/ChartMessage';

interface ChatExplorerProps {
  datasetId: string | null;
  agentId: string | null;
  demoTitle?: string;
  goldenQueries: GoldenQuery[];
  onPinInsight: (
    question: string,
    chartData: ChartData,
    sqlQuery?: string,
    source?: 'conversation' | 'quick-insight'
  ) => void;
}

export function ChatExplorer({
  datasetId,
  agentId,
  demoTitle,
  goldenQueries,
  onPinInsight
}: ChatExplorerProps) {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage: ChatMsg = {
      role: 'user',
      content: textToSend,
      timestamp: Date.now()
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

      const assistantMessage: ChatMsg = {
        role: 'assistant',
        content: data.response || 'No response',
        chartData: data.chartData,
        sqlQuery: data.sqlQuery,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      toast.error('Failed to get response', {
        description: 'Please try again'
      });

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: Date.now()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePin = (message: ChatMsg) => {
    if (!message.chartData) return;

    // Find the user question that led to this response
    const messageIndex = messages.findIndex(m => m === message);
    const userQuestion =
      messageIndex > 0 && messages[messageIndex - 1].role === 'user'
        ? messages[messageIndex - 1].content
        : 'Insight';

    onPinInsight(userQuestion, message.chartData, message.sqlQuery, 'conversation');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Suggested questions from golden queries (show first 3)
  const suggestedQuestions = goldenQueries.slice(0, 3);

  return (
    <div className="w-[45%] flex flex-col bg-background border-r border-border">
      {/* Header */}
      <CardHeader className="border-b border-border bg-card/50 backdrop-blur-sm flex-shrink-0">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-bold text-foreground">
              {demoTitle ? `${demoTitle} Explorer` : 'Analytics Explorer'}
            </h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Ask questions about your data in natural language
          </p>
        </div>
      </CardHeader>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <Card className="border-dashed border-primary/30 bg-primary/5">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-primary">
                    <Lightbulb className="h-5 w-5" />
                    <h3 className="font-semibold">Get Started</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Try asking questions like:
                  </p>
                  <div className="space-y-2">
                    {suggestedQuestions.length > 0 ? (
                      suggestedQuestions.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(q.question)}
                          className="w-full text-left p-3 rounded-lg bg-background/80 hover:bg-background border border-border/50 hover:border-primary/30 transition-all text-sm"
                        >
                          💡 {q.question}
                        </button>
                      ))
                    ) : (
                      <>
                        <p className="text-sm text-muted-foreground">
                          • "What is the total revenue?"
                        </p>
                        <p className="text-sm text-muted-foreground">
                          • "Show me top 10 customers"
                        </p>
                        <p className="text-sm text-muted-foreground">
                          • "Revenue trends by month"
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card border border-border'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                {/* Chart visualization */}
                {msg.chartData && msg.role === 'assistant' && (
                  <div className="mt-3 pt-3 border-t border-border/30">
                    <ChartMessage chartData={msg.chartData} />

                    {/* Pin to Dashboard button */}
                    <div className="mt-3 flex justify-end">
                      <Button
                        onClick={() => handlePin(msg)}
                        size="sm"
                        className="gap-2 bg-gradient-to-r from-primary to-primary/80 hover:opacity-90"
                      >
                        <Pin className="h-3 w-3" />
                        Add to Dashboard
                      </Button>
                    </div>
                  </div>
                )}

                {/* SQL query (if available) */}
                {msg.sqlQuery && msg.role === 'assistant' && !msg.chartData && (
                  <details className="mt-2 text-xs">
                    <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                      View SQL
                    </summary>
                    <pre className="mt-1 p-2 bg-muted/50 rounded text-[10px] overflow-x-auto">
                      {msg.sqlQuery}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl px-4 py-3 bg-card border border-border">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Analyzing your data...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-border bg-card/50 backdrop-blur-sm flex-shrink-0">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your data..."
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={() => handleSend()} disabled={loading || !input.trim()} size="lg">
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        {!datasetId && (
          <p className="text-xs text-amber-600 mt-2">
            ⚠️ No dataset ID provided. Chat may not work correctly.
          </p>
        )}
      </div>
    </div>
  );
}
