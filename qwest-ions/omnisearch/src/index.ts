#!/usr/bin/env bun

/**
 * Omnisearch Qwest-ion - Main Entry Point
 * Multi-source educational content search orchestrator
 */

import { parseArgs } from "util";
import { OmnisearchInput, OmnisearchInputSchema, OmnisearchOutput, SearchResult } from "./types.js";
import { getConfig } from "./config.js";
import { createLogger } from "./logger.js";
import { orchestrate } from "./orchestrator.js";
import { rankResults } from "./ranker.js";

/**
 * Main orchestration function
 * Executes parallel search across all 8 sources and returns ranked results
 */
export async function main(input: OmnisearchInput): Promise<OmnisearchOutput> {
  const startTime = Date.now();
  
  // Load configuration and initialize logger
  const config = getConfig();
  const logger = createLogger(config);
  
  logger.info("Starting omnisearch", { 
    query: input.query,
    grade_level: input.grade_level,
    subject: input.subject 
  });

  try {
    // Validate input
    const validatedInput = OmnisearchInputSchema.parse(input);
    
    // Execute parallel searches across all 8 tools
    const searchResults = await orchestrate(validatedInput, config, logger);
    
    // Extract all successful results
    const allResults: SearchResult[] = [];
    const sourcesUsed: string[] = [];
    const failedSources: string[] = [];
    
    for (const toolResult of searchResults) {
      if (toolResult.success) {
        allResults.push(...toolResult.results);
        sourcesUsed.push(toolResult.source);
      } else {
        failedSources.push(toolResult.source);
        logger.warn(`Tool ${toolResult.source} failed`, { error: toolResult.error });
      }
    }

    // Check if we have minimum viable results
    if (allResults.length < config.execution.min_results) {
      throw new Error(`Insufficient results: got ${allResults.length}, need at least ${config.execution.min_results}`);
    }

    // Rank and filter results
    const rankedResults = rankResults(allResults, config);
    
    // Limit to max results
    const finalResults = rankedResults.slice(0, validatedInput.max_results);
    
    const executionTime = Date.now() - startTime;
    const successRate = sourcesUsed.length / (sourcesUsed.length + failedSources.length);

    logger.info("Omnisearch completed", {
      total_results: finalResults.length,
      execution_time_ms: executionTime,
      sources_used: sourcesUsed,
      success_rate: successRate
    });

    return {
      query: validatedInput.query,
      results: finalResults,
      metadata: {
        total_found: finalResults.length,
        execution_time_ms: executionTime,
        sources_used: sourcesUsed,
        success_rate: successRate
      }
    };

  } catch (error) {
    const executionTime = Date.now() - startTime;
    
    logger.error("Omnisearch failed", { 
      error: error instanceof Error ? error.message : String(error),
      execution_time_ms: executionTime
    });

    // Return minimal error response
    return {
      query: input.query,
      results: [],
      metadata: {
        total_found: 0,
        execution_time_ms: executionTime,
        sources_used: [],
        success_rate: 0
      }
    };
  }
}

/**
 * CLI argument parsing
 */
function parseCliArgs(): OmnisearchInput {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      query: {
        type: "string",
        short: "q"
      },
      "grade-level": {
        type: "string",
        short: "g"
      },
      subject: {
        type: "string",
        short: "s"
      },
      "content-types": {
        type: "string",
        multiple: true
      },
      "max-results": {
        type: "string",
        short: "n"
      },
      "timeout-ms": {
        type: "string",
        short: "t"
      },
      help: {
        type: "boolean",
        short: "h"
      }
    },
    allowPositionals: true
  });

  if (values.help) {
    console.log(`
Omnisearch Qwest-ion - Multi-source educational content search

Usage: omnisearch [options]

Options:
  -q, --query <query>           Search query (required)
  -g, --grade-level <level>     Target grade level (e.g., "5th grade")
  -s, --subject <subject>       Subject area (e.g., "math", "science")
  --content-types <types>       Content types to include (video,article,paper,discussion,wiki)
  -n, --max-results <number>    Maximum results to return (default: 40)
  -t, --timeout-ms <ms>         Timeout in milliseconds (default: 10000)
  -h, --help                    Show this help message

Examples:
  omnisearch --query "quadratic equations" --subject "math" --grade-level "high school"
  omnisearch -q "photosynthesis" -s "biology" --content-types video,article
`);
    process.exit(0);
  }

  if (!values.query) {
    console.error("Error: --query is required");
    process.exit(1);
  }

  const input: OmnisearchInput = {
    query: values.query,
    grade_level: values["grade-level"],
    subject: values.subject,
    max_results: values["max-results"] ? parseInt(values["max-results"]) : 40,
    timeout_ms: values["timeout-ms"] ? parseInt(values["timeout-ms"]) : 10000
  };

  if (values["content-types"]) {
    input.content_types = values["content-types"] as ("video" | "article" | "paper" | "discussion" | "wiki")[];
  }

  return input;
}

/**
 * CLI execution when run directly
 */
if (import.meta.main) {
  try {
    const input = parseCliArgs();
    const result = await main(input);
    
    // Output JSON result to stdout
    console.log(JSON.stringify(result, null, 2));
    
    // Exit with success/failure code
    process.exit(result.results.length > 0 ? 0 : 1);
    
  } catch (error) {
    console.error("Fatal error:", error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}