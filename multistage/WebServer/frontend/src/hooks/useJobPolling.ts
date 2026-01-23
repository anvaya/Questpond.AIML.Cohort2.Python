import { useState, useEffect, useCallback, useRef } from 'react';
import { getJobStatus } from '@/lib/api';
import type { Job } from '@/types';

const POLL_INTERVAL = 2000; // 2 seconds

export function useJobPolling(jobId: string | null) {
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const poll = useCallback(async () => {
    if (!jobId) return;

    try {
      const data = await getJobStatus(jobId);
      setJob(data);

      // Stop polling if job is completed or failed
      if (data.status === 'completed' || data.status === 'failed') {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }

      // Set error message if job failed
      if (data.status === 'failed') {
        setError(data.error_message || data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch job status');
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) return;

    // Initial poll
    poll();

    // Set up polling interval
    intervalRef.current = window.setInterval(poll, POLL_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [jobId, poll]);

  return { job, error, isPolling: job?.status === 'processing' || job?.status === 'queued' };
}
