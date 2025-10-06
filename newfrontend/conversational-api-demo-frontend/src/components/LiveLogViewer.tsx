import { useEffect, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LogEntry } from '@/hooks/useProvisioningProgress';
import { cn } from '@/lib/utils';
import { Terminal } from 'lucide-react';

interface LiveLogViewerProps {
  logs: LogEntry[];
}

export const LiveLogViewer = ({ logs }: LiveLogViewerProps) => {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'SUCCESS':
        return 'text-green-500';
      case 'ERROR':
        return 'text-red-500';
      case 'WARNING':
        return 'text-yellow-500';
      case 'INFO':
      default:
        return 'text-blue-400';
    }
  };

  const getLevelBadge = (level: LogEntry['level']) => {
    switch (level) {
      case 'SUCCESS':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'ERROR':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      case 'WARNING':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'INFO':
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2 bg-slate-900 border-b border-slate-800">
        <Terminal className="w-4 h-4 text-green-400" />
        <span className="text-sm font-mono text-green-400">Live Logs</span>
        <div className="ml-auto flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-slate-400">{logs.length} entries</span>
        </div>
      </div>

      {/* Logs */}
      <ScrollArea className="h-[300px]" ref={scrollAreaRef}>
        <div className="p-4 space-y-1 font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              Waiting for logs...
            </div>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={cn(
                  'flex items-start gap-3 py-1.5 px-2 rounded hover:bg-slate-900/50 transition-colors',
                  'animate-in fade-in slide-in-from-left-2 duration-200'
                )}
              >
                {/* Timestamp */}
                <span className="text-slate-500 text-xs whitespace-nowrap mt-0.5">
                  {formatTimestamp(log.timestamp)}
                </span>

                {/* Stage */}
                <span className="text-slate-600 text-xs whitespace-nowrap mt-0.5">
                  [Stage {log.stage}]
                </span>

                {/* Level Badge */}
                <span
                  className={cn(
                    'px-1.5 py-0.5 text-[10px] font-bold rounded border whitespace-nowrap',
                    getLevelBadge(log.level)
                  )}
                >
                  {log.level}
                </span>

                {/* Message */}
                <span className={cn('flex-1', getLevelColor(log.level))}>
                  {log.message}
                </span>
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
};
