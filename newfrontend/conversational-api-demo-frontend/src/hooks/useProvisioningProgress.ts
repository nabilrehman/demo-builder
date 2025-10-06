import { useState, useEffect, useRef, useCallback } from 'react';
import { STAGES } from '@/data/progressMessages';

export type StageStatus = 'pending' | 'running' | 'complete' | 'failed';

export interface StageProgress {
  number: number;
  name: string;
  status: StageStatus;
  duration?: number;
  data?: any;
}

export interface LogEntry {
  timestamp: string;
  stage: number;
  level: 'INFO' | 'SUCCESS' | 'ERROR' | 'WARNING';
  message: string;
}

export interface ProvisioningState {
  jobId: string;
  customerUrl: string;
  startTime: Date;
  elapsedSeconds: number;
  stages: StageProgress[];
  currentStage: number;
  currentMessage: string;
  logs: LogEntry[];
  progressPercentage: number;
  isComplete: boolean;
  isFailed: boolean;
  metadata?: {
    projectId?: string;
    datasetId?: string;
    agentId?: string;
    datasetFullName?: string;
    totalRows?: number;
    totalStorageMB?: number;
  };
}

interface UseProvisioningProgressProps {
  jobId: string;
  customerUrl: string;
  mockMode?: boolean; // Enable mock SSE simulation
}

export const useProvisioningProgress = ({
  jobId,
  customerUrl,
  mockMode = true
}: UseProvisioningProgressProps) => {
  const [state, setState] = useState<ProvisioningState>({
    jobId,
    customerUrl,
    startTime: new Date(),
    elapsedSeconds: 0,
    stages: STAGES.map((stage) => ({
      number: stage.number,
      name: stage.name,
      status: 'pending',
    })),
    currentStage: 1,
    currentMessage: 'Initializing provisioning pipeline...',
    logs: [],
    progressPercentage: 0,
    isComplete: false,
    isFailed: false,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const mockTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Update elapsed time every second
  useEffect(() => {
    timerRef.current = setInterval(() => {
      setState((prev) => ({
        ...prev,
        elapsedSeconds: Math.floor((new Date().getTime() - prev.startTime.getTime()) / 1000),
      }));
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Mock SSE simulation for testing
  const startMockSSE = useCallback(() => {
    let currentStage = 1;
    let stageStartTime = Date.now();

    const stageDurations = [15, 300, 45, 60, 180, 240, 50]; // seconds for each stage

    const updateStage = () => {
      const elapsed = Math.floor((Date.now() - stageStartTime) / 1000);

      // Update current stage to running
      setState((prev) => {
        const newStages = [...prev.stages];
        newStages[currentStage - 1] = {
          ...newStages[currentStage - 1],
          status: 'running',
          duration: elapsed,
        };

        // Calculate progress percentage
        const completedStages = currentStage - 1;
        const totalStages = STAGES.length; // 6 stages (validator disabled)
        const progressPercentage = Math.floor((completedStages / totalStages) * 100 + (elapsed / stageDurations[currentStage - 1]) * (100 / totalStages));

        return {
          ...prev,
          stages: newStages,
          currentStage,
          progressPercentage: Math.min(progressPercentage, 100),
        };
      });

      // Add logs periodically
      if (elapsed % 3 === 0) {
        const logMessages = [
          'Processing data...',
          'Analyzing schema...',
          'Generating content...',
          'Validating output...',
          'Optimizing results...',
        ];

        setState((prev) => ({
          ...prev,
          logs: [
            ...prev.logs,
            {
              timestamp: new Date().toISOString(),
              stage: currentStage,
              level: 'INFO',
              message: logMessages[Math.floor(Math.random() * logMessages.length)],
            },
          ],
        }));
      }

      // Check if stage is complete
      if (elapsed >= stageDurations[currentStage - 1]) {
        setState((prev) => {
          const newStages = [...prev.stages];
          newStages[currentStage - 1] = {
            ...newStages[currentStage - 1],
            status: 'complete',
            duration: stageDurations[currentStage - 1],
            data: getMockStageData(currentStage),
          };

          return {
            ...prev,
            stages: newStages,
            logs: [
              ...prev.logs,
              {
                timestamp: new Date().toISOString(),
                stage: currentStage,
                level: 'SUCCESS',
                message: `Stage ${currentStage} completed successfully`,
              },
            ],
          };
        });

        currentStage++;
        stageStartTime = Date.now();

        // Check if all stages complete
        if (currentStage > STAGES.length) {
          setState((prev) => ({
            ...prev,
            isComplete: true,
            currentMessage: '🎊 PROVISIONING COMPLETE! 🎊',
            progressPercentage: 100,
          }));

          if (mockTimerRef.current) {
            clearInterval(mockTimerRef.current);
          }
        }
      }
    };

    mockTimerRef.current = setInterval(updateStage, 1000);
  }, []);

  // Get mock data for completed stages
  const getMockStageData = (stage: number): any => {
    switch (stage) {
      case 1:
        return { industry: 'E-commerce' };
      case 2:
        return { demoTitle: 'E-commerce Analytics Dashboard', queryCount: 12 };
      case 3:
        return { tableCount: 8, totalFields: 67, queryCount: 12 };
      case 4:
        return { totalRows: 145000, tableCount: 8, totalSize: 12.3 };
      case 5:
        return {
          datasetName: 'demo_ecommerce_20251004',
          tableCount: 8,
          totalRows: 145000,
          totalSize: 12.3,
          consoleUrl: 'https://console.cloud.google.com/bigquery?project=demo&d=demo_ecommerce',
        };
      case 6:
        return { fileSize: 42, tableCount: 8, relationshipCount: 15, queryCount: 12, filePath: '/tmp/capi_ecommerce.yaml' };
      case 7:
        return { validatedCount: 12, totalCount: 12 };
      default:
        return {};
    }
  };

  // Helper function to process backend data and update state
  const processBackendData = useCallback((data: any, prev: ProvisioningState) => {
    const newStages = [...prev.stages];

    // FIX: Backend sends full job state with agents array
    if (data.agents && Array.isArray(data.agents)) {
      data.agents.forEach((agent: any, index: number) => {
        if (index < newStages.length) {
          newStages[index] = {
            number: index + 1,
            name: agent.name || newStages[index].name,
            status: agent.status === 'completed' ? 'complete' : agent.status, // FIX: Map "completed" to "complete"
            duration: agent.elapsed_seconds || 0,
            data: agent.data,
          };
        }
      });
    }

    // FIX: Convert logs from backend to frontend format and APPEND (don't replace)
    let newLogs = prev.logs;
    const backendLogs = data.logs || data.recent_logs; // Backend sends "logs", not "recent_logs"
    if (backendLogs && Array.isArray(backendLogs) && backendLogs.length > 0) {
      const formattedLogs = backendLogs.map((log: any) => ({
        timestamp: log.timestamp,
        stage: 0, // Backend logs don't have stage numbers
        level: log.level || 'INFO',
        message: log.message,
      }));

      // Only append new logs (avoid duplicates based on timestamp+message)
      const existingLogKeys = new Set(prev.logs.map(l => `${l.timestamp}:${l.message}`));
      const newBackendLogs = formattedLogs.filter(l => !existingLogKeys.has(`${l.timestamp}:${l.message}`));
      newLogs = [...prev.logs, ...newBackendLogs];
    }

    // FIX: Determine current stage from agents
    let currentStage = prev.currentStage;
    if (data.agents) {
      const runningAgentIndex = data.agents.findIndex((a: any) => a.status === 'running');
      if (runningAgentIndex >= 0) {
        currentStage = runningAgentIndex + 1;
      }
    }

    return {
      ...prev,
      customerUrl: data.customer_url || prev.customerUrl, // FIX: Extract customer_url from backend
      stages: newStages,
      currentStage,
      currentMessage: data.current_phase || prev.currentMessage,
      logs: newLogs,
      progressPercentage: data.overall_progress || prev.progressPercentage,
      isComplete: data.status === 'completed',
      isFailed: data.status === 'failed',
      metadata: data.metadata || prev.metadata,
    };
  }, []);

  // Fetch initial job status
  const fetchInitialStatus = useCallback(async () => {
    try {
      const response = await fetch(`/api/provision/status/${jobId}`);
      const data = await response.json();

      setState((prev) => processBackendData(data, prev));
    } catch (error) {
      console.error('Error fetching initial status:', error);
    }
  }, [jobId, processBackendData]);

  // Real SSE connection
  const connectSSE = useCallback(() => {
    const eventSource = new EventSource(`/api/provision/stream/${jobId}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setState((prev) => processBackendData(data, prev));
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      eventSource.close();

      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (!state.isComplete && !state.isFailed) {
          connectSSE();
        }
      }, 3000);
    };

    eventSourceRef.current = eventSource;
  }, [jobId, state.isComplete, state.isFailed]);

  // Initialize connection
  useEffect(() => {
    if (mockMode) {
      startMockSSE();
    } else {
      // Fetch initial status first, then connect to SSE for real-time updates
      fetchInitialStatus().then(() => {
        connectSSE();
      });
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (mockTimerRef.current) {
        clearInterval(mockTimerRef.current);
      }
    };
  }, [mockMode, connectSSE, startMockSSE, fetchInitialStatus]);

  return state;
};
