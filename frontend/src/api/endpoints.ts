import apiClient from './client';
import type {
  ContentGenerationRequest,
  ContentGenerationResponse,
  AsyncJobResponse,
  JobStatusResponse,
  LanguagesResponse,
  StrategiesResponse,
  HealthResponse,
  FileUploadResponse,
  JobHistoryResponse,
} from './types';

export const geoApi = {
  // Health check
  health: () =>
    apiClient.get<HealthResponse>('/health', {
      timeout: 5000, // 5 seconds - health checks should be quick
    }),

  // Get supported languages
  getLanguages: () =>
    apiClient.get<LanguagesResponse>('/languages'),

  // Get GEO strategies
  getStrategies: () =>
    apiClient.get<StrategiesResponse>('/strategies'),

  // Synchronous content generation (not recommended for UI - long running)
  generateSync: (data: ContentGenerationRequest) =>
    apiClient.post<ContentGenerationResponse>('/generate', data, {
      timeout: 300000, // 5 minutes for sync
    }),

  // Async content generation (recommended)
  generateAsync: (data: ContentGenerationRequest) =>
    apiClient.post<AsyncJobResponse>('/generate/async', data, {
      timeout: 60000, // 60 seconds for async job start
    }),

  // Poll job status (use shorter timeout since polling is frequent)
  getJobStatus: (jobId: string) =>
    apiClient.get<JobStatusResponse>(`/jobs/${jobId}`, {
      timeout: 10000, // 10 seconds - polling requests should be quick
    }),

  // Upload reference files
  uploadFiles: (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    return apiClient.post<FileUploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload
    });
  },

  // Get job history
  getJobHistory: () =>
    apiClient.get<JobHistoryResponse>('/history'),

  // Download generated content
  downloadContent: (jobId: string) =>
    apiClient.get(`/jobs/${jobId}/download`, {
      responseType: 'blob',
      timeout: 30000,
    }),
};

export default geoApi;
