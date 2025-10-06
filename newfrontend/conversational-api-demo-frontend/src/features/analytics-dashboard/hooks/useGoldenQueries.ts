/**
 * Hook for fetching golden queries from provisioning API
 *
 * Fetches suggested insights that users can quickly add to dashboard
 */

import { useState, useEffect } from 'react';
import { GoldenQuery } from '../types';

export function useGoldenQueries(jobId: string | null) {
  const [goldenQueries, setGoldenQueries] = useState<GoldenQuery[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setGoldenQueries([]);
      return;
    }

    const fetchGoldenQueries = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/provision/assets/${jobId}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch golden queries: ${response.statusText}`);
        }

        const data = await response.json();
        setGoldenQueries(data.golden_queries || []);
      } catch (err) {
        console.error('Error fetching golden queries:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setGoldenQueries([]);
      } finally {
        setLoading(false);
      }
    };

    fetchGoldenQueries();
  }, [jobId]);

  return {
    goldenQueries,
    loading,
    error
  };
}
