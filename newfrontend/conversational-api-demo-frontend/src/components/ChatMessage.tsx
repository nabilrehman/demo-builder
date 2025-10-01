import { cn } from "@/lib/utils";
import { ChartMessage } from "./ChartMessage";

// Vega-Lite specification from Google Conversational Analytics API
interface ChartData {
  $schema?: string;
  [key: string]: any;
}

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isLoading?: boolean;
  chartData?: ChartData;
}

export const ChatMessage = ({ role, content, isLoading, chartData }: ChatMessageProps) => {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-slide-up flex-col",
        isUser ? "items-end" : "items-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 shadow-sm",
          isUser
            ? "bg-gradient-button text-primary-foreground"
            : "bg-bot-message text-bot-message-foreground",
          chartData && !isUser && "max-w-[90%]"
        )}
      >
        {isLoading ? (
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-full bg-current animate-pulse-subtle" />
            <div className="h-2 w-2 rounded-full bg-current animate-pulse-subtle [animation-delay:0.2s]" />
            <div className="h-2 w-2 rounded-full bg-current animate-pulse-subtle [animation-delay:0.4s]" />
          </div>
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        )}
      </div>
      {chartData && !isUser && (
        <div className="mt-3 w-full max-w-[90%]">
          <ChartMessage chartData={chartData} />
        </div>
      )}
    </div>
  );
};
