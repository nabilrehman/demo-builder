import React from 'react';
import { Card } from "@/components/ui/card";
import { CheckCircle, XCircle, Clock, TrendingUp } from "lucide-react";

interface UserStats {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  running_jobs: number;
  success_rate: number;
  avg_completion_time: number;
  total_time_saved: number;
}

interface UserStatsCardProps {
  stats: UserStats | null;
  loading?: boolean;
}

const UserStatsCard: React.FC<UserStatsCardProps> = ({ stats, loading }) => {
  // Format time in human-readable format
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  // Format time saved in hours
  const formatTimeSaved = (seconds: number): string => {
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min`;
    const hours = Math.floor(seconds / 3600);
    return `${hours} hours`;
  };

  if (loading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-6 animate-pulse">
            <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-muted rounded w-3/4"></div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      {/* Total Jobs */}
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Total Jobs</p>
            <p className="text-3xl font-bold">{stats.total_jobs}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <TrendingUp className="h-6 w-6 text-primary" />
          </div>
        </div>
      </Card>

      {/* Success Rate */}
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Success Rate</p>
            <p className="text-3xl font-bold text-green-600">{stats.success_rate}%</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          {stats.completed_jobs} completed, {stats.failed_jobs} failed
        </p>
      </Card>

      {/* Average Time */}
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Avg Time</p>
            <p className="text-3xl font-bold">{formatTime(stats.avg_completion_time)}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
            <Clock className="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          {stats.running_jobs} currently running
        </p>
      </Card>

      {/* Time Saved */}
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Time Saved</p>
            <p className="text-3xl font-bold text-purple-600">{formatTimeSaved(stats.total_time_saved)}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
            <TrendingUp className="h-6 w-6 text-purple-600" />
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          vs manual provisioning
        </p>
      </Card>
    </div>
  );
};

export default UserStatsCard;
