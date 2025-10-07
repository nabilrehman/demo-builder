import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle2, XCircle, Loader2, Clock, Trash2, ExternalLink, Play } from 'lucide-react';
import DeleteJobModal from './DeleteJobModal';

export interface ProvisionJob {
  id: string;
  url: string;
  status: 'complete' | 'failed' | 'running';
  duration: string;
  date: string;
  mode: 'default' | 'advanced';
}

interface EnhancedJobHistoryTableProps {
  jobs: ProvisionJob[];
  onDelete: (jobId: string) => Promise<void>;
  onViewJob: (jobId: string) => void;
}

const EnhancedJobHistoryTable: React.FC<EnhancedJobHistoryTableProps> = ({
  jobs,
  onDelete,
  onViewJob,
}) => {
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [jobToDelete, setJobToDelete] = useState<ProvisionJob | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (job: ProvisionJob) => {
    setJobToDelete(job);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!jobToDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(jobToDelete.id);
      setDeleteModalOpen(false);
      setJobToDelete(null);
    } catch (error) {
      console.error('Error deleting job:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-3 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1.5";

    switch (status) {
      case 'complete':
        return (
          <span className={`${baseClasses} bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border border-green-200`}>
            {getStatusIcon(status)}
            Completed
          </span>
        );
      case 'failed':
        return (
          <span className={`${baseClasses} bg-gradient-to-r from-red-100 to-rose-100 text-red-700 border border-red-200`}>
            {getStatusIcon(status)}
            Failed
          </span>
        );
      case 'running':
        return (
          <span className={`${baseClasses} bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border border-blue-200`}>
            {getStatusIcon(status)}
            Running
          </span>
        );
      default:
        return (
          <span className={`${baseClasses} bg-gradient-to-r from-gray-100 to-slate-100 text-gray-700 border border-gray-200`}>
            {getStatusIcon(status)}
            Pending
          </span>
        );
    }
  };

  const getModeBadge = (mode: string) => {
    if (mode === 'advanced') {
      return (
        <span className="px-2 py-0.5 rounded text-xs font-medium bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 border border-purple-200">
          Advanced
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-xs font-medium bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-700 border border-blue-200">
        Default
      </span>
    );
  };

  if (jobs.length === 0) {
    return (
      <Card className="p-12 text-center bg-gradient-to-br from-white to-gray-50 border-2 border-dashed border-gray-200">
        <div className="flex flex-col items-center gap-4">
          <div className="h-20 w-20 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
            <Play className="h-10 w-10 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">No jobs found</h3>
            <p className="text-sm text-gray-500">
              Try adjusting your filters or create a new provisioning job
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {jobs.map((job) => (
          <Card
            key={job.id}
            className="p-5 hover:shadow-lg transition-all duration-300 bg-gradient-to-r from-white to-gray-50/50 border border-gray-200 hover:border-blue-300 group"
          >
            <div className="flex items-center justify-between gap-4">
              {/* Left: Job Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-gray-900 truncate hover:text-blue-600 transition-colors">
                    {job.url}
                  </h3>
                  {getModeBadge(job.mode)}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {job.duration}
                  </span>
                  <span>•</span>
                  <span>{job.date}</span>
                </div>
              </div>

              {/* Center: Status */}
              <div className="flex items-center gap-3">
                {getStatusBadge(job.status)}
              </div>

              {/* Right: Actions */}
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewJob(job.id)}
                  className="border-blue-200 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 hover:border-blue-400 text-blue-700 transition-all"
                >
                  <ExternalLink className="h-4 w-4 mr-1" />
                  View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteClick(job)}
                  className="border-red-200 hover:bg-gradient-to-r hover:from-red-50 hover:to-rose-50 hover:border-red-400 text-red-700 transition-all"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteJobModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setJobToDelete(null);
        }}
        onConfirm={handleDeleteConfirm}
        jobUrl={jobToDelete?.url || ''}
        isDeleting={isDeleting}
      />
    </>
  );
};

export default EnhancedJobHistoryTable;
