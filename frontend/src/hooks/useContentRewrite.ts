import { useState, useCallback } from 'react';
import { geoApi } from '../api/endpoints';
import { useRewriteJobPolling } from './useRewriteJobPolling';
import type { ContentRewriteRequest, ContentRewriteResponse, UrlContentPreview } from '../api/types';

interface UseContentRewriteResult {
  // Form submission
  submit: (data: ContentRewriteRequest) => Promise<void>;

  // URL preview
  fetchPreview: (url: string) => Promise<UrlContentPreview | null>;
  preview: UrlContentPreview | null;
  isFetchingPreview: boolean;
  previewError: string | null;

  // State
  isSubmitting: boolean;
  jobId: string | null;

  // From polling
  status: ReturnType<typeof useRewriteJobPolling>['status'];
  result: ContentRewriteResponse | null;
  error: string | null;
  isPolling: boolean;
  elapsedTime: number;
  estimatedProgress: number;

  // Actions
  reset: () => void;
  clearPreview: () => void;
}

export function useContentRewrite(): UseContentRewriteResult {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // URL preview state
  const [preview, setPreview] = useState<UrlContentPreview | null>(null);
  const [isFetchingPreview, setIsFetchingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const {
    status,
    result,
    error: pollingError,
    isPolling,
    elapsedTime,
    estimatedProgress,
    stop,
  } = useRewriteJobPolling(jobId);

  const fetchPreview = useCallback(async (url: string): Promise<UrlContentPreview | null> => {
    setIsFetchingPreview(true);
    setPreviewError(null);

    try {
      const response = await geoApi.fetchUrlContent(url);
      setPreview(response.data);
      return response.data;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch URL content';
      setPreviewError(errorMsg);
      setPreview(null);
      return null;
    } finally {
      setIsFetchingPreview(false);
    }
  }, []);

  const clearPreview = useCallback(() => {
    setPreview(null);
    setPreviewError(null);
  }, []);

  const submit = useCallback(async (data: ContentRewriteRequest) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setJobId(null);

    try {
      const response = await geoApi.rewriteAsync(data);
      setJobId(response.data.job_id);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start rewrite';
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
    setPreview(null);
    setPreviewError(null);
  }, [stop]);

  return {
    submit,
    fetchPreview,
    preview,
    isFetchingPreview,
    previewError,
    isSubmitting,
    jobId,
    status,
    result,
    error: submitError || pollingError,
    isPolling,
    elapsedTime,
    estimatedProgress,
    reset,
    clearPreview,
  };
}

export default useContentRewrite;
