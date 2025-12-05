import { useState, useCallback } from 'react';
import { geoApi } from '../api/endpoints';
import { useJobPolling } from './useJobPolling';
import type { ContentGenerationRequest, ContentGenerationResponse } from '../api/types';

interface UseContentGenerationResult {
  // Form submission
  submit: (data: ContentGenerationRequest) => Promise<void>;

  // State
  isSubmitting: boolean;
  jobId: string | null;

  // From polling
  status: ReturnType<typeof useJobPolling>['status'];
  result: ContentGenerationResponse | null;
  error: string | null;
  isPolling: boolean;
  elapsedTime: number;
  estimatedProgress: number;

  // Actions
  reset: () => void;
}

export function useContentGeneration(): UseContentGenerationResult {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    status,
    result,
    error: pollingError,
    isPolling,
    elapsedTime,
    estimatedProgress,
    stop,
  } = useJobPolling(jobId);

  const submit = useCallback(async (data: ContentGenerationRequest) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setJobId(null);

    try {
      const response = await geoApi.generateAsync(data);
      setJobId(response.data.job_id);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start generation';
      setSubmitError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  const reset = useCallback(() => {
    stop();
    setJobId(null);
    setSubmitError(null);
    setIsSubmitting(false);
  }, [stop]);

  return {
    submit,
    isSubmitting,
    jobId,
    status,
    result,
    error: submitError || pollingError,
    isPolling,
    elapsedTime,
    estimatedProgress,
    reset,
  };
}

export default useContentGeneration;
