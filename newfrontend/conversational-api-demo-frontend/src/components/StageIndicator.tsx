import { StageStatus } from '@/hooks/useProvisioningProgress';
import { formatElapsedTime } from '@/data/progressMessages';
import { Loader2, CheckCircle2, XCircle, Pause } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StageIndicatorProps {
  stageNumber: number;
  name: string;
  status: StageStatus;
  duration?: number;
}

export const StageIndicator = ({ stageNumber, name, status, duration = 0 }: StageIndicatorProps) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Pause className="w-4 h-4 text-muted-foreground" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'complete':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'border-muted bg-muted/5';
      case 'running':
        return 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20';
      case 'complete':
        return 'border-green-500 bg-green-500/10';
      case 'failed':
        return 'border-red-500 bg-red-500/10';
    }
  };

  const getTextColor = () => {
    switch (status) {
      case 'pending':
        return 'text-muted-foreground';
      case 'running':
        return 'text-blue-600 font-medium';
      case 'complete':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
    }
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg border-2 transition-all duration-300',
        getStatusColor()
      )}
    >
      {/* Stage Number */}
      <div
        className={cn(
          'flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm transition-colors',
          status === 'running' && 'bg-blue-500 text-white',
          status === 'complete' && 'bg-green-500 text-white',
          status === 'failed' && 'bg-red-500 text-white',
          status === 'pending' && 'bg-muted text-muted-foreground'
        )}
      >
        {stageNumber}
      </div>

      {/* Stage Name */}
      <div className="flex-1">
        <div className={cn('text-sm font-medium', getTextColor())}>{name}</div>
      </div>

      {/* Status Icon & Duration */}
      <div className="flex items-center gap-2">
        {status === 'running' && duration > 0 && (
          <span className="text-xs text-muted-foreground font-mono">
            {formatElapsedTime(duration)}
          </span>
        )}
        {getStatusIcon()}
      </div>
    </div>
  );
};
