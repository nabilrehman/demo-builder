import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Database, ExternalLink, Copy, Calendar, HardDrive, Layers, Globe } from 'lucide-react';
import { toast } from 'sonner';

interface MetadataDisplayProps {
  metadata: {
    datasetId: string;
    datasetFullName: string;
    projectId: string;
    totalRows: number;
    totalStorageMB: number;
    generationTimestamp: string;
    totalTables: number;
  };
  customerUrl: string;
  jobId: string;
}

export const MetadataDisplay = ({ metadata, customerUrl, jobId }: MetadataDisplayProps) => {
  const copyToClipboard = async (text: string, label: string) => {
    await navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`, {
      description: text
    });
  };

  const openBigQuery = (path: string) => {
    const url = `https://console.cloud.google.com/bigquery?project=${metadata.projectId}&ws=${path}`;
    window.open(url, '_blank');
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  };

  const formatStorageSize = (mb: number) => {
    if (mb < 1) return `${(mb * 1024).toFixed(2)} KB`;
    if (mb < 1024) return `${mb.toFixed(2)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  return (
    <div className="space-y-6">
      {/* Dataset Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-indigo-600" />
            Dataset Information
          </CardTitle>
          <CardDescription>BigQuery dataset details and identifiers</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-600">Dataset ID</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-gray-100 px-3 py-2 rounded text-sm font-mono">
                  {metadata.datasetId}
                </code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(metadata.datasetId, 'Dataset ID')}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-600">Project ID</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-gray-100 px-3 py-2 rounded text-sm font-mono">
                  {metadata.projectId}
                </code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(metadata.projectId, 'Project ID')}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-600">Full Dataset Name</label>
            <div className="flex items-center gap-2">
              <code className="flex-1 bg-gray-100 px-3 py-2 rounded text-sm font-mono">
                {metadata.datasetFullName}
              </code>
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(metadata.datasetFullName, 'Full dataset name')}
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => openBigQuery(`!1m4!1m3!3m2!1s${metadata.projectId}!2s${metadata.datasetId}`)}
              >
                <ExternalLink className="h-4 w-4 mr-1" />
                Open in BigQuery
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-purple-600" />
            Dataset Statistics
          </CardTitle>
          <CardDescription>Data volume and composition metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-indigo-600">
                {metadata.totalTables}
              </div>
              <div className="text-sm text-indigo-700 mt-1">Tables</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {metadata.totalRows.toLocaleString()}
              </div>
              <div className="text-sm text-green-700 mt-1">Total Rows</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {formatStorageSize(metadata.totalStorageMB)}
              </div>
              <div className="text-sm text-purple-700 mt-1">Storage Size</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {(metadata.totalRows / metadata.totalTables).toLocaleString(undefined, {
                  maximumFractionDigits: 0
                })}
              </div>
              <div className="text-sm text-orange-700 mt-1">Avg Rows/Table</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Provisioning Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-600" />
            Provisioning Details
          </CardTitle>
          <CardDescription>Generation metadata and source information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Source URL
              </label>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-gray-100 px-3 py-2 rounded text-sm font-mono overflow-x-auto">
                  {customerUrl}
                </code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open(customerUrl, '_blank')}
                >
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-600 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Generation Time
              </label>
              <div className="bg-gray-100 px-3 py-2 rounded text-sm">
                {formatTimestamp(metadata.generationTimestamp)}
              </div>
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-600">Job ID</label>
            <div className="flex items-center gap-2">
              <code className="flex-1 bg-gray-100 px-3 py-2 rounded text-sm font-mono">
                {jobId}
              </code>
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(jobId, 'Job ID')}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* BigQuery Links */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="h-5 w-5 text-blue-600" />
            Quick Links
          </CardTitle>
          <CardDescription>Jump directly to BigQuery console views</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start bg-white"
              onClick={() => openBigQuery(`!1m4!1m3!3m2!1s${metadata.projectId}!2s${metadata.datasetId}`)}
            >
              <Database className="h-4 w-4 mr-2" />
              View Dataset in BigQuery Console
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start bg-white"
              onClick={() => openBigQuery(`!1m5!1m4!4m3!1s${metadata.projectId}!2s${metadata.datasetId}!3sschema`)}
            >
              <Layers className="h-4 w-4 mr-2" />
              View Schema in BigQuery
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start bg-white"
              onClick={() => window.open(`https://console.cloud.google.com/bigquery?project=${metadata.projectId}`, '_blank')}
            >
              <HardDrive className="h-4 w-4 mr-2" />
              Open BigQuery Query Editor
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Cost Information */}
      <Card className="bg-green-50 border-green-200">
        <CardContent className="pt-6">
          <h3 className="font-semibold text-green-900 mb-2">Cost Information</h3>
          <div className="text-sm text-green-800 space-y-1">
            <div className="flex justify-between">
              <span>Storage Cost (per month):</span>
              <Badge variant="outline" className="bg-white">
                ${((metadata.totalStorageMB / 1024) * 0.02).toFixed(4)}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span>Generation Cost (estimated):</span>
              <Badge variant="outline" className="bg-white">$0.10</Badge>
            </div>
            <div className="text-xs text-green-700 mt-2">
              * Storage pricing: $0.02 per GB/month (active storage)
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
