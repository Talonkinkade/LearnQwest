/**
 * Configuration Loader
 * Loads and validates quality assessment configuration
 */

import { readFile } from "fs/promises";
import { parse } from "yaml";
import { QualityConfigSchema, type QualityConfig } from "./types.ts";

const DEFAULT_CONFIG_PATH = "./config/thresholds.yaml";

export async function loadConfig(configPath?: string): Promise<QualityConfig> {
  const path = configPath || DEFAULT_CONFIG_PATH;

  try {
    const content = await readFile(path, "utf-8");
    const rawConfig = parse(content);

    // Validate with Zod schema
    const config = QualityConfigSchema.parse(rawConfig);

    // Validate that weights sum to 1.0
    const weightSum =
      config.weights.credibility +
      config.weights.accuracy +
      config.weights.production +
      config.weights.educational +
      config.weights.engagement;

    if (Math.abs(weightSum - 1.0) > 0.001) {
      throw new Error(
        `Weights must sum to 1.0 (got ${weightSum.toFixed(3)}). ` +
        `Check config.weights in ${path}`
      );
    }

    return config;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load config from ${path}: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Get thresholds for a specific mode
 */
export function getThresholds(config: QualityConfig, mode: "production" | "testing" | "strict") {
  return config.modes[mode];
}
