import { RefreshCw, Download, History, Clock, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { RewriteForm } from '../components/forms/RewriteForm';
import { JobStatusCard } from '../components/status/JobStatusCard';
import { ProgressIndicator } from '../components/status/ProgressIndicator';
import { ContentComparison } from '../components/results/ContentComparison';
import { OptimizationsApplied } from '../components/results/OptimizationsApplied';
import { RewriteEvaluationScores } from '../components/results/RewriteEvaluationScores';
import { GeoCommentary } from '../components/results/GeoCommentary';
import { GeoInsights } from '../components/results/GeoInsights';
import { TraceLink } from '../components/common/TraceLink';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useContentRewrite } from '../hooks/useContentRewrite';
import { formatDuration } from '../utils/formatters';
import { geoApi } from '../api/endpoints';
import type { JobHistoryItem } from '../api/types';

export function Rewrite() {
  const {
    submit,
    isSubmitting,
    jobId,
    status,
    result,
    error,
    isPolling,
    elapsedTime,
    reset,
    fetchPreview,
    isFetchingPreview,
    preview,
    clearPreview,
  } = useContentRewrite();

  const [jobHistory, setJobHistory] = useState<JobHistoryItem[]>([]);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  // Fetch job history on mount and after completion
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await geoApi.getJobHistory();
        // Filter for rewrite jobs if we have a way to identify them
        // For now, show all jobs
        setJobHistory(response.data.jobs);
      } catch (err) {
        console.error('Failed to fetch job history:', err);
      }
    };
    fetchHistory();
  }, [status]);

  const handleDownload = async (downloadJobId: string) => {
    setIsDownloading(true);
    try {
      const response = await geoApi.downloadRewrittenContent(downloadJobId);
      const blob = new Blob([response.data], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `geo_rewritten_${downloadJobId}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download content:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all completed jobs?')) {
      return;
    }
    setIsClearing(true);
    try {
      await geoApi.clearJobHistory();
      setJobHistory([]);
    } catch (err) {
      console.error('Failed to clear job history:', err);
    } finally {
      setIsClearing(false);
    }
  };

  const isIdle = !jobId && !isSubmitting;
  const isProcessing = isPolling || isSubmitting;
  const isComplete = status === 'completed' && result;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Rewrite Content</h2>
            <p className="text-gray-500 mt-1">
              Optimize existing content for generative search engines
            </p>
          </div>
          {(isComplete || error) && (
            <Button
              variant="outline"
              onClick={() => {
                reset();
                clearPreview();
              }}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              New Rewrite
            </Button>
          )}
        </div>

        {/* Form Section */}
        {isIdle && (
          <Card>
            <RewriteForm
              onSubmit={submit}
              isSubmitting={isSubmitting}
              disabled={isProcessing}
              onFetchPreview={fetchPreview}
              isFetchingPreview={isFetchingPreview}
              preview={preview}
              onClearPreview={clearPreview}
            />
          </Card>
        )}

        {/* Processing Section */}
        {isProcessing && jobId && status && (
          <div className="space-y-6">
            <JobStatusCard
              jobId={jobId}
              status={status}
              elapsedTime={elapsedTime}
              error={error}
            />
            <Card title="Rewrite Progress">
              <ProgressIndicator
                elapsedTime={elapsedTime}
                isComplete={false}
                error={error}
              />
            </Card>
          </div>
        )}

        {/* Error Display */}
        {error && !isProcessing && (
          <Card className="border-red-200 bg-red-50">
            <div className="text-center py-4">
              <p className="text-red-600 font-medium">Rewrite Failed</p>
              <p className="text-red-500 text-sm mt-2">{error}</p>
              <Button
                variant="outline"
                onClick={() => {
                  reset();
                  clearPreview();
                }}
                className="mt-4"
                leftIcon={<RefreshCw className="w-4 h-4" />}
              >
                Try Again
              </Button>
            </div>
          </Card>
        )}

        {/* Results Section */}
        {isComplete && result && (
          <div className="space-y-6">
            {/* Metadata */}
            <Card>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-6">
                  <div>
                    <p className="text-sm text-gray-500">Rewrite Time</p>
                    <p className="font-medium">{formatDuration(result.generation_time_ms)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Language</p>
                    <p className="font-medium">{result.detected_language}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Direction</p>
                    <p className="font-medium uppercase">{result.writing_direction}</p>
                  </div>
                  {result.style_applied && (
                    <div>
                      <p className="text-sm text-gray-500">Style</p>
                      <p className="font-medium capitalize">{result.style_applied}</p>
                    </div>
                  )}
                  {result.tone_applied && (
                    <div>
                      <p className="text-sm text-gray-500">Tone</p>
                      <p className="font-medium capitalize">{result.tone_applied}</p>
                    </div>
                  )}
                </div>
                <TraceLink traceId={result.trace_id} traceUrl={result.trace_url} />
              </div>
            </Card>

            {/* Content Comparison */}
            {result.comparison && (
              <ContentComparison
                comparison={result.comparison}
                languageCode={result.language_code}
                writingDirection={result.writing_direction}
                detectedLanguage={result.detected_language}
              />
            )}

            {/* GEO Optimizations Applied */}
            {result.optimizations_applied && (
              <OptimizationsApplied optimizations={result.optimizations_applied} />
            )}

            {/* Evaluation Scores */}
            {result.optimizations_applied && (
              <RewriteEvaluationScores
                overallScore={result.evaluation_score}
                iterations={result.evaluation_iterations}
                optimizations={result.optimizations_applied}
                modelsUsed={result.models_used}
              />
            )}

            {/* GEO Commentary */}
            <GeoCommentary commentary={result.geo_commentary} />

            {/* GEO Insights */}
            {result.geo_insights && <GeoInsights insights={result.geo_insights} />}

            {/* Download Button */}
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Download Rewritten Content</h3>
                  <p className="text-sm text-gray-500">Save the optimized content as a Markdown file</p>
                </div>
                <Button
                  onClick={() => handleDownload(jobId!)}
                  disabled={isDownloading}
                  leftIcon={<Download className="w-4 h-4" />}
                  isLoading={isDownloading}
                >
                  Download Markdown
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Job History Section */}
        {jobHistory.length > 0 && (
          <Card title="Recent Jobs" className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <History className="w-4 h-4" />
                <span>Last {jobHistory.length} completed jobs</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearHistory}
                disabled={isClearing}
                leftIcon={<Trash2 className="w-3 h-3" />}
                isLoading={isClearing}
              >
                Clear All
              </Button>
            </div>
            <div className="space-y-3">
              {jobHistory.map((job) => (
                <div
                  key={job.job_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 truncate">{job.client_name}</span>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${
                        job.evaluation_score >= 80 ? 'bg-green-100 text-green-700' :
                        job.evaluation_score >= 70 ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {job.evaluation_score.toFixed(1)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 truncate">{job.target_question}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(job.completed_at).toLocaleString()}
                      </span>
                      <span>{job.word_count} words</span>
                      <span>{formatDuration(job.generation_time_ms)}</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(job.job_id)}
                    disabled={isDownloading}
                    leftIcon={<Download className="w-3 h-3" />}
                  >
                    Download
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Rewrite;
