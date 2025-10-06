/**
 * Hook for managing dashboard insights (pinned charts)
 *
 * Provides add functionality for building dashboard through conversation
 */

import { useState } from 'react';
import { toast } from 'sonner';
import { DashboardInsight, ChartData } from '../types';

export function useDashboardInsights() {
  const [insights, setInsights] = useState<DashboardInsight[]>([]);

  const addInsight = (
    question: string,
    chartData: ChartData,
    sqlQuery?: string,
    source: 'conversation' | 'quick-insight' = 'conversation'
  ) => {
    const newInsight: DashboardInsight = {
      id: crypto.randomUUID(),
      question,
      chartData,
      sqlQuery,
      timestamp: Date.now(),
      source
    };

    setInsights(prev => [...prev, newInsight]);

    // Show success toast
    toast.success('✨ Insight added to dashboard', {
      description: question.length > 50 ? question.substring(0, 50) + '...' : question
    });
  };

  return {
    insights,
    addInsight,
    insightCount: insights.length
  };
}
