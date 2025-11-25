/**
 * Orchestrator for Omnisearch Qwest-ion
 * Executes all 8 CLI search tools in parallel
 */

import { spawn } from "bun";
import type {
  OmnisearchInput,
  Config,
  Logger,
  AggregatedResults,
  SearchResult,
  SearchToolResult,
} from "./types.js";

/**
 * Tool configuration mapping
 */
const TOOL_CONFIGS = {
  youtube: {
    path: "./tools/cli/youtube-search",
    type: "video" as const,
  },
  google: {
    path: "./tools/cli/google-search",
    type: "article" as const,
  },
  scholar: {
    path: "./tools/cli/scholar-search",
    type: "paper" as const,
  },
  khan: {
    path: "./tools/cli/khan-search",
    type: "video" as const,
  },
  reddit: {
    path: "./tools/cli/reddit-search",
    type: "discussion" as const,
  },
  stackoverflow: {
    path: "./tools/cli/stackoverflow-search",
    type: "qa" as const,
  },
  wikipedia: {
    path: "./tools/cli/wikipedia-search",
    type: "wiki" as const,
  },
  arxiv: {
    path: "./tools/cli/arxiv-search",
    type: "paper" as const,
  },
} as const;

/**
 * Execute a single search tool
 */
async function executeTool(
  toolName: string,
  input: OmnisearchInput,
  config: Config,
  logger: Logger
): Promise<SearchToolResult> {
  const startTime = Date.now();
  const toolConfig = config.tools[toolName];
  const cliConfig = TOOL_CONFIGS[toolName as keyof typeof TOOL_CONFIGS];

  if (!toolConfig?.enabled) {
    logger.debug(`Tool ${toolName} is disabled`);
    return {
      source: toolName,
      results: [],
      execution_time_ms: 0,
      success: false,
      error: "Tool disabled",
    };
  }

  if (!cliConfig) {
    logger.error(`Unknown tool: ${toolName}`);
    return {
      source: toolName,
      results: [],
      execution_time_ms: Date.now() - startTime,
      success: false,
      error: "Unknown tool",
    };
  }

  try {
    logger.debug(`Executing ${toolName}`, { query: input.query, max_results: toolConfig.max_results });

    // Build CLI arguments
    const args = [
      "--query", input.query,
      "--max-results", toolConfig.max_results.toString(),
    ];

    // Add optional parameters
    if (input.grade_level) {
      args.push("--grade-level", input.grade_level);
    }
    if (input.subject) {
      args.push("--subject", input.subject);
    }

    // Execute tool with timeout
    const proc = spawn({
      cmd: [cliConfig.path, ...args],
      stdout: "pipe",
      stderr: "pipe",
    });

    // Create timeout promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        proc.kill();
        reject(new Error(`Tool ${toolName} timed out after ${toolConfig.timeout_ms}ms`));
      }, toolConfig.timeout_ms);
    });

    // Wait for completion or timeout
    const result = await Promise.race([
      proc.exited,
      timeoutPromise,
    ]);

    const exitCode = await result;
    const stdout = await new Response(proc.stdout).text();
    const stderr = await new Response(proc.stderr).text();

    if (exitCode !== 0) {
      throw new Error(`Tool ${toolName} exited with code ${exitCode}: ${stderr}`);
    }

    // Parse JSON output
    let toolResults: any[];
    try {
      toolResults = JSON.parse(stdout);
      if (!Array.isArray(toolResults)) {
        throw new Error("Tool output is not an array");
      }
    } catch (parseError) {
      throw new Error(`Failed to parse JSON output: ${parseError}`);
    }

    // Convert to SearchResult format
    const searchResults: SearchResult[] = toolResults.map((result, index) => ({
      title: result.title || "Untitled",
      url: result.url || "",
      source: toolName as any,
      type: cliConfig.type,
      relevance_score: result.relevance_score || 0.5,
      metadata: {
        ...result,
        tool_index: index,
      },
    }));

    const executionTime = Date.now() - startTime;
    logger.debug(`Tool ${toolName} completed`, {
      results_count: searchResults.length,
      execution_time_ms: executionTime,
    });

    return {
      source: toolName,
      results: searchResults,
      execution_time_ms: executionTime,
      success: true,
    };

  } catch (error) {
    const executionTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    logger.warn(`Tool ${toolName} failed`, {
      error: errorMessage,
      execution_time_ms: executionTime,
    });

    return {
      source: toolName,
      results: [],
      execution_time_ms: executionTime,
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Execute tool with retry logic
 */
async function executeToolWithRetry(
  toolName: string,
  input: OmnisearchInput,
  config: Config,
  logger: Logger
): Promise<SearchToolResult> {
  const toolConfig = config.tools[toolName];
  const maxAttempts = toolConfig?.retry_attempts || 1;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await executeTool(toolName, input, config, logger);
    
    if (result.success || attempt === maxAttempts) {
      if (attempt > 1) {
        logger.info(`Tool ${toolName} succeeded on attempt ${attempt}`);
      }
      return result;
    }

    // Exponential backoff for retries
    const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
    logger.debug(`Tool ${toolName} failed on attempt ${attempt}, retrying in ${delay}ms`);
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  // This should never be reached due to the logic above, but TypeScript needs it
  throw new Error(`Unexpected error in retry logic for ${toolName}`);
}

/**
 * Aggregate results from all tools
 */
function aggregateResults(toolResults: SearchToolResult[]): AggregatedResults {
  const allResults: SearchResult[] = [];
  const bySource = new Map<string, SearchResult[]>();
  const successfulSources: string[] = [];
  const failedSources: string[] = [];

  for (const toolResult of toolResults) {
    if (toolResult.success) {
      successfulSources.push(toolResult.source);
      allResults.push(...toolResult.results);
      bySource.set(toolResult.source, toolResult.results);
    } else {
      failedSources.push(toolResult.source);
      bySource.set(toolResult.source, []);
    }
  }

  return {
    all_results: allResults,
    by_source: bySource,
    total_count: allResults.length,
    successful_sources: successfulSources,
    failed_sources: failedSources,
  };
}

/**
 * Main orchestrator function
 * Executes all enabled search tools in parallel
 */
export async function orchestrate(
  input: OmnisearchInput,
  config: Config,
  logger: Logger
): Promise<AggregatedResults> {
  const startTime = Date.now();
  
  logger.info("Starting omnisearch orchestration", {
    query: input.query,
    timeout_ms: config.execution.overall_timeout_ms,
  });

  // Get list of enabled tools
  const enabledTools = Object.keys(config.tools).filter(
    toolName => config.tools[toolName]?.enabled
  );

  if (enabledTools.length === 0) {
    logger.error("No tools are enabled");
    return {
      all_results: [],
      by_source: new Map(),
      total_count: 0,
      successful_sources: [],
      failed_sources: [],
    };
  }

  try {
    // Create promises for all tools
    const toolPromises = enabledTools.map(toolName =>
      executeToolWithRetry(toolName, input, config, logger)
    );

    // Execute all tools in parallel with overall timeout
    const overallTimeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Overall orchestration timeout after ${config.execution.overall_timeout_ms}ms`));
      }, config.execution.overall_timeout_ms);
    });

    // Wait for all tools to complete or overall timeout
    const results = await Promise.race([
      Promise.allSettled(toolPromises),
      overallTimeoutPromise,
    ]);

    // Process results
    const toolResults: SearchToolResult[] = [];
    for (let i = 0; i < results.length; i++) {
      const result = results[i];
      if (result.status === "fulfilled") {
        toolResults.push(result.value);
      } else {
        // Promise was rejected
        const toolName = enabledTools[i];
        logger.error(`Tool ${toolName} promise rejected`, { error: result.reason });
        toolResults.push({
          source: toolName,
          results: [],
          execution_time_ms: 0,
          success: false,
          error: result.reason instanceof Error ? result.reason.message : String(result.reason),
        });
      }
    }

    const aggregated = aggregateResults(toolResults);
    const executionTime = Date.now() - startTime;

    // Log summary
    logger.info("Orchestration completed", {
      total_results: aggregated.total_count,
      successful_tools: aggregated.successful_sources.length,
      failed_tools: aggregated.failed_sources.length,
      execution_time_ms: executionTime,
      success_rate: aggregated.successful_sources.length / enabledTools.length,
    });

    // Check if we have minimum results
    if (aggregated.total_count < config.execution.min_results) {
      logger.warn(`Only ${aggregated.total_count} results found, minimum is ${config.execution.min_results}`);
    }

    return aggregated;

  } catch (error) {
    const executionTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    logger.error("Orchestration failed", {
      error: errorMessage,
      execution_time_ms: executionTime,
    });

    // Return empty results on catastrophic failure
    return {
      all_results: [],
      by_source: new Map(),
      total_count: 0,
      successful_sources: [],
      failed_sources: enabledTools,
    };
  }
}

/**
 * Calculate execution metrics
 */
export function calculateMetrics(
  toolResults: SearchToolResult[],
  totalExecutionTime: number
): {
  success_rate: number;
  avg_tool_time: number;
  total_results: number;
  fastest_tool: string | null;
  slowest_tool: string | null;
} {
  const successfulResults = toolResults.filter(r => r.success);
  const successRate = toolResults.length > 0 ? successfulResults.length / toolResults.length : 0;
  
  const toolTimes = toolResults.map(r => r.execution_time_ms);
  const avgToolTime = toolTimes.length > 0 ? toolTimes.reduce((a, b) => a + b, 0) / toolTimes.length : 0;
  
  const totalResults = toolResults.reduce((sum, r) => sum + r.results.length, 0);
  
  let fastestTool: string | null = null;
  let slowestTool: string | null = null;
  
  if (successfulResults.length > 0) {
    const sortedByTime = successfulResults.sort((a, b) => a.execution_time_ms - b.execution_time_ms);
    fastestTool = sortedByTime[0].source;
    slowestTool = sortedByTime[sortedByTime.length - 1].source;
  }

  return {
    success_rate: successRate,
    avg_tool_time: avgToolTime,
    total_results: totalResults,
    fastest_tool: fastestTool,
    slowest_tool: slowestTool,
  };
}