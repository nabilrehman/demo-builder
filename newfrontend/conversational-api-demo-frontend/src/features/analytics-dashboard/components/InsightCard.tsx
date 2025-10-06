/**
 * InsightCard Component
 *
 * Displays a single pinned chart/insight in the dashboard
 * Wraps the existing ChartMessage component with metadata
 */

import { ChartMessage } from '@/components/ChartMessage';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Sparkles, MessageSquare } from 'lucide-react';
import { DashboardInsight } from '../types';

interface InsightCardProps {
  insight: DashboardInsight;
}

function formatTimeAgo(timestamp: number): string {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function InsightCard({ insight }: InsightCardProps) {
  const { question, chartData, sqlQuery, timestamp, source } = insight;

  return (
    <Card className="animate-slide-up hover:shadow-lg transition-all duration-300 border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <h3 className="font-semibold text-base text-foreground leading-snug">
              {question}
            </h3>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {source === 'quick-insight' && (
              <Badge variant="secondary" className="gap-1 text-xs">
                <Sparkles className="h-3 w-3" />
                Quick
              </Badge>
            )}
            {source === 'conversation' && (
              <Badge variant="outline" className="gap-1 text-xs">
                <MessageSquare className="h-3 w-3" />
                Chat
              </Badge>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
          <Clock className="h-3 w-3" />
          <span>{formatTimeAgo(timestamp)}</span>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Reuse existing ChartMessage component */}
        <ChartMessage chartData={chartData} />

        {/* Optional: Show SQL query in expandable section */}
        {sqlQuery && (
          <details className="mt-4 group">
            <summary className="cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground transition-colors list-none flex items-center gap-2">
              <span className="text-xs">▶</span>
              View SQL Query
            </summary>
            <pre className="mt-2 p-3 bg-muted/50 rounded-md text-xs overflow-x-auto font-mono text-foreground border border-border/30">
              {sqlQuery}
            </pre>
          </details>
        )}
      </CardContent>
    </Card>
  );
}
