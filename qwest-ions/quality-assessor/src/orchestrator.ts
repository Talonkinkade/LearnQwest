/**
 * Quality Assessment Orchestrator
 * Coordinates all 5 scorers with parallel batching for high performance
 */

import type {
  ContentItem,
  QualityAssessment,
  BatchAssessmentInput,
  BatchAssessmentOutput,
  QualityConfig,
  Logger,
} from "./types.ts";
import { getThresholds } from "./config.ts";
import { CredibilityScorer } from "./scorers/credibility.ts";
import { AccuracyScorer } from "./scorers/accuracy.ts";
import { ProductionScorer } from "./scorers/production.ts";
import { EducationalScorer } from "./scorers/educational.ts";
import { EngagementScorer } from "./scorers/engagement.ts";

export class QualityAssessor {
  private scorers = [
    new CredibilityScorer(),
    new AccuracyScorer(),
    new ProductionScorer(),
    new EducationalScorer(),
    new EngagementScorer(),
  ];

  constructor(
    private config: QualityConfig,
    private logger: Logger
  ) {
    this.logger.info("Quality Assessor initialized", {
      version: config.agent.version,
      scorers: this.scorers.map(s => s.dimension),
    });
  }

  /**
   * Assess a single content item
   */
  async assessItem(
    item: ContentItem,
    mode: "production" | "testing" | "strict" = "production"
  ): Promise<QualityAssessment> {
    this.logger.debug(`Assessing item: ${item.title}`, { id: item.id, mode });

    const startTime = Date.now();

    try {
      // Score with all 5 dimensions in parallel
      const dimensionScores = await Promise.all(
        this.scorers.map(scorer => scorer.score(item, this.config))
      );

      // Calculate overall score (weighted sum)
      const overall_score = dimensionScores.reduce(
        (sum, dim) => sum + dim.weighted_score,
        0
      );

      // Get thresholds for the specified mode
      const thresholds = getThresholds(this.config, mode);
      const threshold = thresholds.overall;

      // Check if passed overall threshold
      let passed = overall_score >= threshold;

      // Also check dimension-specific thresholds
      for (const dimScore of dimensionScores) {
        const dimThreshold = thresholds.dimensions[dimScore.dimension];
        if (dimScore.score < dimThreshold) {
          passed = false;
          this.logger.debug(`Failed ${dimScore.dimension} threshold`, {
            score: dimScore.score,
            threshold: dimThreshold,
          });
        }
      }

      const executionTime = Date.now() - startTime;

      this.logger.info(`Assessment complete: ${passed ? "PASS" : "FAIL"}`, {
        id: item.id,
        overall_score: overall_score.toFixed(2),
        threshold,
        execution_time_ms: executionTime,
      });

      return {
        item,
        dimensions: dimensionScores,
        overall_score,
        passed,
        threshold,
        assessed_at: new Date().toISOString(),
        assessment_version: this.config.agent.version,
      };
    } catch (error) {
      this.logger.error(`Failed to assess item ${item.id}`, {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Assess multiple items in batch with parallel processing
   * Optimized for performance: processes items in concurrent batches
   */
  async assessBatch(input: BatchAssessmentInput): Promise<BatchAssessmentOutput> {
    const mode = input.mode || "production";
    const batchSize = this.config.performance.batch_size;

    this.logger.info(`Starting batch assessment`, {
      total_items: input.items.length,
      threshold: input.threshold,
      mode,
      batch_size: batchSize,
    });

    const startTime = Date.now();
    const allAssessments: QualityAssessment[] = [];

    // Process items in batches for optimal performance
    for (let i = 0; i < input.items.length; i += batchSize) {
      const batch = input.items.slice(i, i + batchSize);
      const batchNum = Math.floor(i / batchSize) + 1;
      const totalBatches = Math.ceil(input.items.length / batchSize);

      this.logger.debug(`Processing batch ${batchNum}/${totalBatches}`, {
        batch_size: batch.length,
        items_processed: i,
        items_remaining: input.items.length - i - batch.length,
      });

      try {
        // Assess all items in this batch in parallel
        const batchResults = await Promise.all(
          batch.map(item => this.assessItem(item, mode))
        );
        allAssessments.push(...batchResults);

        this.logger.debug(`Batch ${batchNum} complete`, {
          passed: batchResults.filter(r => r.passed).length,
          failed: batchResults.filter(r => !r.passed).length,
        });
      } catch (error) {
        this.logger.error(`Batch ${batchNum} failed`, {
          error: error instanceof Error ? error.message : String(error),
        });
        throw error;
      }
    }

    // Split into passed/failed
    const passed = allAssessments.filter(a => a.passed);
    const failed = allAssessments.filter(a => !a.passed);

    // Calculate statistics
    const avg_score =
      allAssessments.reduce((sum, a) => sum + a.overall_score, 0) /
      allAssessments.length;

    const avg_by_dimension: Record<string, number> = {};
    for (const dim of ["credibility", "accuracy", "production", "educational", "engagement"]) {
      avg_by_dimension[dim] =
        allAssessments.reduce((sum, a) => {
          const dimScore = a.dimensions.find(d => d.dimension === dim);
          return sum + (dimScore?.score || 0);
        }, 0) / allAssessments.length;
    }

    const executionTime = Date.now() - startTime;
    const itemsPerSecond = (allAssessments.length / executionTime) * 1000;

    this.logger.info(`Batch assessment complete`, {
      total: allAssessments.length,
      passed: passed.length,
      failed: failed.length,
      pass_rate: `${((passed.length / allAssessments.length) * 100).toFixed(1)}%`,
      avg_score: avg_score.toFixed(2),
      execution_time_ms: executionTime,
      items_per_second: itemsPerSecond.toFixed(2),
      performance_target: "100 items < 5000ms",
      performance_met: allAssessments.length >= 100 ? executionTime < 5000 : "N/A",
    });

    return {
      total_assessed: allAssessments.length,
      passed,
      failed,
      statistics: {
        pass_rate: passed.length / allAssessments.length,
        avg_score,
        avg_by_dimension,
        execution_time_ms: executionTime,
        items_per_second: itemsPerSecond,
      },
      assessed_at: new Date().toISOString(),
      mode,
    };
  }

  /**
   * Get detailed breakdown for a single assessment (for debugging)
   */
  getAssessmentBreakdown(assessment: QualityAssessment): string {
    const lines: string[] = [];

    lines.push(`Assessment for: ${assessment.item.title}`);
    lines.push(`URL: ${assessment.item.url}`);
    lines.push(`Overall Score: ${assessment.overall_score.toFixed(2)}/100`);
    lines.push(`Status: ${assessment.passed ? "PASSED" : "FAILED"} (threshold: ${assessment.threshold})`);
    lines.push("");
    lines.push("Dimension Breakdown:");

    for (const dim of assessment.dimensions) {
      lines.push(`  ${dim.dimension.toUpperCase()}: ${dim.score.toFixed(1)}/100 (weight: ${(dim.weight * 100).toFixed(0)}%)`);
      lines.push(`    Weighted contribution: ${dim.weighted_score.toFixed(2)}`);
      lines.push(`    Confidence: ${(dim.confidence * 100).toFixed(0)}%`);
      lines.push(`    Signals (${dim.signals.length}):`);

      for (const signal of dim.signals) {
        const impact = signal.impact === "positive" ? "+" : signal.impact === "negative" ? "-" : "=";
        lines.push(`      [${impact}] ${signal.indicator}: ${signal.value}`);
      }
      lines.push("");
    }

    return lines.join("\n");
  }
}
