/**
 * InsightsGrid Component
 *
 * Right panel showing dashboard with pinned insights
 * Includes Quick Insights panel and grid of charts
 */

import { InsightCard } from './InsightCard';
import { QuickInsights } from './QuickInsights';
import { Card, CardContent } from '@/components/ui/card';
import { Sparkles, BarChart3 } from 'lucide-react';
import { DashboardInsight, GoldenQuery, ChartData } from '../types';
import { toast } from 'sonner';

interface InsightsGridProps {
  insights: DashboardInsight[];
  goldenQueries: GoldenQuery[];
  demoTitle?: string;
  datasetId: string | null;
  agentId: string | null;
  onAddInsight: (
    question: string,
    chartData: ChartData,
    sqlQuery?: string,
    source?: 'conversation' | 'quick-insight'
  ) => void;
}

export function InsightsGrid({
  insights,
  goldenQueries,
  demoTitle,
  datasetId,
  agentId,
  onAddInsight
}: InsightsGridProps) {
  // Execute golden query and add to dashboard
  const handleExecuteGoldenQuery = async (query: GoldenQuery) => {
    try {
      // Call chat API with the golden query question
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query.question,
          dataset_id: datasetId,
          agent_id: agentId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to execute query');
      }

      const data = await response.json();

      // Add to dashboard if we got chart data
      if (data.chartData) {
        onAddInsight(query.question, data.chartData, data.sqlQuery, 'quick-insight');
      } else {
        toast.warning('No chart data returned', {
          description: 'This query did not return visualizable data'
        });
      }
    } catch (error) {
      console.error('Error executing golden query:', error);
      toast.error('Failed to execute query', {
        description: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-slate-50 to-blue-50 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">
            {demoTitle || 'Analytics Dashboard'}
          </h1>
          <p className="text-muted-foreground">
            {insights.length === 0
              ? 'Your insights will appear here as you explore'
              : `${insights.length} insight${insights.length === 1 ? '' : 's'} added`}
          </p>
        </div>

        {/* Quick Insights Panel */}
        {goldenQueries.length > 0 && (
          <QuickInsights
            queries={goldenQueries}
            onExecute={handleExecuteGoldenQuery}
          />
        )}

        {/* Insights Grid */}
        {insights.length === 0 ? (
          <Card className="border-dashed border-2 border-border/50 bg-background/30">
            <CardContent className="p-12">
              <div className="text-center space-y-4">
                <div className="flex justify-center">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <BarChart3 className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-foreground">
                    Start Building Your Dashboard
                  </h3>
                  <p className="text-sm text-muted-foreground max-w-md mx-auto">
                    Ask questions in the chat to explore your data. When you get insights with
                    charts, click <strong>"📌 Add to Dashboard"</strong> to pin them here.
                  </p>
                </div>
                {goldenQueries.length > 0 && (
                  <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground pt-4">
                    <Sparkles className="h-4 w-4 text-primary" />
                    <span>Or try a Quick Insight above</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {insights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        )}

        {/* Footer */}
        {insights.length > 0 && (
          <div className="text-center py-6 text-sm text-muted-foreground">
            <div className="flex items-center justify-center gap-2">
              <Sparkles className="h-4 w-4" />
              <span>Built with Conversational Analytics API</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
