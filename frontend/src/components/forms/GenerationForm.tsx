import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, X, Sparkles, Upload, FileText } from 'lucide-react';
import { useState, useRef } from 'react';
import { Button } from '../common/Button';
import { useLanguages } from '../../hooks/useLanguages';
import { cn } from '../../utils/cn';
import { geoApi } from '../../api/endpoints';
import type { ContentGenerationRequest } from '../../api/types';

const formSchema = z.object({
  client_name: z.string().min(1, 'Client name is required'),
  target_question: z.string().min(10, 'Question must be at least 10 characters'),
  language_override: z.string().optional(),
  target_word_count: z.number().min(100).max(3000).optional(),
});

type FormData = z.infer<typeof formSchema>;

interface GenerationFormProps {
  onSubmit: (data: ContentGenerationRequest) => void;
  isSubmitting?: boolean;
  disabled?: boolean;
}

export function GenerationForm({ onSubmit, isSubmitting, disabled }: GenerationFormProps) {
  const [urls, setUrls] = useState<string[]>([]);
  const [urlInput, setUrlInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<{ name: string; path: string }[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { languages, isLoading: languagesLoading } = useLanguages();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      target_word_count: 500,
    },
  });

  const wordCount = watch('target_word_count') || 500;

  const addUrl = () => {
    if (urlInput.trim() && !urls.includes(urlInput.trim())) {
      setUrls([...urls, urlInput.trim()]);
      setUrlInput('');
    }
  };

  const removeUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
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

  const handleFormSubmit = (data: FormData) => {
    onSubmit({
      ...data,
      reference_urls: urls.length > 0 ? urls : undefined,
      reference_documents: uploadedFiles.length > 0 ? uploadedFiles.map((f) => f.path) : undefined,
      language_override: data.language_override || undefined,
      target_word_count: data.target_word_count || 500,
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Client Name */}
      <div>
        <label htmlFor="client_name" className="block text-sm font-medium text-gray-700 mb-1">
          Client / Entity Name <span className="text-red-500">*</span>
        </label>
        <input
          id="client_name"
          type="text"
          {...register('client_name')}
          className={cn(
            'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500',
            errors.client_name ? 'border-red-500' : 'border-slate-300'
          )}
          placeholder="e.g., Ocean Park Hong Kong"
          disabled={disabled}
        />
        {errors.client_name && (
          <p className="mt-1 text-sm text-red-500">{errors.client_name.message}</p>
        )}
      </div>

      {/* Target Question */}
      <div>
        <label htmlFor="target_question" className="block text-sm font-medium text-gray-700 mb-1">
          Target Question <span className="text-red-500">*</span>
        </label>
        <textarea
          id="target_question"
          {...register('target_question')}
          rows={3}
          className={cn(
            'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500',
            errors.target_question ? 'border-red-500' : 'border-slate-300'
          )}
          placeholder="e.g., What are the main attractions at Ocean Park Hong Kong?"
          disabled={disabled}
        />
        {errors.target_question && (
          <p className="mt-1 text-sm text-red-500">{errors.target_question.message}</p>
        )}
      </div>

      {/* Target Word Count */}
      <div>
        <label htmlFor="target_word_count" className="block text-sm font-medium text-gray-700 mb-1">
          Target Word Count
        </label>
        <div className="flex items-center gap-4">
          <input
            id="target_word_count"
            type="range"
            min={100}
            max={3000}
            step={100}
            defaultValue={500}
            {...register('target_word_count', { valueAsNumber: true })}
            className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
            disabled={disabled}
          />
          <span className="w-24 text-center text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded">
            {wordCount} words
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-500">Range: 100 - 3000 words</p>
      </div>

      {/* Reference URLs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reference URLs (Optional)
        </label>
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

      {/* Reference Files (PDF/DOCX) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reference Files (Optional)
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Upload PDF, DOCX, or TXT files to use as reference material
        </p>
        <div className="flex gap-2 mb-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md"
            multiple
            onChange={handleFileSelect}
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
            {isUploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </div>
        {uploadError && (
          <p className="text-sm text-red-500 mb-2">{uploadError}</p>
        )}
        {uploadedFiles.length > 0 && (
          <div className="flex flex-wrap gap-2">
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
          Language (Optional - auto-detected if not set)
        </label>
        <select
          id="language_override"
          {...register('language_override')}
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
          disabled={disabled || languagesLoading}
        >
          <option value="">Auto-detect</option>
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
        leftIcon={<Sparkles className="w-5 h-5" />}
      >
        Generate GEO-Optimized Content
      </Button>
    </form>
  );
}

export default GenerationForm;
