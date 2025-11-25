/**
 * Configuration Loader for Omnisearch Qwest-ion
 * Loads and validates config.yaml with environment variable substitution
 */

import { readFileSync, existsSync } from "fs";
import { parse as parseYAML } from "yaml";
import { z } from "zod";
import { join, resolve } from "path";
import type { Config, ToolConfig } from "./types";

// ============================================================================
// Configuration Validation Schema
// ============================================================================

const ToolConfigSchema = z.object({
  enabled: z.boolean(),
  api_key_env: z.string().optional(),
  cx_env: z.string().optional(),
  client_id_env: z.string().optional(),
  client_secret_env: z.string().optional(),
  max_results: z.number().int().positive(),
  timeout_ms: z.number().int().positive(),
  retry_attempts: z.number().int().min(0),
});

const ConfigSchema = z.object({
  agent: z.object({
    id: z.string(),
    name: z.string(),
    version: z.string(),
    description: z.string(),
  }),
  tools: z.record(ToolConfigSchema),
  execution: z.object({
    parallel: z.boolean(),
    overall_timeout_ms: z.number().int().positive(),
    min_results: z.number().int().min(0),
    max_results: z.number().int().positive(),
  }),
  ranking: z.object({
    boost_educational: z.boolean(),
    boost_recent: z.boolean(),
    diversity_weight: z.number().min(0).max(1),
  }),
  logging: z.object({
    level: z.enum(["debug", "info", "warn", "error"]),
    format: z.enum(["json", "text"]),
    output: z.enum(["stdout", "file"]),
    file: z.string().nullable(),
  }),
  e2b: z.object({
    enabled: z.boolean(),
    template_id: z.string().optional(),
    timeout_ms: z.number().int().positive().optional(),
    memory_mb: z.number().int().positive().optional(),
    env_vars: z.record(z.string()).optional(),
  }).optional(),
  rate_limit: z.object({
    enabled: z.boolean(),
    requests_per_minute: z.number().int().positive(),
    burst: z.number().int().positive(),
  }).optional(),
  cache: z.object({
    enabled: z.boolean(),
    ttl_seconds: z.number().int().positive(),
    max_size_mb: z.number().int().positive(),
    backend: z.enum(["memory", "redis"]),
  }).optional(),
  monitoring: z.object({
    enabled: z.boolean(),
    report_interval_ms: z.number().int().positive(),
    metrics: z.array(z.string()),
  }).optional(),
  development: z.object({
    mock_apis: z.boolean(),
    verbose_logging: z.boolean(),
    save_requests: z.boolean(),
  }).optional(),
});

// ============================================================================
// Configuration Loader
// ============================================================================

let cachedConfig: Config | null = null;

/**
 * Load environment variable or throw error if required
 */
function getEnvVar(key: string, required: boolean = false): string | undefined {
  const value = process.env[key];
  if (required && !value) {
    throw new Error(`Required environment variable ${key} is not set`);
  }
  return value;
}

/**
 * Load API keys from environment variables for tool configuration
 * Skips validation when mock_apis is enabled in development config
 */
function loadApiKeys(toolConfig: any, mockMode: boolean = false): ToolConfig {
  const config = { ...toolConfig };

  // Skip API key validation in mock mode
  if (mockMode) {
    return config;
  }

  // Load API key if specified
  if (config.api_key_env) {
    const apiKey = getEnvVar(config.api_key_env);
    if (!apiKey && config.enabled) {
      throw new Error(`API key not found in environment variable: ${config.api_key_env}`);
    }
    config.api_key = apiKey;
  }

  // Load Google Custom Search CX if specified
  if (config.cx_env) {
    const cx = getEnvVar(config.cx_env);
    if (!cx && config.enabled) {
      throw new Error(`Google CX not found in environment variable: ${config.cx_env}`);
    }
    config.cx = cx;
  }

  // Load Reddit client credentials if specified
  if (config.client_id_env) {
    const clientId = getEnvVar(config.client_id_env);
    if (!clientId && config.enabled) {
      throw new Error(`Client ID not found in environment variable: ${config.client_id_env}`);
    }
    config.client_id = clientId;
  }

  if (config.client_secret_env) {
    const clientSecret = getEnvVar(config.client_secret_env);
    if (!clientSecret && config.enabled) {
      throw new Error(`Client secret not found in environment variable: ${config.client_secret_env}`);
    }
    config.client_secret = clientSecret;
  }

  return config;
}

/**
 * Find config.yaml file in possible locations
 */
function findConfigFile(): string {
  const possiblePaths = [
    "config.yaml",
    "config.yml",
    join(__dirname, "..", "config.yaml"),
    join(__dirname, "..", "config.yml"),
    join(process.cwd(), "config.yaml"),
    join(process.cwd(), "config.yml"),
  ];

  for (const path of possiblePaths) {
    const resolvedPath = resolve(path);
    if (existsSync(resolvedPath)) {
      return resolvedPath;
    }
  }

  throw new Error(`Config file not found. Searched paths: ${possiblePaths.join(", ")}`);
}

/**
 * Load and parse YAML configuration file
 */
function loadYamlFile(filePath?: string): any {
  try {
    const configPath = filePath ? resolve(filePath) : findConfigFile();
    
    if (!existsSync(configPath)) {
      throw new Error(`Config file not found: ${configPath}`);
    }

    const yamlContent = readFileSync(configPath, "utf8");
    const parsed = parseYAML(yamlContent);

    if (!parsed) {
      throw new Error(`Config file is empty or invalid YAML: ${configPath}`);
    }

    return parsed;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load config file: ${error.message}`);
    }
    throw new Error(`Failed to load config file: ${String(error)}`);
  }
}

/**
 * Validate configuration structure and types
 */
function validateConfig(config: any): Config {
  try {
    const result = ConfigSchema.parse(config);
    
    // Additional validation
    if (result.execution.min_results > result.execution.max_results) {
      throw new Error("execution.min_results cannot be greater than execution.max_results");
    }

    // Validate that at least one tool is enabled
    const enabledTools = Object.values(result.tools).filter(tool => tool.enabled);
    if (enabledTools.length === 0) {
      throw new Error("At least one search tool must be enabled");
    }

    return result;
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.map(err => `${err.path.join(".")}: ${err.message}`).join(", ");
      throw new Error(`Configuration validation failed: ${errors}`);
    }
    throw error;
  }
}

/**
 * Load configuration with environment variable substitution
 */
export function getConfig(configPath?: string, forceReload: boolean = false): Config {
  // Return cached config if available and not forcing reload
  if (cachedConfig && !forceReload) {
    return cachedConfig;
  }

  try {
    // Load raw YAML
    const rawConfig = loadYamlFile(configPath);

    // Check if mock mode is enabled
    const mockMode = rawConfig.development?.mock_apis === true;

    // Load API keys from environment variables (skipped in mock mode)
    const processedConfig = {
      ...rawConfig,
      tools: Object.fromEntries(
        Object.entries(rawConfig.tools).map(([name, toolConfig]) => [
          name,
          loadApiKeys(toolConfig, mockMode)
        ])
      )
    };

    // Validate configuration
    const validatedConfig = validateConfig(processedConfig);

    // Cache for future use
    cachedConfig = validatedConfig;

    return validatedConfig;
  } catch (error) {
    throw new Error(`Configuration loading failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Get configuration for a specific tool
 */
export function getToolConfig(toolName: string, config?: Config): ToolConfig {
  const cfg = config || getConfig();
  
  if (!cfg.tools[toolName]) {
    throw new Error(`Tool configuration not found: ${toolName}`);
  }

  return cfg.tools[toolName];
}

/**
 * Check if a tool is enabled and properly configured
 */
export function isToolEnabled(toolName: string, config?: Config): boolean {
  try {
    const toolConfig = getToolConfig(toolName, config);
    return toolConfig.enabled;
  } catch {
    return false;
  }
}

/**
 * Get list of enabled tools
 */
export function getEnabledTools(config?: Config): string[] {
  const cfg = config || getConfig();
  return Object.entries(cfg.tools)
    .filter(([_, toolConfig]) => toolConfig.enabled)
    .map(([name, _]) => name);
}

/**
 * Reset cached configuration (useful for testing)
 */
export function resetConfigCache(): void {
  cachedConfig = null;
}

// ============================================================================
// Configuration Utilities
// ============================================================================

/**
 * Merge user configuration with defaults
 */
export function mergeWithDefaults(userConfig: Partial<Config>, defaultConfig: Config): Config {
  return {
    ...defaultConfig,
    ...userConfig,
    agent: { ...defaultConfig.agent, ...userConfig.agent },
    tools: { ...defaultConfig.tools, ...userConfig.tools },
    execution: { ...defaultConfig.execution, ...userConfig.execution },
    ranking: { ...defaultConfig.ranking, ...userConfig.ranking },
    logging: { ...defaultConfig.logging, ...userConfig.logging },
  };
}

/**
 * Export configuration for debugging
 */
export function exportConfig(config?: Config, includeSecrets: boolean = false): string {
  const cfg = config || getConfig();
  
  if (!includeSecrets) {
    // Remove sensitive data
    const sanitized = JSON.parse(JSON.stringify(cfg));
    Object.keys(sanitized.tools).forEach(toolName => {
      const tool = sanitized.tools[toolName];
      if (tool.api_key) tool.api_key = "[REDACTED]";
      if (tool.client_secret) tool.client_secret = "[REDACTED]";
    });
    return JSON.stringify(sanitized, null, 2);
  }

  return JSON.stringify(cfg, null, 2);
}