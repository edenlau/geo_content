import { useState, useEffect, useCallback, useRef } from 'react';
import { geoApi } from '../api/endpoints';
import type { ContentRewriteResponse, JobStatus } from '../api/types';

interface UseRewriteJobPollingOptions {
  interval?: number;       // Base polling interval in ms (default: 2000)
  maxAttempts?: number;    // Max polling attempts (default: 300 = ~10 min)
  onComplete?: (result: ContentRewriteResponse) => void;
  onError?: (error: string) => void;
}

interface UseRewriteJobPollingResult {
  status: JobStatus | null;
  result: ContentRewriteResponse | null;
  error: string | null;
  isPolling: boolean;
  attempts: number;
  elapsedTime: number;
  estimatedProgress: number;
  stop: () => void;
}

// Estimated step durations for rewrite progress calculation (in seconds)
const STEP_DURATIONS = {
  content_extraction: 5,
  language_detection: 2,
  research: 15,
  rewrite: 25,
  evaluation: 15,
  analysis: 8,
};

const TOTAL_ESTIMATED_TIME = Object.values(STEP_DURATIONS).reduce((a, b) => a + b, 0);

export function useRewriteJobPolling(
  jobId: string | null,
  options: UseRewriteJobPollingOptions = {}
): UseRewriteJobPollingResult {
  const {
    interval = 2000,
    maxAttempts = 300,
    onComplete,
    onError,
  } = options;

  const [status, setStatus] = useState<JobStatus | null>(null);
  const [result, setResult] = useState<ContentRewriteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Use refs to avoid React batching issues and prevent duplicate polling loops
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);
  const consecutiveErrorsRef = useRef(0);
  const attemptsRef = useRef(0);
  const isPollingActiveRef = useRef(false);
  const MAX_CONSECUTIVE_ERRORS = 3;

  // Calculate estimated progress based on elapsed time
  const estimatedProgress = Math.min(
    (elapsedTime / TOTAL_ESTIMATED_TIME) * 100,
    95 // Cap at 95% until complete
  );

  const stop = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    isPollingActiveRef.current = false;
    setIsPolling(false);
  }, []);

  const poll = useCallback(async () => {
    // Guard: Don't poll if not active, not mounted, or no jobId
    if (!jobId || !isMountedRef.current || !isPollingActiveRef.current) return;

    try {
      const response = await geoApi.getRewriteJobStatus(jobId);
      const data = response.data;

      if (!isMountedRef.current || !isPollingActiveRef.current) return;

      // Reset consecutive errors on successful response
      consecutiveErrorsRef.current = 0;
      setStatus(data.status);

      if (data.status === 'completed' && data.result) {
        setResult(data.result);
        isPollingActiveRef.current = false;
        setIsPolling(false);
        onComplete?.(data.result);
        return;
      }

      if (data.status === 'failed') {
        const errorMsg = data.error || 'Rewrite job failed';
        setError(errorMsg);
        isPollingActiveRef.current = false;
        setIsPolling(false);
        onError?.(errorMsg);
        return;
      }

      // Increment attempts using ref (avoids React batching issues)
      attemptsRef.current += 1;
      setAttempts(attemptsRef.current); // Sync state for UI

      if (attemptsRef.current >= maxAttempts) {
        setError('Polling timeout - rewrite took too long');
        isPollingActiveRef.current = false;
        setIsPolling(false);
        onError?.('Polling timeout');
        return;
      }

      // Continue polling with exponential backoff
      // Start at 2s, increase by 30% every 15 attempts, max 8s
      const backoffFactor = Math.pow(1.3, Math.floor(attemptsRef.current / 15));
      const delay = Math.min(interval * backoffFactor, 8000);

      timeoutRef.current = setTimeout(poll, delay);
    } catch (err) {
      if (!isMountedRef.current || !isPollingActiveRef.current) return;

      consecutiveErrorsRef.current += 1;

      // Only stop polling if we hit max consecutive errors
      if (consecutiveErrorsRef.current >= MAX_CONSECUTIVE_ERRORS) {
        const errorMsg = err instanceof Error ? err.message : 'Polling error';
        setError(errorMsg);
        isPollingActiveRef.current = false;
        setIsPolling(false);
        onError?.(errorMsg);
      } else {
        // Retry after a delay on transient errors
        timeoutRef.current = setTimeout(poll, 2000);
      }
    }
  }, [jobId, interval, maxAttempts, onComplete, onError]);

  // Start polling when jobId changes
  useEffect(() => {
    if (!jobId) {
      setStatus(null);
      setResult(null);
      setError(null);
      setAttempts(0);
      setElapsedTime(0);
      setStartTime(null);
      attemptsRef.current = 0;
      isPollingActiveRef.current = false;
      return;
    }

    // Prevent multiple polling loops (important for StrictMode)
    if (isPollingActiveRef.current) {
      return;
    }

    // Reset state for new job
    setStatus('pending');
    setResult(null);
    setError(null);
    setAttempts(0);
    setIsPolling(true);
    setStartTime(Date.now());

    // Reset refs
    attemptsRef.current = 0;
    consecutiveErrorsRef.current = 0;
    isPollingActiveRef.current = true;

    // Start polling
    poll();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      isPollingActiveRef.current = false;
    };
  }, [jobId, poll]);

  // Update elapsed time
  useEffect(() => {
    if (!isPolling || !startTime) return;

    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [isPolling, startTime]);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      isPollingActiveRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    status,
    result,
    error,
    isPolling,
    attempts,
    elapsedTime,
    estimatedProgress,
    stop,
  };
}

export default useRewriteJobPolling;
