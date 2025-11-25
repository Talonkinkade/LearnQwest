/**
 * Structured Logger
 * Provides consistent logging across the Quality Assessment agent
 */

import type { Logger } from "./types.ts";

export function createLogger(config: { level: string; format: string }): Logger {
  const levels = ["debug", "info", "warn", "error"];
  const minLevel = levels.indexOf(config.level);

  function shouldLog(level: string): boolean {
    return levels.indexOf(level) >= minLevel;
  }

  function formatMessage(level: string, message: string, data?: any): string {
    const timestamp = new Date().toISOString();

    if (config.format === "json") {
      return JSON.stringify({
        timestamp,
        level,
        message,
        ...(data && { data }),
      });
    }

    // Text format
    const dataStr = data ? ` ${JSON.stringify(data)}` : "";
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${dataStr}`;
  }

  return {
    debug: (message: string, data?: any) => {
      if (shouldLog("debug")) {
        console.debug(formatMessage("debug", message, data));
      }
    },

    info: (message: string, data?: any) => {
      if (shouldLog("info")) {
        console.info(formatMessage("info", message, data));
      }
    },

    warn: (message: string, data?: any) => {
      if (shouldLog("warn")) {
        console.warn(formatMessage("warn", message, data));
      }
    },

    error: (message: string, data?: any) => {
      if (shouldLog("error")) {
        console.error(formatMessage("error", message, data));
      }
    },
  };
}
