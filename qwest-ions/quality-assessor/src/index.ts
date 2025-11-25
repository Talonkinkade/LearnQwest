#!/usr/bin/env bun

/**
 * Quality Assessment Qwest-ion CLI
 * Main entry point for quality assessment agent
 */

import { parseArgs } from "util";
import { readFile } from "fs/promises";
import { QualityAssessor } from "./orchestrator.ts";
import { createLogger } from "./logger.ts";
import { loadConfig } from "./config.ts";
import { ContentItemSchema, type ContentItem } from "./types.ts";

async function main() {
  const { values } = parseArgs({
    options: {
      input: { type: "string", short: "i" },
      output: { type: "string", short: "o" },
      threshold: { type: "string", short: "t" },
      mode: { type: "string", short: "m" },
      config: { type: "string", short: "c" },
      verbose: { type: "boolean", short: "v", default: false },
      breakdown: { type: "boolean", short: "b", default: false },
      help: { type: "boolean", short: "h", default: false },
    },
  });

  // Show help
  if (values.help) {
    console.log(`
Quality Assessment Qwest-ion v1.0.0
Educational content quality filtering with 5-dimension scoring

USAGE:
  bun run src/index.ts [OPTIONS]

OPTIONS:
  -i, --input <file>      Input JSON file with content items (required)
  -o, --output <file>     Output JSON file for results (default: quality-assessment-output.json)
  -t, --threshold <num>   Override overall quality threshold (0-100)
  -m, --mode <mode>       Assessment mode: production|testing|strict (default: production)
  -c, --config <file>     Custom config file (default: ./config/thresholds.yaml)
  -v, --verbose           Enable debug logging
  -b, --breakdown         Show detailed breakdown for each assessment
  -h, --help              Show this help message

MODES:
  production   70% overall threshold (default)
  testing      55% overall threshold (for synthetic test data)
  strict       85% overall threshold (premium content only)

EXAMPLES:
  # Basic usage
  bun run src/index.ts -i omnisearch-results.json -o filtered.json

  # Testing mode with verbose output
  bun run src/index.ts -i test-data.json -m testing -v

  # Custom threshold with breakdown
  bun run src/index.ts -i content.json -t 75 -b

  # Strict mode with custom config
  bun run src/index.ts -i premium.json -m strict -c custom-config.yaml

INPUT FORMAT:
  JSON array of content items or object with "results" key:
  [
    {
      "id": "item1",
      "title": "Example Video",
      "url": "https://youtube.com/watch?v=...",
      "source": "youtube",
      "type": "video",
      "views": 15000,
      "likes": 850
      // ... additional metadata
    }
  ]

OUTPUT FORMAT:
  {
    "total_assessed": 100,
    "passed": [/* QualityAssessment objects */],
    "failed": [/* QualityAssessment objects */],
    "statistics": {
      "pass_rate": 0.75,
      "avg_score": 72.5,
      "avg_by_dimension": {...},
      "execution_time_ms": 3500,
      "items_per_second": 28.57
    }
  }
`);
    return;
  }

  // Validate required args
  if (!values.input) {
    console.error("Error: --input required");
    console.error("Run with --help for usage information");
    process.exit(1);
  }

  try {
    // Load configuration
    const config = await loadConfig(values.config as string | undefined);

    // Create logger
    const logger = createLogger({
      level: values.verbose ? "debug" : config.logging.level,
      format: config.logging.format,
    });

    logger.info("Quality Assessment Qwest-ion starting", {
      version: config.agent.version,
      input: values.input,
      mode: values.mode || "production",
    });

    // Read input file
    const inputData = JSON.parse(await readFile(values.input, "utf-8"));

    // Parse as ContentItem array
    let items: ContentItem[] = [];

    if (Array.isArray(inputData)) {
      items = inputData;
    } else if (inputData.results && Array.isArray(inputData.results)) {
      items = inputData.results;
    } else {
      throw new Error("Input must be array or object with 'results' key");
    }

    // Validate all items
    logger.debug(`Validating ${items.length} content items`);
    const validatedItems = items.map((item, idx) => {
      try {
        return ContentItemSchema.parse(item);
      } catch (error) {
        logger.error(`Invalid item at index ${idx}`, {
          item,
          error: error instanceof Error ? error.message : String(error),
        });
        throw new Error(`Item ${idx} failed validation: ${error}`);
      }
    });

    logger.info(`Loaded ${validatedItems.length} valid content items`);

    // Determine mode
    const mode = (values.mode as "production" | "testing" | "strict") || "production";
    if (!["production", "testing", "strict"].includes(mode)) {
      throw new Error(`Invalid mode: ${mode}. Must be production, testing, or strict`);
    }

    // Override threshold if provided
    let threshold: number | undefined;
    if (values.threshold) {
      threshold = parseFloat(values.threshold);
      if (isNaN(threshold) || threshold < 0 || threshold > 100) {
        throw new Error(`Invalid threshold: ${values.threshold}. Must be 0-100`);
      }
      logger.info(`Using custom threshold: ${threshold}`);
    }

    // Create assessor
    const assessor = new QualityAssessor(config, logger);

    // Run assessment
    const result = await assessor.assessBatch({
      items: validatedItems,
      threshold,
      mode,
    });

    // Write output
    const outputPath = values.output || "quality-assessment-output.json";
    await Bun.write(outputPath, JSON.stringify(result, null, 2));

    // Print summary
    console.log("\nQuality Assessment Complete");
    console.log("================================");
    console.log(`Mode: ${mode}`);
    console.log(`Total assessed: ${result.total_assessed}`);
    console.log(`Passed: ${result.passed.length} (${(result.statistics.pass_rate * 100).toFixed(1)}%)`);
    console.log(`Failed: ${result.failed.length}`);
    console.log(`Average score: ${result.statistics.avg_score.toFixed(1)}/100`);
    console.log("");
    console.log("Average by dimension:");
    for (const [dim, score] of Object.entries(result.statistics.avg_by_dimension)) {
      console.log(`  ${dim}: ${score.toFixed(1)}/100`);
    }
    console.log("");
    console.log(`Performance: ${result.statistics.items_per_second.toFixed(2)} items/second`);
    console.log(`Execution time: ${result.statistics.execution_time_ms}ms`);
    console.log(`\nOutput written to: ${outputPath}`);

    // Show breakdown if requested
    if (values.breakdown) {
      console.log("\n================================");
      console.log("DETAILED BREAKDOWN");
      console.log("================================\n");

      // Show first 3 passed and first 3 failed
      const showPassed = result.passed.slice(0, 3);
      const showFailed = result.failed.slice(0, 3);

      if (showPassed.length > 0) {
        console.log("PASSED ITEMS (showing first 3):\n");
        for (const assessment of showPassed) {
          console.log(assessor.getAssessmentBreakdown(assessment));
          console.log("---\n");
        }
      }

      if (showFailed.length > 0) {
        console.log("\nFAILED ITEMS (showing first 3):\n");
        for (const assessment of showFailed) {
          console.log(assessor.getAssessmentBreakdown(assessment));
          console.log("---\n");
        }
      }
    }

  } catch (error) {
    console.error("Fatal error:", error instanceof Error ? error.message : String(error));
    if (values.verbose && error instanceof Error) {
      console.error("\nStack trace:");
      console.error(error.stack);
    }
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Unhandled error:", error);
  process.exit(1);
});
