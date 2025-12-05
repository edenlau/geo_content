/**
 * Structured logging utility for GEO Content Platform frontend.
 *
 * Provides environment-aware logging with log levels and timestamps.
 * In development: all logs visible
 * In production: only warnings and errors
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  data?: unknown;
  timestamp: string;
  component?: string;
}

const isDevelopment = import.meta.env.DEV;

const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

// Minimum level to log (debug in dev, warn in prod)
const MIN_LOG_LEVEL: LogLevel = isDevelopment ? 'debug' : 'warn';

function shouldLog(level: LogLevel): boolean {
  return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[MIN_LOG_LEVEL];
}

function formatLogEntry(entry: LogEntry): string {
  const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`;
  const component = entry.component ? ` [${entry.component}]` : '';
  return `${prefix}${component} ${entry.message}`;
}

function createLogEntry(
  level: LogLevel,
  message: string,
  data?: unknown,
  component?: string
): LogEntry {
  return {
    level,
    message,
    data,
    timestamp: new Date().toISOString(),
    component,
  };
}

function log(level: LogLevel, message: string, data?: unknown, component?: string): void {
  if (!shouldLog(level)) return;

  const entry = createLogEntry(level, message, data, component);
  const formattedMessage = formatLogEntry(entry);

  switch (level) {
    case 'debug':
      if (data !== undefined) {
        console.debug(formattedMessage, data);
      } else {
        console.debug(formattedMessage);
      }
      break;
    case 'info':
      if (data !== undefined) {
        console.info(formattedMessage, data);
      } else {
        console.info(formattedMessage);
      }
      break;
    case 'warn':
      if (data !== undefined) {
        console.warn(formattedMessage, data);
      } else {
        console.warn(formattedMessage);
      }
      break;
    case 'error':
      if (data !== undefined) {
        console.error(formattedMessage, data);
      } else {
        console.error(formattedMessage);
      }
      break;
  }
}

/**
 * Logger instance with component context.
 */
export function createLogger(component: string) {
  return {
    debug: (message: string, data?: unknown) => log('debug', message, data, component),
    info: (message: string, data?: unknown) => log('info', message, data, component),
    warn: (message: string, data?: unknown) => log('warn', message, data, component),
    error: (message: string, data?: unknown) => log('error', message, data, component),
  };
}

/**
 * Default logger without component context.
 */
export const logger = {
  debug: (message: string, data?: unknown) => log('debug', message, data),
  info: (message: string, data?: unknown) => log('info', message, data),
  warn: (message: string, data?: unknown) => log('warn', message, data),
  error: (message: string, data?: unknown) => log('error', message, data),
};

export default logger;
