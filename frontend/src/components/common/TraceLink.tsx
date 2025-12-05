import { ExternalLink, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../utils/cn';

interface TraceLinkProps {
  traceId: string;
  traceUrl: string;
  className?: string;
}

export function TraceLink({ traceId, traceUrl, className }: TraceLinkProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(traceId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <a
        href={traceUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2 text-sky-600 hover:text-sky-700 hover:underline"
      >
        <ExternalLink className="w-4 h-4" />
        <span className="text-sm font-medium">
          View Trace: {traceId.slice(0, 12)}...
        </span>
      </a>
      <button
        onClick={handleCopy}
        className="p-1 rounded hover:bg-gray-100 transition-colors"
        title="Copy trace ID"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-600" />
        ) : (
          <Copy className="w-4 h-4 text-gray-400" />
        )}
      </button>
    </div>
  );
}

export default TraceLink;
