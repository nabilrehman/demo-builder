import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useProvisioningProgress } from '@/hooks/useProvisioningProgress';
import { StageIndicator } from '@/components/StageIndicator';
import { LiveLogViewer } from '@/components/LiveLogViewer';
import { LoadingState } from '@/components/LoadingState';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  getRunningMessage,
  formatElapsedTime,
  COMPLETION_MESSAGES,
  FAILURE_MESSAGES,
  PENDING_MESSAGE,
} from '@/data/progressMessages';
import { Clock, ExternalLink, RefreshCw, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

const ProvisionProgress = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const jobId = searchParams.get('jobId') || searchParams.get('job_id') || 'demo-job-123';
  const customerUrl = searchParams.get('customer_url') || 'https://example.com';

  const state = useProvisioningProgress({
    jobId,
    customerUrl,
    mockMode: false, // Use REAL SSE stream from backend
  });

  const [currentMessage, setCurrentMessage] = useState('Initializing provisioning pipeline...');

  // Update current message based on stage status
  useEffect(() => {
    const currentStage = state.stages[state.currentStage - 1];

    if (!currentStage) return;

    if (currentStage.status === 'running') {
      const runningMsg = getRunningMessage(currentStage.number, currentStage.duration || 0);
      setCurrentMessage(`${runningMsg.icon} ${runningMsg.message}`);
    } else if (currentStage.status === 'complete') {
      const completionMsg = COMPLETION_MESSAGES[currentStage.number];
      setCurrentMessage(completionMsg ? completionMsg(currentStage.data) : '✅ Stage complete!');
    } else if (currentStage.status === 'failed') {
      setCurrentMessage(FAILURE_MESSAGES[currentStage.number] || '❌ Stage failed!');
    } else {
      setCurrentMessage(PENDING_MESSAGE);
    }
  }, [state.currentStage, state.stages, state.elapsedSeconds]);

  const getStatusBadge = () => {
    if (state.isFailed) {
      return (
        <Badge variant="destructive" className="gap-1">
          <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
          Failed
        </Badge>
      );
    }
    if (state.isComplete) {
      return (
        <Badge variant="default" className="gap-1 bg-green-500 hover:bg-green-600">
          <span className="w-2 h-2 bg-white rounded-full" />
          Complete
        </Badge>
      );
    }
    return (
      <Badge variant="default" className="gap-1 bg-blue-500 hover:bg-blue-600">
        <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
        Running
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <CardTitle className="text-2xl">Provisioning Pipeline</CardTitle>
                  {getStatusBadge()}
                </div>
                <CardDescription className="flex items-center gap-2">
                  <ExternalLink className="w-3 h-3" />
                  <a
                    href={customerUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    {customerUrl}
                  </a>
                </CardDescription>
              </div>

              <div className="text-right space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className="font-mono">{formatElapsedTime(state.elapsedSeconds)}</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Started {state.startTime.toLocaleTimeString()}
                </div>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Overall Progress Bar */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Overall Progress</span>
                <span className="font-mono font-medium">{state.progressPercentage}%</span>
              </div>
              <Progress value={state.progressPercentage} className="h-2" />
            </div>

            {/* Current Status Message */}
            <div
              className={cn(
                'p-4 rounded-lg border-2 transition-all duration-300',
                state.isFailed && 'border-red-500 bg-red-500/10',
                state.isComplete && 'border-green-500 bg-green-500/10',
                !state.isFailed && !state.isComplete && 'border-blue-500 bg-blue-500/10'
              )}
            >
              {/* Use witty LoadingState when running, otherwise show stage-specific message */}
              {!state.isFailed && !state.isComplete ? (
                <LoadingState />
              ) : (
                <div className="flex items-start gap-3">
                  <Sparkles
                    className={cn(
                      'w-5 h-5 mt-0.5',
                      state.isFailed && 'text-red-500',
                      state.isComplete && 'text-green-500'
                    )}
                  />
                  <div className="flex-1">
                    <div className="font-medium text-sm whitespace-pre-line">{currentMessage}</div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Stages */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Pipeline Stages</CardTitle>
            <CardDescription>7-stage autonomous provisioning system</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {state.stages.map((stage) => (
                <StageIndicator
                  key={stage.number}
                  stageNumber={stage.number}
                  name={stage.name}
                  status={stage.status}
                  duration={stage.duration}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Live Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Live Logs</CardTitle>
            <CardDescription>Real-time provisioning logs and events</CardDescription>
          </CardHeader>
          <CardContent>
            <LiveLogViewer logs={state.logs} />
          </CardContent>
        </Card>

        {/* Success Actions */}
        {state.isComplete && (
          <Card className="border-green-500 bg-green-500/5">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <span>🎉</span> Provisioning Complete!
              </CardTitle>
              <CardDescription>Your demo environment is ready</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="default"
                  className="gap-2"
                  onClick={() => {
                    // Open BigQuery console with the dataset
                    const projectId = state.metadata?.projectId || 'bq-demos-469816';
                    const datasetId = state.metadata?.datasetId || '';
                    window.open(`https://console.cloud.google.com/bigquery?project=${projectId}&ws=!1m4!1m3!3m2!1s${projectId}!2s${datasetId}`, '_blank');
                  }}
                >
                  <ExternalLink className="w-4 h-4" />
                  Open BigQuery Console
                </Button>
                <Button
                  variant="outline"
                  className="gap-2"
                  onClick={() => {
                    // Navigate to demo assets page
                    navigate(`/demo-assets?jobId=${jobId}`);
                  }}
                >
                  <ExternalLink className="w-4 h-4" />
                  View Demo Assets
                </Button>
                <Button
                  variant="outline"
                  className="gap-2"
                  onClick={() => {
                    // Navigate to polished chat interface (Index.tsx) with branding
                    const agentId = state.metadata?.agentId || '';
                    const datasetId = state.metadata?.datasetId || '';
                    const websiteUrl = state.metadata?.customerUrl || '';
                    // Navigate to root path (/) for polished interface with logo and loading jokes
                    navigate(`/?website=${websiteUrl}&agent_id=${agentId}&dataset_id=${datasetId}`);
                  }}
                >
                  <Sparkles className="w-4 h-4" />
                  Launch Chat Interface
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Failure Actions */}
        {state.isFailed && (
          <Card className="border-red-500 bg-red-500/5">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <span>💥</span> Provisioning Failed
              </CardTitle>
              <CardDescription>An error occurred during provisioning</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button variant="destructive" className="gap-2">
                  <RefreshCw className="w-4 h-4" />
                  Retry from Beginning
                </Button>
                <Button variant="outline" className="gap-2">
                  <ExternalLink className="w-4 h-4" />
                  View Error Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ProvisionProgress;
