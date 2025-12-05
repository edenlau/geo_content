import { Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Card } from '../common/Card';
import { cn } from '../../utils/cn';
import { formatDuration } from '../../utils/formatters';
import type { JobStatus } from '../../api/types';

interface JobStatusCardProps {
  jobId: string;
  status: JobStatus;
  elapsedTime: number;
  error?: string | null;
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: 'Pending',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
  },
  processing: {
    icon: Loader2,
    label: 'Processing',
    color: 'text-sky-600',
    bgColor: 'bg-sky-100',
  },
  completed: {
    icon: CheckCircle,
    label: 'Completed',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
  },
  failed: {
    icon: XCircle,
    label: 'Failed',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
  },
};

export function JobStatusCard({ jobId, status, elapsedTime, error }: JobStatusCardProps) {
  const config = statusConfig[status];
  const Icon = config.icon;
  const isAnimated = status === 'processing';

  return (
    <Card className="mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className={cn('p-2 rounded-lg', config.bgColor)}>
            <Icon className={cn('w-6 h-6', config.color, isAnimated && 'animate-spin')} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Job ID</p>
            <p className="font-mono text-sm">{jobId}</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-sm text-gray-500">Status</p>
            <p className={cn('font-medium', config.color)}>{config.label}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Elapsed Time</p>
            <p className="font-medium">{formatDuration(elapsedTime * 1000)}</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </Card>
  );
}

export default JobStatusCard;
