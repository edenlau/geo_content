import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, X, RefreshCw, Upload, FileText, Link, Eye, Loader2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { useLanguages } from '../../hooks/useLanguages';
import { cn } from '../../utils/cn';
import { geoApi } from '../../api/endpoints';
import type { ContentRewriteRequest, UrlContentPreview, RewriteStyleInfo, RewriteToneInfo } from '../../api/types';

const formSchema = z.object({
  source_url: z.string().url().optional().or(z.literal('')),
  style: z.enum(['professional', 'casual', 'academic', 'journalistic', 'marketing']),
  tone: z.enum(['neutral', 'enthusiastic', 'authoritative', 'conversational']),
  preserve_structure: z.boolean(),
  use_original_length: z.boolean(),
  target_word_count: z.number().min(100).max(5000).optional(),
  client_name: z.string().optional(),
  language_override: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface RewriteFormProps {
  onSubmit: (data: ContentRewriteRequest) => void;
  isSubmitting?: boolean;
  disabled?: boolean;
  onFetchPreview?: (url: string) => Promise<UrlContentPreview | null>;
  preview?: UrlContentPreview | null;
  isFetchingPreview?: boolean;
  previewError?: string | null;
  onClearPreview?: () => void;
}

export function RewriteForm({
  onSubmit,
  isSubmitting,
  disabled,
  onFetchPreview,
  preview,
  isFetchingPreview,
  previewError,
  onClearPreview,
}: RewriteFormProps) {
  const [urls, setUrls] = useState<string[]>([]);
  const [urlInput, setUrlInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<{ name: string; path: string }[]>([]);
  const [sourceFile, setSourceFile] = useState<{ name: string; path: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [styles, setStyles] = useState<RewriteStyleInfo[]>([]);
  const [tones, setTones] = useState<RewriteToneInfo[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const sourceFileInputRef = useRef<HTMLInputElement>(null);
  const { languages, isLoading: languagesLoading } = useLanguages();

  // Fetch styles and tones on mount
  useEffect(() => {
    const fetchStylesAndTones = async () => {
      try {
        const response = await geoApi.getRewriteStyles();
        setStyles(response.data.styles);
        setTones(response.data.tones);
      } catch (error) {
        console.error('Failed to fetch styles and tones:', error);
        // Use defaults if API fails
        setStyles([
          { id: 'professional', name: 'Professional', description: 'Formal business language' },
          { id: 'casual', name: 'Casual', description: 'Friendly, conversational' },
          { id: 'academic', name: 'Academic', description: 'Scholarly with citations' },
          { id: 'journalistic', name: 'Journalistic', description: 'News reporting style' },
          { id: 'marketing', name: 'Marketing', description: 'Persuasive, benefit-focused' },
        ]);
        setTones([
          { id: 'neutral', name: 'Neutral', description: 'Balanced and objective' },
          { id: 'enthusiastic', name: 'Enthusiastic', description: 'Energetic and positive' },
          { id: 'authoritative', name: 'Authoritative', description: 'Expert and confident' },
          { id: 'conversational', name: 'Conversational', description: 'Direct and personal' },
        ]);
      }
    };
    fetchStylesAndTones();
  }, []);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      style: 'professional',
      tone: 'neutral',
      preserve_structure: true,
      use_original_length: true,
    },
  });

  const sourceUrl = watch('source_url');
  const wordCount = watch('target_word_count');
  const useOriginalLength = watch('use_original_length');

  const handleFetchPreview = async () => {
    if (sourceUrl && onFetchPreview) {
      await onFetchPreview(sourceUrl);
    }
  };

  const addUrl = () => {
    if (urlInput.trim() && !urls.includes(urlInput.trim())) {
      setUrls([...urls, urlInput.trim()]);
      setUrlInput('');
    }
  };

  const removeUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const handleSourceFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const fileArray = Array.from(files);
      const response = await geoApi.uploadFiles(fileArray);

      if (response.data.uploaded_files.length > 0) {
        setSourceFile({
          name: fileArray[0]?.name || 'Unknown',
          path: response.data.uploaded_files[0],
        });
        // Clear URL if file is selected
        setValue('source_url', '');
        onClearPreview?.();
      }

      if (response.data.errors && response.data.errors.length > 0) {
        setUploadError(response.data.errors.join(', '));
      }
    } catch (error) {
      setUploadError('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
      if (sourceFileInputRef.current) {
        sourceFileInputRef.current.value = '';
      }
    }
  };

  const handleReferenceFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const fileArray = Array.from(files);
      const response = await geoApi.uploadFiles(fileArray);

      if (response.data.uploaded_files.length > 0) {
        const newFiles = response.data.uploaded_files.map((path, index) => ({
          name: fileArray[index]?.name || path.split('/').pop() || 'Unknown',
          path,
        }));
        setUploadedFiles((prev) => [...prev, ...newFiles]);
      }

      if (response.data.errors && response.data.errors.length > 0) {
        setUploadError(response.data.errors.join(', '));
      }
    } catch (error) {
      setUploadError('Failed to upload files. Please try again.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index));
  };

  const clearSourceFile = () => {
    setSourceFile(null);
  };

  const handleFormSubmit = (data: FormData) => {
    // Require either source URL or source file
    if (!data.source_url && !sourceFile) {
      setUploadError('Please provide a URL or upload a file to rewrite');
      return;
    }

    onSubmit({
      source_url: data.source_url || undefined,
      source_file_path: sourceFile?.path || undefined,
      style: data.style,
      tone: data.tone,
      preserve_structure: data.preserve_structure,
      target_word_count: data.use_original_length ? undefined : (data.target_word_count || 500),
      reference_urls: urls.length > 0 ? urls : undefined,
      reference_documents: uploadedFiles.length > 0 ? uploadedFiles.map((f) => f.path) : undefined,
      client_name: data.client_name || undefined,
      language_override: data.language_override || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Source Content Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Source Content</h3>
        <p className="text-sm text-gray-500">
          Provide a URL or upload a file containing the content you want to rewrite
        </p>

        {/* Source URL */}
        <div>
          <label htmlFor="source_url" className="block text-sm font-medium text-gray-700 mb-1">
            Source URL
          </label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                id="source_url"
                type="url"
                {...register('source_url')}
                className={cn(
                  'w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500',
                  errors.source_url ? 'border-red-500' : 'border-slate-300'
                )}
                placeholder="https://example.com/article"
                disabled={disabled || !!sourceFile}
              />
            </div>
            <Button
              type="button"
              variant="outline"
              onClick={handleFetchPreview}
              disabled={disabled || !sourceUrl || isFetchingPreview || !!sourceFile}
              leftIcon={isFetchingPreview ? <Loader2 className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
            >
              Preview
            </Button>
          </div>
          {errors.source_url && (
            <p className="mt-1 text-sm text-red-500">{errors.source_url.message}</p>
          )}
        </div>

        {/* URL Preview */}
        {preview && (
          <Card className="bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-medium text-gray-900">{preview.title}</h4>
              <button
                type="button"
                onClick={onClearPreview}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-2">{preview.content_preview}</p>
            <div className="flex gap-4 text-xs text-gray-500">
              <span>{preview.word_count} words</span>
              <span>{preview.language}</span>
              <span>Fetched in {preview.fetch_time_ms}ms</span>
            </div>
          </Card>
        )}

        {previewError && (
          <p className="text-sm text-red-500">{previewError}</p>
        )}

        {/* OR Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-gray-500">OR</span>
          </div>
        </div>

        {/* Source File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Upload Source File
          </label>
          <input
            ref={sourceFileInputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleSourceFileSelect}
            className="hidden"
            disabled={disabled || isUploading}
          />
          {sourceFile ? (
            <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <FileText className="w-5 h-5 text-amber-600" />
              <span className="flex-1 truncate">{sourceFile.name}</span>
              <button
                type="button"
                onClick={clearSourceFile}
                className="p-1 hover:bg-amber-100 rounded"
                disabled={disabled}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Button
              type="button"
              variant="outline"
              onClick={() => sourceFileInputRef.current?.click()}
              disabled={disabled || isUploading || !!sourceUrl}
              leftIcon={<Upload className="w-4 h-4" />}
              isLoading={isUploading}
              className="w-full"
            >
              {isUploading ? 'Uploading...' : 'Upload File (PDF, DOCX, TXT, MD)'}
            </Button>
          )}
        </div>
      </div>

      {/* Style and Tone Section */}
      <div className="grid grid-cols-2 gap-4">
        {/* Style */}
        <div>
          <label htmlFor="style" className="block text-sm font-medium text-gray-700 mb-1">
            Writing Style
          </label>
          <select
            id="style"
            {...register('style')}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            disabled={disabled}
          >
            {styles.map((style) => (
              <option key={style.id} value={style.id}>
                {style.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {styles.find((s) => s.id === watch('style'))?.description}
          </p>
        </div>

        {/* Tone */}
        <div>
          <label htmlFor="tone" className="block text-sm font-medium text-gray-700 mb-1">
            Tone
          </label>
          <select
            id="tone"
            {...register('tone')}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            disabled={disabled}
          >
            {tones.map((tone) => (
              <option key={tone.id} value={tone.id}>
                {tone.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {tones.find((t) => t.id === watch('tone'))?.description}
          </p>
        </div>
      </div>

      {/* Preserve Structure Toggle */}
      <div className="flex items-center gap-3">
        <input
          id="preserve_structure"
          type="checkbox"
          {...register('preserve_structure')}
          className="w-4 h-4 text-amber-500 border-gray-300 rounded focus:ring-amber-500"
          disabled={disabled}
        />
        <label htmlFor="preserve_structure" className="text-sm text-gray-700">
          Preserve original structure (headings, sections)
        </label>
      </div>

      {/* Target Word Count */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <input
            id="use_original_length"
            type="checkbox"
            {...register('use_original_length')}
            className="w-4 h-4 text-amber-500 border-gray-300 rounded focus:ring-amber-500"
            disabled={disabled}
          />
          <label htmlFor="use_original_length" className="text-sm font-medium text-gray-700">
            Use original content length
          </label>
        </div>

        {!useOriginalLength && (
          <div className="pl-7">
            <label htmlFor="target_word_count" className="block text-sm text-gray-600 mb-2">
              Target Word Count
            </label>
            <div className="flex items-center gap-4">
              <input
                id="target_word_count"
                type="range"
                min={100}
                max={5000}
                step={100}
                {...register('target_word_count', { valueAsNumber: true })}
                className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
                disabled={disabled}
              />
              <span className="w-24 text-center text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded">
                {wordCount || 500} words
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Client Name (Optional) */}
      <div>
        <label htmlFor="client_name" className="block text-sm font-medium text-gray-700 mb-1">
          Client / Entity Name (Optional - for entity optimization)
        </label>
        <input
          id="client_name"
          type="text"
          {...register('client_name')}
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
          placeholder="e.g., Ocean Park Hong Kong"
          disabled={disabled}
        />
      </div>

      {/* Reference URLs for Research */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reference URLs for Research Enhancement (Optional)
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Add URLs to gather additional facts, statistics, and citations
        </p>
        <div className="flex gap-2 mb-2">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addUrl())}
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            placeholder="https://example.com"
            disabled={disabled}
          />
          <Button
            type="button"
            variant="outline"
            onClick={addUrl}
            disabled={disabled || !urlInput.trim()}
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
        {urls.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {urls.map((url, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 rounded-full text-sm"
              >
                <span className="max-w-[200px] truncate">{url}</span>
                <button
                  type="button"
                  onClick={() => removeUrl(index)}
                  className="p-0.5 hover:bg-gray-200 rounded-full"
                  disabled={disabled}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Reference Files for Research */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reference Files for Research Enhancement (Optional)
        </label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.txt,.md"
          multiple
          onChange={handleReferenceFileSelect}
          className="hidden"
          disabled={disabled || isUploading}
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isUploading}
          leftIcon={<Upload className="w-4 h-4" />}
          isLoading={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Reference Files'}
        </Button>
        {uploadError && (
          <p className="text-sm text-red-500 mt-2">{uploadError}</p>
        )}
        {uploadedFiles.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {uploadedFiles.map((file, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-3 py-1 bg-amber-50 border border-amber-200 rounded-full text-sm"
              >
                <FileText className="w-3 h-3 text-amber-600" />
                <span className="max-w-[200px] truncate">{file.name}</span>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="p-0.5 hover:bg-amber-100 rounded-full"
                  disabled={disabled}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Language Override */}
      <div>
        <label htmlFor="language_override" className="block text-sm font-medium text-gray-700 mb-1">
          Language Override (Optional - preserves original language if not set)
        </label>
        <select
          id="language_override"
          {...register('language_override')}
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
          disabled={disabled || languagesLoading}
        >
          <option value="">Preserve original language</option>
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name} ({lang.code})
            </option>
          ))}
        </select>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        size="lg"
        className="w-full"
        isLoading={isSubmitting}
        disabled={disabled}
        leftIcon={<RefreshCw className="w-5 h-5" />}
      >
        Rewrite with GEO Optimization
      </Button>
    </form>
  );
}

export default RewriteForm;
