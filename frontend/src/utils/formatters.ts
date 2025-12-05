import { format, formatDistanceToNow } from 'date-fns';

/**
 * Format milliseconds to human-readable duration
 */
export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) return `${minutes}m ${remainingSeconds}s`;

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Format a date string to relative time
 */
export function formatRelativeTime(dateString: string): string {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
}

/**
 * Format a date string to a readable format
 */
export function formatDate(dateString: string): string {
  return format(new Date(dateString), 'MMM d, yyyy h:mm a');
}

/**
 * Format a score (0-100) to display format
 */
export function formatScore(score: number): string {
  return score.toFixed(1);
}

/**
 * Get score color class based on value
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-geo-excellent';
  if (score >= 70) return 'text-geo-good';
  if (score >= 60) return 'text-geo-adequate';
  return 'text-geo-poor';
}

/**
 * Get score background color class based on value
 */
export function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-geo-excellent';
  if (score >= 70) return 'bg-geo-good';
  if (score >= 60) return 'bg-geo-adequate';
  return 'bg-geo-poor';
}

/**
 * Format word count with comma separators
 */
export function formatWordCount(count: number): string {
  return count.toLocaleString();
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

/**
 * Format visibility boost percentage
 */
export function formatVisibilityBoost(boost: string): string {
  // Handle formats like "+25-40%" or "35.8%"
  return boost.startsWith('+') ? boost : `+${boost}`;
}
