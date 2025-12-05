import { RefreshCw, Download, History, Clock } from 'lucide-react';
import { useState, useEffect } from 'react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { GenerationForm } from '../components/forms/GenerationForm';
import { JobStatusCard } from '../components/status/JobStatusCard';
import { ProgressIndicator } from '../components/status/ProgressIndicator';
import { ContentDisplay } from '../components/results/ContentDisplay';
import { EvaluationScores } from '../components/results/EvaluationScores';
import { GeoCommentary } from '../components/results/GeoCommentary';
import { GeoInsights } from '../components/results/GeoInsights';
import { TraceLink } from '../components/common/TraceLink';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useContentGeneration } from '../hooks/useContentGeneration';
import { formatDuration } from '../utils/formatters';
import { geoApi } from '../api/endpoints';
import type { JobHistoryItem } from '../api/types';

export function Generate() {
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
  } = useContentGeneration();

  const [jobHistory, setJobHistory] = useState<JobHistoryItem[]>([]);
  const [isDownloading, setIsDownloading] = useState(false);

  // Fetch job history on mount and after completion
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await geoApi.getJobHistory();
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
      const response = await geoApi.downloadContent(downloadJobId);
      const blob = new Blob([response.data], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `geo_content_${downloadJobId}.md`;
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

  const isIdle = !jobId && !isSubmitting;
  const isProcessing = isPolling || isSubmitting;
  const isComplete = status === 'completed' && result;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Generate Content</h2>
            <p className="text-gray-500 mt-1">
              Create GEO-optimized content for generative search engines
            </p>
          </div>
          {(isComplete || error) && (
            <Button
              variant="outline"
              onClick={reset}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              New Generation
            </Button>
          )}
        </div>

        {/* Form Section */}
        {isIdle && (
          <Card>
            <GenerationForm
              onSubmit={submit}
              isSubmitting={isSubmitting}
              disabled={isProcessing}
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
            <Card title="Generation Progress">
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
              <p className="text-red-600 font-medium">Generation Failed</p>
              <p className="text-red-500 text-sm mt-2">{error}</p>
              <Button
                variant="outline"
                onClick={reset}
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
                    <p className="text-sm text-gray-500">Generation Time</p>
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
                </div>
                <TraceLink traceId={result.trace_id} traceUrl={result.trace_url} />
              </div>
            </Card>

            {/* Evaluation Scores */}
            <EvaluationScores
              overallScore={result.evaluation_score}
              selectedDraft={result.selected_draft}
              iterations={result.evaluation_iterations}
              geoAnalysis={result.geo_analysis}
              modelsUsed={result.models_used}
            />

            {/* Generated Content */}
            <ContentDisplay
              content={result.content}
              wordCount={result.word_count}
              languageCode={result.language_code}
              writingDirection={result.writing_direction}
              detectedLanguage={result.detected_language}
            />

            {/* GEO Commentary */}
            <GeoCommentary commentary={result.geo_commentary} />

            {/* GEO Insights - NEW Enhanced Insights */}
            {result.geo_insights && <GeoInsights insights={result.geo_insights} />}

            {/* Download Button */}
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Download Content</h3>
                  <p className="text-sm text-gray-500">Save the generated content as a Markdown file</p>
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
          <Card title="Recent Generations" className="mt-8">
            <div className="flex items-center gap-2 mb-4 text-sm text-gray-500">
              <History className="w-4 h-4" />
              <span>Last {jobHistory.length} completed generations</span>
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

export default Generate;
