/**
 * Omnisearch Qwest-ion Logger
 * Structured logging with configurable levels and outputs
 */

import { writeFileSync, appendFileSync, existsSync, mkdirSync } from 'fs';
import { dirname } from 'path';
import type { Logger, LogEntry, LogFunction, Config } from './types.js';

/**
 * Creates a structured logger instance based on configuration
 * 
 * @param config - Logging configuration from config.yaml
 * @returns Logger instance with debug/info/warn/error methods
 */
export function createLogger(config: Config['logging']): Logger {
  const logLevel = getLogLevelPriority(config.level);

  /**
   * Core logging function that handles formatting and output
   */
  const log = (level: LogEntry['level'], message: string, data?: any, source?: string): void => {
    const levelPriority = getLogLevelPriority(level);
    
    // Skip if log level is below configured threshold
    if (levelPriority < logLevel) {
      return;
    }

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      source,
      ...(data && { data })
    };

    const formattedMessage = formatLogEntry(logEntry, config.format);
    outputLog(formattedMessage, config);
  };

  /**
   * Create log functions for each level
   */
  const debug: LogFunction = (message: string, data?: any) => log('debug', message, data, 'omnisearch');
  const info: LogFunction = (message: string, data?: any) => log('info', message, data, 'omnisearch');
  const warn: LogFunction = (message: string, data?: any) => log('warn', message, data, 'omnisearch');
  const error: LogFunction = (message: string, data?: any) => log('error', message, data, 'omnisearch');

  return {
    debug,
    info,
    warn,
    error
  };
}

/**
 * Convert log level string to numeric priority for filtering
 */
function getLogLevelPriority(level: LogEntry['level']): number {
  const priorities = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3
  };
  return priorities[level];
}

/**
 * Format log entry based on configured format
 */
function formatLogEntry(entry: LogEntry, format: Config['logging']['format']): string {
  if (format === 'json') {
    return JSON.stringify(entry);
  }

  // Text format: [TIMESTAMP] LEVEL MESSAGE (data if present)
  let formatted = `[${entry.timestamp}] ${entry.level.toUpperCase().padEnd(5)} ${entry.message}`;
  
  if (entry.source) {
    formatted += ` (${entry.source})`;
  }
  
  if (entry.data) {
    formatted += ` ${JSON.stringify(entry.data)}`;
  }
  
  return formatted;
}

/**
 * Output formatted log message based on configuration
 */
function outputLog(message: string, config: Config['logging']): void {
  if (config.output === 'stdout' || !config.file) {
    console.log(message);
    return;
  }

  // File output
  try {
    // Ensure directory exists
    const logDir = dirname(config.file);
    if (!existsSync(logDir)) {
      mkdirSync(logDir, { recursive: true });
    }

    // Append to log file
    appendFileSync(config.file, message + '\n', 'utf8');
  } catch (err) {
    // Fallback to console if file write fails
    console.error('Failed to write to log file, falling back to stdout:', err);
    console.log(message);
  }
}

/**
 * Create a logger with source context for specific components
 */
export function createSourceLogger(config: Config['logging'], source: string): Logger {
  const baseLogger = createLogger(config);
  
  return {
    debug: (message: string, data?: any) => baseLogger.debug(`[${source}] ${message}`, data),
    info: (message: string, data?: any) => baseLogger.info(`[${source}] ${message}`, data),
    warn: (message: string, data?: any) => baseLogger.warn(`[${source}] ${message}`, data),
    error: (message: string, data?: any) => baseLogger.error(`[${source}] ${message}`, data)
  };
}

/**
 * Performance logger for measuring execution times
 */
export function createPerformanceLogger(logger: Logger) {
  const timers = new Map<string, number>();

  return {
    start: (operation: string): void => {
      timers.set(operation, Date.now());
      logger.debug(`Started: ${operation}`);
    },
    
    end: (operation: string, data?: any): number => {
      const startTime = timers.get(operation);
      if (!startTime) {
        logger.warn(`No start time found for operation: ${operation}`);
        return 0;
      }
      
      const duration = Date.now() - startTime;
      timers.delete(operation);
      
      logger.info(`Completed: ${operation}`, { 
        duration_ms: duration,
        ...data 
      });
      
      return duration;
    },
    
    measure: <T>(operation: string, fn: () => Promise<T>): Promise<T> => {
      return new Promise(async (resolve, reject) => {
        const startTime = Date.now();
        logger.debug(`Started: ${operation}`);
        
        try {
          const result = await fn();
          const duration = Date.now() - startTime;
          logger.info(`Completed: ${operation}`, { duration_ms: duration });
          resolve(result);
        } catch (error) {
          const duration = Date.now() - startTime;
          logger.error(`Failed: ${operation}`, { 
            duration_ms: duration, 
            error: error instanceof Error ? error.message : String(error)
          });
          reject(error);
        }
      });
    }
  };
}

/**
 * Default logger instance for immediate use
 * Uses info level, JSON format, stdout output
 */
export const defaultLogger = createLogger({
  level: 'info',
  format: 'json',
  output: 'stdout',
  file: null
});