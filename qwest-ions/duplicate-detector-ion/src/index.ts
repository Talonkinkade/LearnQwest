#!/usr/bin/env bun
import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { Command } from 'commander';
import { parse as parseYaml } from 'yaml';
import {
  ScanResultSchema,
  DuplicateReportSchema,
  ConfigSchema,
  type ScanResult,
  type DuplicateReport,
  type Config,
} from './types';
import { DuplicateDetector } from './detector';
import { logger } from './logger';

/**
 * Duplicate Detector Ion - BMAD Method
 * Detects exact and similar code duplicates from Code Scanner output
 */

const program = new Command();

program
  .name('duplicate-detector-ion')
  .description('BMAD Ion for detecting exact and similar code duplicates')
  .version('1.0.0')
  .requiredOption('-i, --input <path>', 'Path to scan-results.json from Code Scanner Ion')
  .option('-o, --output <path>', 'Path to output duplicates-report.json (default: ./duplicates-report.json)')
  .option('-c, --config <path>', 'Path to config.yaml (default: ./config.yaml)')
  .option('--verbose', 'Enable verbose logging')
  .parse(process.argv);

const options = program.opts();

async function main() {
  try {
    logger.section('Duplicate Detector Ion - BMAD Method');
    logger.info('Starting duplicate detection analysis...');

    // Load config
    const configPath = resolve(options.config || './config.yaml');
    logger.info(`Loading config from: ${configPath}`);

    const configRaw = readFileSync(configPath, 'utf-8');
    const configData = parseYaml(configRaw);
    const config: Config = ConfigSchema.parse(configData);

    logger.success('Config loaded successfully');

    // Load scan results
    const inputPath = resolve(options.input);
    logger.info(`Loading scan results from: ${inputPath}`);

    const scanRaw = readFileSync(inputPath, 'utf-8');
    const scanData = JSON.parse(scanRaw);
    const scanResult: ScanResult = ScanResultSchema.parse(scanData);

    logger.success('Scan results loaded successfully');
    logger.info(`Project root: ${scanResult.project_root}`);
    logger.info(`Scan level: ${scanResult.scan_level}`);

    // Run detection
    const detector = new DuplicateDetector(config, scanResult.project_root);
    const analysisResults = await detector.analyze(scanResult);

    // Generate report
    logger.section('Generating Report');

    const filesAnalyzed = scanResult.findings?.files?.length || 0;
    const totalLines = scanResult.findings?.files?.reduce((sum, f) => sum + f.lines, 0) || 0;
    const duplicatesFound = analysisResults.duplicateGroups.length;
    const exactDuplicates = analysisResults.duplicateGroups.filter(g => g.type === 'exact').length;
    const similarDuplicates = analysisResults.duplicateGroups.filter(g => g.type === 'similar').length;
    const totalSpaceSavings = analysisResults.duplicateGroups.reduce(
      (sum, g) => sum + g.space_savings_potential,
      0
    );

    const report: DuplicateReport = {
      generated_at: new Date().toISOString(),
      project_root: scanResult.project_root,
      scan_summary: {
        files_analyzed: filesAnalyzed,
        total_lines: totalLines,
        duplicates_found: duplicatesFound,
        exact_duplicates: exactDuplicates,
        similar_duplicates: similarDuplicates,
        total_space_savings: totalSpaceSavings,
      },
      duplicate_groups: analysisResults.duplicateGroups,
      pattern_groups: analysisResults.patternGroups,
      file_path_patterns: analysisResults.filePathPatterns,
      recommendations: generateRecommendations(analysisResults.duplicateGroups),
    };

    // Validate output
    DuplicateReportSchema.parse(report);

    // Write output
    const outputPath = resolve(options.output || './duplicates-report.json');
    writeFileSync(outputPath, JSON.stringify(report, null, 2));

    logger.success(`Report written to: ${outputPath}`);

    // Display summary
    logger.section('Analysis Summary');
    logger.info(`Files analyzed: ${filesAnalyzed}`);
    logger.info(`Total lines: ${totalLines.toLocaleString()}`);
    logger.info(`Duplicates found: ${duplicatesFound}`);
    logger.info(`  - Exact: ${exactDuplicates}`);
    logger.info(`  - Similar: ${similarDuplicates}`);
    logger.info(`Pattern groups: ${analysisResults.patternGroups.length}`);
    logger.info(`Space savings potential: ${formatBytes(totalSpaceSavings)}`);

    // Display priorities
    const priorities = {
      critical: analysisResults.duplicateGroups.filter(g => g.refactor_priority === 'critical').length,
      high: analysisResults.duplicateGroups.filter(g => g.refactor_priority === 'high').length,
      medium: analysisResults.duplicateGroups.filter(g => g.refactor_priority === 'medium').length,
      low: analysisResults.duplicateGroups.filter(g => g.refactor_priority === 'low').length,
    };

    logger.subsection('Refactor Priority Breakdown');
    logger.info(`🔴 Critical: ${priorities.critical}`);
    logger.info(`🟠 High: ${priorities.high}`);
    logger.info(`🟡 Medium: ${priorities.medium}`);
    logger.info(`🟢 Low: ${priorities.low}`);

    // Display top recommendations
    if (report.recommendations.length > 0) {
      logger.subsection('Top Recommendations');
      report.recommendations.slice(0, 5).forEach((rec, idx) => {
        logger.info(`${idx + 1}. [${rec.priority.toUpperCase()}] ${rec.description}`);
        logger.debug(`   Category: ${rec.category}`);
        logger.debug(`   Affected files: ${rec.affected_files.length}`);
        logger.debug(`   Estimated effort: ${rec.estimated_effort}`);
      });
    }

    logger.success('Duplicate detection complete!');
    process.exit(0);
  } catch (error) {
    logger.error('Fatal error during duplicate detection:');
    logger.error(error instanceof Error ? error.message : String(error));

    if (options.verbose && error instanceof Error) {
      logger.debug('Stack trace:');
      console.error(error.stack);
    }

    process.exit(1);
  }
}

/**
 * Generate recommendations from duplicate groups
 */
function generateRecommendations(groups: any[]): any[] {
  const recommendations: any[] = [];

  // Group by priority
  const criticalGroups = groups.filter(g => g.refactor_priority === 'critical');
  const highGroups = groups.filter(g => g.refactor_priority === 'high');

  // Critical recommendations
  if (criticalGroups.length > 0) {
    recommendations.push({
      priority: 'critical',
      category: 'Code Duplication',
      description: `${criticalGroups.length} critical duplicate(s) found. Immediate refactoring recommended.`,
      affected_files: criticalGroups.flatMap(g => g.files.map((f: any) => f.path)),
      estimated_effort: `${Math.ceil(criticalGroups.length * 2)} hours`,
    });
  }

  // High priority recommendations
  if (highGroups.length > 0) {
    recommendations.push({
      priority: 'high',
      category: 'Code Duplication',
      description: `${highGroups.length} high-priority duplicate(s) found. Should be addressed soon.`,
      affected_files: highGroups.flatMap(g => g.files.map((f: any) => f.path)),
      estimated_effort: `${Math.ceil(highGroups.length * 1.5)} hours`,
    });
  }

  // Exact duplicates
  const exactDupes = groups.filter(g => g.type === 'exact');
  if (exactDupes.length > 0) {
    recommendations.push({
      priority: 'high',
      category: 'Exact Duplicates',
      description: `${exactDupes.length} exact duplicate(s) detected. These can be safely extracted into shared modules.`,
      affected_files: exactDupes.flatMap(g => g.files.map((f: any) => f.path)),
      estimated_effort: `${Math.ceil(exactDupes.length)} hour`,
    });
  }

  // Similar duplicates
  const similarDupes = groups.filter(g => g.type === 'similar');
  if (similarDupes.length > 3) {
    recommendations.push({
      priority: 'medium',
      category: 'Similar Code',
      description: `${similarDupes.length} similar code blocks found. Consider creating common patterns or abstractions.`,
      affected_files: similarDupes.flatMap(g => g.files.map((f: any) => f.path)),
      estimated_effort: `${Math.ceil(similarDupes.length * 0.5)} hours`,
    });
  }

  return recommendations.sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return priorityOrder[a.priority as keyof typeof priorityOrder] - priorityOrder[b.priority as keyof typeof priorityOrder];
  });
}

/**
 * Format bytes to human-readable string
 */
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

main();
