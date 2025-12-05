import { cn } from '../../utils/cn';
import { formatScore, getScoreColor } from '../../utils/formatters';

interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const sizes = {
  sm: { width: 60, strokeWidth: 4, fontSize: 'text-sm' },
  md: { width: 80, strokeWidth: 5, fontSize: 'text-lg' },
  lg: { width: 120, strokeWidth: 6, fontSize: 'text-2xl' },
};

export function ScoreGauge({ score, label, size = 'md', showLabel = true }: ScoreGaugeProps) {
  const { width, strokeWidth, fontSize } = sizes[size];
  const radius = (width - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 100);
  const offset = circumference - (progress / 100) * circumference;

  const getStrokeColor = (score: number): string => {
    if (score >= 80) return '#22c55e'; // green
    if (score >= 70) return '#84cc16'; // lime
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width, height: width }}>
        <svg className="transform -rotate-90" width={width} height={width}>
          {/* Background circle */}
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={width / 2}
            cy={width / 2}
            r={radius}
            fill="none"
            stroke={getStrokeColor(score)}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out score-gauge"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn('font-bold', fontSize, getScoreColor(score))}>
            {formatScore(score)}
          </span>
        </div>
      </div>
      {showLabel && (
        <span className="mt-2 text-sm text-gray-600 text-center">{label}</span>
      )}
    </div>
  );
}

export default ScoreGauge;
