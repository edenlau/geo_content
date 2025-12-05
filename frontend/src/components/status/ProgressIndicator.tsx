import { Check, Loader2, Circle } from 'lucide-react';
import { cn } from '../../utils/cn';

interface Step {
  id: string;
  label: string;
  description: string;
}

const GENERATION_STEPS: Step[] = [
  { id: 'language', label: 'Language Detection', description: 'Detecting input language' },
  { id: 'research', label: 'Research & Harvesting', description: 'Gathering information from sources' },
  { id: 'draft_a', label: 'Draft A (GPT)', description: 'Generating content with GPT-4.1-mini' },
  { id: 'draft_b', label: 'Draft B (Claude)', description: 'Generating content with Claude 3.5 Haiku' },
  { id: 'evaluation', label: 'Evaluation', description: 'Comparing and scoring drafts' },
  { id: 'commentary', label: 'GEO Commentary', description: 'Generating performance analysis' },
];

interface ProgressIndicatorProps {
  elapsedTime: number;
  isComplete?: boolean;
  error?: string | null;
}

export function ProgressIndicator({ elapsedTime, isComplete, error }: ProgressIndicatorProps) {
  // Estimate current step based on elapsed time
  const estimatedSteps = [
    { threshold: 2, step: 0 },   // Language detection: ~2s
    { threshold: 15, step: 1 },  // Research: ~15s
    { threshold: 35, step: 2 },  // Draft A: ~20s
    { threshold: 55, step: 3 },  // Draft B: ~20s (parallel but show sequentially)
    { threshold: 70, step: 4 },  // Evaluation: ~15s
    { threshold: 80, step: 5 },  // Commentary: ~10s
  ];

  let currentStep = 0;
  for (const { threshold, step } of estimatedSteps) {
    if (elapsedTime >= threshold) currentStep = step;
  }

  if (isComplete) currentStep = GENERATION_STEPS.length;

  return (
    <div className="py-4">
      <div className="space-y-4">
        {GENERATION_STEPS.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep && !isComplete && !error;
          const isPending = index > currentStep;

          return (
            <div key={step.id} className="flex items-start gap-4">
              {/* Step indicator */}
              <div className="flex-shrink-0 relative">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center',
                    isCompleted && 'bg-green-500 text-white',
                    isCurrent && 'bg-sky-500 text-white',
                    isPending && 'bg-gray-200 text-gray-400',
                    error && isCurrent && 'bg-red-500 text-white'
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-5 h-5" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Circle className="w-5 h-5" />
                  )}
                </div>
                {/* Connector line */}
                {index < GENERATION_STEPS.length - 1 && (
                  <div
                    className={cn(
                      'absolute left-1/2 top-8 w-0.5 h-8 -translate-x-1/2',
                      isCompleted ? 'bg-green-500' : 'bg-gray-200'
                    )}
                  />
                )}
              </div>

              {/* Step content */}
              <div className="flex-1 min-w-0 pb-8">
                <p
                  className={cn(
                    'font-medium',
                    isCompleted && 'text-green-600',
                    isCurrent && 'text-sky-600',
                    isPending && 'text-gray-400'
                  )}
                >
                  {step.label}
                </p>
                <p className="text-sm text-gray-500 mt-0.5">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ProgressIndicator;
