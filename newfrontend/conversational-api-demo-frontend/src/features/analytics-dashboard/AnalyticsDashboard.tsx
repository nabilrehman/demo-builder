/**
 * Analytics Dashboard - Main Page
 *
 * Conversational dashboard builder for non-technical users
 * Ask questions → Get insights → Build dashboard on the fly
 */

import { useSearchParams } from 'react-router-dom';
import { ChatExplorer } from './components/ChatExplorer';
import { InsightsGrid } from './components/InsightsGrid';
import { useDashboardInsights } from './hooks/useDashboardInsights';
import { useGoldenQueries } from './hooks/useGoldenQueries';

export default function AnalyticsDashboard() {
  const [searchParams] = useSearchParams();

  // Get URL parameters
  const datasetId = searchParams.get('dataset_id');
  const agentId = searchParams.get('agent_id');
  const jobId = searchParams.get('job_id');

  // State management
  const { insights, addInsight, insightCount } = useDashboardInsights();
  const { goldenQueries, loading: loadingQueries } = useGoldenQueries(jobId);

  // Extract demo title from golden queries metadata if available
  const demoTitle = goldenQueries[0]?.businessValue?.includes('Nike')
    ? 'Nike E-Commerce Analytics'
    : 'Analytics Dashboard';

  return (
    <div className="h-screen flex overflow-hidden">
      {/* Left: Chat Explorer (45%) */}
      <ChatExplorer
        datasetId={datasetId}
        agentId={agentId}
        demoTitle={demoTitle}
        goldenQueries={goldenQueries}
        onPinInsight={addInsight}
      />

      {/* Right: Insights Grid (55%) */}
      <InsightsGrid
        insights={insights}
        goldenQueries={goldenQueries}
        demoTitle={demoTitle}
        datasetId={datasetId}
        agentId={agentId}
        onAddInsight={addInsight}
      />
    </div>
  );
}
