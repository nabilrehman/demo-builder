import { useSearchParams, useNavigate } from 'react-router-dom';
import { useDemoAssets } from '@/hooks/useDemoAssets';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Rocket, Download, Copy, ExternalLink, RefreshCw, CheckCircle2, Clock } from 'lucide-react';
import { DemoTitleDisplay } from '@/components/DemoTitleDisplay';
import { GoldenQueriesDisplay } from '@/components/GoldenQueriesDisplay';
import { SchemaVisualization } from '@/components/SchemaVisualization';
import { MetadataDisplay } from '@/components/MetadataDisplay';
import { toast } from 'sonner';

const DemoAssets = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const jobId = searchParams.get('jobId') || 'demo_shopify_20251004_1234';

  const { data: assets, isLoading, error } = useDemoAssets(jobId);

  const handleLaunchChat = () => {
    if (!assets) return;
    // Navigate to local chat route (same window)
    navigate(assets.provisionUrl);
  };

  const handleDownloadYAML = async () => {
    if (!assets) return;

    try {
      const response = await fetch(`/api/provision/download-yaml/${assets.jobId}`);
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `capi_instructions_${assets.metadata.datasetId}.yaml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('YAML downloaded successfully');
    } catch (err) {
      console.error('Download error:', err);
      toast.error('Failed to download YAML');
    }
  };

  const handleCopyDatasetId = async () => {
    if (!assets) return;
    await navigator.clipboard.writeText(assets.metadata.datasetId);
    toast.success('Dataset ID copied to clipboard', {
      description: assets.metadata.datasetId
    });
  };

  const handleViewInBigQuery = () => {
    if (!assets) return;
    const bqUrl = `https://console.cloud.google.com/bigquery?project=${assets.metadata.projectId}&ws=!1m4!1m3!3m2!1s${assets.metadata.projectId}!2s${assets.metadata.datasetId}`;
    window.open(bqUrl, '_blank');
  };

  const handleReRun = () => {
    toast.info('Re-provisioning demo...', {
      description: 'This will create a new dataset with updated data'
    });
    // In production: trigger re-run
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading demo assets...</p>
        </div>
      </div>
    );
  }

  if (error || !assets) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <Alert variant="destructive">
              <AlertDescription>
                Failed to load demo assets. Please check the job ID and try again.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Success Banner */}
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          <AlertDescription className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-2xl">🎉</span>
              <div>
                <div className="font-semibold text-green-900">Provision Complete!</div>
                <div className="text-green-700 text-sm mt-1">
                  Demo ready at: <span className="font-mono bg-white px-2 py-0.5 rounded">{assets.provisionUrl}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-green-700">
              <Clock className="h-4 w-4" />
              <span className="font-medium">{assets.totalTime}</span>
            </div>
          </AlertDescription>
        </Alert>

        {/* Launch Chat Button - Prominent */}
        <Card className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white border-0">
          <CardContent className="py-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                  <Rocket className="h-6 w-6" />
                  Ready to Launch
                </h2>
                <p className="text-indigo-100">
                  Your demo is provisioned and ready. Click to open the chat interface with pre-loaded data.
                </p>
              </div>
              <Button
                onClick={handleLaunchChat}
                size="lg"
                className="bg-white text-indigo-600 hover:bg-indigo-50 font-bold text-lg px-8 py-6"
              >
                <Rocket className="h-5 w-5 mr-2" />
                Launch Chat Interface
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button
            onClick={handleDownloadYAML}
            variant="outline"
            className="h-20 flex flex-col gap-2"
          >
            <Download className="h-5 w-5" />
            <span className="text-sm">Download YAML</span>
          </Button>
          <Button
            onClick={handleCopyDatasetId}
            variant="outline"
            className="h-20 flex flex-col gap-2"
          >
            <Copy className="h-5 w-5" />
            <span className="text-sm">Copy Dataset ID</span>
          </Button>
          <Button
            onClick={handleViewInBigQuery}
            variant="outline"
            className="h-20 flex flex-col gap-2"
          >
            <ExternalLink className="h-5 w-5" />
            <span className="text-sm">View in BigQuery</span>
          </Button>
          <Button
            onClick={handleReRun}
            variant="outline"
            className="h-20 flex flex-col gap-2"
          >
            <RefreshCw className="h-5 w-5" />
            <span className="text-sm">Re-run Provision</span>
          </Button>
        </div>

        {/* Tabs for Demo Content */}
        <Card>
          <CardContent className="pt-6">
            <Tabs defaultValue="title" className="w-full">
              <TabsList className="grid w-full grid-cols-4 mb-6">
                <TabsTrigger value="title">Demo Title</TabsTrigger>
                <TabsTrigger value="queries">Golden Queries</TabsTrigger>
                <TabsTrigger value="schema">Schema</TabsTrigger>
                <TabsTrigger value="metadata">Metadata</TabsTrigger>
              </TabsList>

              <TabsContent value="title" className="space-y-4">
                <DemoTitleDisplay
                  title={assets.demoTitle}
                  executiveSummary={assets.executiveSummary}
                  businessChallenges={assets.businessChallenges}
                  talkingTrack={assets.talkingTrack}
                />
              </TabsContent>

              <TabsContent value="queries" className="space-y-4">
                <GoldenQueriesDisplay queries={assets.goldenQueries} />
              </TabsContent>

              <TabsContent value="schema" className="space-y-4">
                <SchemaVisualization schema={assets.schema} />
              </TabsContent>

              <TabsContent value="metadata" className="space-y-4">
                <MetadataDisplay
                  metadata={assets.metadata}
                  customerUrl={assets.customerUrl}
                  jobId={assets.jobId}
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DemoAssets;
