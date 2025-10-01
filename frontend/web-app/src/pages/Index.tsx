import { useState, useEffect } from "react";
import { Bot } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { LoadingState } from "@/components/LoadingState";
import { DeveloperMode } from "@/components/DeveloperMode";
import { BrandingSetup } from "@/components/BrandingSetup";
import { ChatHeader } from "@/components/ChatHeader";

import { useToast } from "@/hooks/use-toast";

interface ChartData {
  type: "bar" | "line" | "pie";
  title: string;
  data: any[];
  xKey?: string;
  yKey?: string;
  nameKey?: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  chartData?: ChartData;
}

interface BrandingData {
  brandName: string;
  logoUrl: string;
  websiteUrl: string;
  primaryColor?: string;
  faviconUrl?: string;
}

const Index = () => {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [developerMode, setDeveloperMode] = useState(false);
  const [lastQuery, setLastQuery] = useState("");
  const [lastResponse, setLastResponse] = useState("");
  const [branding, setBranding] = useState<BrandingData | null>(null);
  const [showSetup, setShowSetup] = useState(false);

  // Load branding from localStorage or URL parameter on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const websiteParam = urlParams.get('website');
    
    if (websiteParam) {
      // Auto-configure from URL parameter
      setShowSetup(false);
      extractAndSetBranding(websiteParam);
    } else {
      // Load from localStorage
      const savedBranding = localStorage.getItem('chatbot_branding');
      if (savedBranding) {
        try {
          const brandingData = JSON.parse(savedBranding);
          setBranding(brandingData);
          updateBrandingElements(brandingData);
        } catch (error) {
          console.error('Error loading branding:', error);
          setShowSetup(true);
        }
      } else {
        setShowSetup(true);
      }
    }
  }, []);

  const updateBrandingElements = (brandingData: BrandingData) => {
    // Update page title
    document.title = `AI Chatbot | ${brandingData.brandName}`;
    // Update favicon if available
    if (brandingData.faviconUrl) {
      const favicon = document.querySelector("link[rel='icon']") as HTMLLinkElement;
      if (favicon) {
        favicon.href = brandingData.faviconUrl;
      }
    }
  };

  const extractAndSetBranding = async (url: string) => {
    try {
      let normalizedUrl = url.trim();
      if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
        normalizedUrl = 'https://' + normalizedUrl;
      }

      const urlObj = new URL(normalizedUrl);
      const domain = urlObj.hostname.replace('www.', '');
      
      const brandName = domain
        .split('.')[0]
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      console.log('Fetching website for branding:', normalizedUrl);
      
      let logoUrl = '';
      let faviconUrl = `${urlObj.protocol}//${urlObj.hostname}/favicon.ico`;
      
      try {
        const response = await fetch(normalizedUrl, {
          method: 'GET',
          headers: {
            'User-Agent': 'Mozilla/5.0 (compatible; LogoExtractor/1.0)'
          }
        });
        
        if (response.ok) {
          const html = await response.text();
          
          const logoPatterns = [
            /<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i,
            /<meta\s+name=["']twitter:image["']\s+content=["']([^"']+)["']/i,
            /<link\s+rel=["']apple-touch-icon["'][^>]*href=["']([^"']+)["']/i,
            /<img[^>]*(?:class|id)=["'][^"']*logo[^"']*["'][^>]*src=["']([^"']+)["']/i,
            /<link\s+rel=["'](?:icon|shortcut icon)["'][^>]*href=["']([^"']+)["']/i,
          ];
          
          for (const pattern of logoPatterns) {
            const match = html.match(pattern);
            if (match && match[1]) {
              let extractedUrl = match[1];
              
              if (extractedUrl.startsWith('//')) {
                extractedUrl = urlObj.protocol + extractedUrl;
              } else if (extractedUrl.startsWith('/')) {
                extractedUrl = `${urlObj.protocol}//${urlObj.hostname}${extractedUrl}`;
              } else if (!extractedUrl.startsWith('http')) {
                extractedUrl = `${urlObj.protocol}//${urlObj.hostname}/${extractedUrl}`;
              }
              
              if (!logoUrl && (pattern === logoPatterns[0] || pattern === logoPatterns[1] || pattern === logoPatterns[3])) {
                logoUrl = extractedUrl;
              }
              
              if (pattern === logoPatterns[2] || pattern === logoPatterns[4]) {
                faviconUrl = extractedUrl;
              }
              
              if (logoUrl) break;
            }
          }
        }
      } catch (fetchError) {
        console.log('Could not fetch website, using fallback:', fetchError);
      }

      if (!logoUrl) {
        logoUrl = faviconUrl;
      }

      const brandingData: BrandingData = {
        brandName,
        logoUrl,
        websiteUrl: normalizedUrl,
        faviconUrl,
        primaryColor: '#8b5cf6'
      };

      setBranding(brandingData);
      updateBrandingElements(brandingData);
      localStorage.setItem('chatbot_branding', JSON.stringify(brandingData));
    } catch (error) {
      console.error('Error extracting branding:', error);
      setShowSetup(true);
    }
  };

  const handleBrandingComplete = (brandingData: BrandingData) => {
    setBranding(brandingData);
    setShowSetup(false);
    updateBrandingElements(brandingData);
  };

  const handleReconfigure = () => {
    setShowSetup(true);
    setMessages([]);
    localStorage.removeItem('chatbot_branding');
  };

  // Mock responses customized for the brand
  const getMockResponses = () => {
    const brandName = branding?.brandName || "Your Brand";
    return [
      `I'm here to help you with ${brandName}! This is a demo response. Your backend integration will replace this.`,
      `Great question! Once connected to your API, I'll provide intelligent responses about ${brandName}.`,
      `I understand. The backend API will process your query and return personalized responses for ${brandName}.`,
      `Interesting! This chatbot is ready to serve ${brandName} customers with AI-powered assistance.`
    ];
  };

  // Generate sample analytics data based on query
  const generateChartData = (query: string): ChartData | undefined => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes("conversation") || lowerQuery.includes("analytics") || lowerQuery.includes("chart")) {
      // Return different chart types based on keywords
      if (lowerQuery.includes("sentiment") || lowerQuery.includes("emotion")) {
        return {
          type: "pie",
          title: "Sentiment Distribution",
          data: [
            { name: "Positive", value: 65 },
            { name: "Neutral", value: 25 },
            { name: "Negative", value: 10 }
          ],
          yKey: "value",
          nameKey: "name"
        };
      }
      
      if (lowerQuery.includes("volume") || lowerQuery.includes("traffic")) {
        return {
          type: "line",
          title: "Conversation Volume Over Time",
          data: [
            { date: "Mon", conversations: 120 },
            { date: "Tue", conversations: 185 },
            { date: "Wed", conversations: 210 },
            { date: "Thu", conversations: 195 },
            { date: "Fri", conversations: 240 },
            { date: "Sat", conversations: 160 },
            { date: "Sun", conversations: 145 }
          ],
          xKey: "date",
          yKey: "conversations"
        };
      }
      
      // Default to bar chart for general queries
      return {
        type: "bar",
        title: "Top Conversation Topics",
        data: [
          { topic: "Billing", count: 145 },
          { topic: "Support", count: 230 },
          { topic: "Features", count: 180 },
          { topic: "Technical", count: 95 },
          { topic: "General", count: 160 }
        ],
        xKey: "topic",
        yKey: "count"
      };
    }
    
    return undefined;
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setLastQuery(content);

    try {
      setLoadingMessage("Analyzing your question...");
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setLoadingMessage("Generating insights...");
      
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from backend");
      }

      const data = await response.json();

      await new Promise(resolve => setTimeout(resolve, 300));

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        chartData: data.chartData
      };
      
      const responseData = {
        query: content,
        response: data.response,
        chartData: data.chartData || null,
        sqlQuery: data.sqlQuery || null,
        source: "Backend API"
      };
      
      setLastResponse(JSON.stringify(responseData, null, 2));
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive",
      });
      
      setMessages(prev => prev.filter(m => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
      setLoadingMessage("");
    }
  };

  // Show setup screen if branding not configured
  if (showSetup || !branding) {
    return <BrandingSetup onComplete={handleBrandingComplete} />;
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <ChatHeader
        brandName={branding.brandName}
        logoUrl={branding.logoUrl}
        faviconUrl={branding.faviconUrl}
        developerMode={developerMode}
        onDeveloperModeChange={setDeveloperMode}
        onReconfigure={handleReconfigure}
      />

      {/* Main Chat Area */}
      <div className="flex-1 container mx-auto px-4 py-6 flex flex-col gap-4 overflow-hidden">
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4 pb-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full py-12 text-center animate-fade-in">
                {branding.logoUrl || branding.faviconUrl ? (
                  <div className="h-16 w-16 rounded-2xl overflow-hidden shadow-xl mb-4 bg-background flex items-center justify-center">
                    <img
                      src={branding.logoUrl || branding.faviconUrl}
                      alt={`${branding.brandName} logo`}
                      className="h-full w-full object-contain"
                      onError={(e) => {
                        const parent = e.currentTarget.parentElement;
                        if (parent) {
                          parent.className = "h-16 w-16 rounded-2xl bg-gradient-button flex items-center justify-center shadow-xl mb-4";
                          parent.innerHTML = `<span class="text-3xl font-bold text-primary-foreground">${branding.brandName.charAt(0)}</span>`;
                        }
                      }}
                    />
                  </div>
                ) : (
                  <div className="h-16 w-16 rounded-2xl bg-gradient-button flex items-center justify-center shadow-xl mb-4">
                    <span className="text-3xl font-bold text-primary-foreground">
                      {branding.brandName.charAt(0)}
                    </span>
                  </div>
                )}
                <h2 className="text-2xl font-bold mb-2">Welcome to {branding.brandName} AI Assistant</h2>
                <p className="text-muted-foreground max-w-md">
                  Start a conversation by typing your question below. Ready to integrate with your backend API.
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  role={message.role}
                  content={message.content}
                  chartData={message.chartData}
                />
              ))
            )}
            {isLoading && <LoadingState message={loadingMessage} />}
          </div>
        </ScrollArea>

        {/* Developer Mode Panel */}
        {developerMode && (
          <div className="animate-slide-up">
            <DeveloperMode query={lastQuery} response={lastResponse} />
          </div>
        )}

        {/* Input Area */}
        <div className="border-t pt-4 bg-card/50 backdrop-blur-sm rounded-t-xl -mx-4 px-4 pb-4">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default Index;
