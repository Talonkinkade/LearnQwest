#!/usr/bin/env bun
import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { Command } from 'commander';
import { parse as parseYaml } from 'yaml';
import { ScanResultSchema, GroupingPlanSchema, ConfigSchema, type GroupingPlan } from './types';
import { CodeGrouper } from './grouper';
import { logger } from './logger';

const program = new Command();

program
  .name('code-grouper-ion')
  .description('BMAD Ion for analyzing code organization')
  .version('1.0.0')
  .requiredOption('-i, --input <path>', 'Path to scan-results.json')
  .option('-o, --output <path>', 'Output path (default: ./grouping-plan.json)')
  .option('-c, --config <path>', 'Config path (default: ./config.yaml)')
  .parse(process.argv);

const options = program.opts();

async function main() {
  try {
    logger.section('Code Grouper Ion - BMAD Method');

    const configPath = resolve(options.config || './config.yaml');
    const config = ConfigSchema.parse(parseYaml(readFileSync(configPath, 'utf-8')));

    const inputPath = resolve(options.input);
    const scanResult = ScanResultSchema.parse(JSON.parse(readFileSync(inputPath, 'utf-8')));

    const grouper = new CodeGrouper(config, scanResult.project_root);
    const results = await grouper.analyze(scanResult);

    const migrationScripts = generateMigrationScripts(results.misplacedFiles, config);

    const plan: GroupingPlan = {
      generated_at: new Date().toISOString(),
      project_root: scanResult.project_root,
      summary: {
        files_analyzed: scanResult.findings?.files?.length || 0,
        groups_suggested: results.fileGroups.length,
        misplaced_files: results.misplacedFiles.length,
        migrations_needed: results.misplacedFiles.length,
      },
      file_groups: results.fileGroups,
      misplaced_files: results.misplacedFiles,
      proposed_structure: results.proposedStructure,
      migration_scripts: migrationScripts,
      recommendations: generateRecommendations(results),
    };

    GroupingPlanSchema.parse(plan);

    const outputPath = resolve(options.output || './grouping-plan.json');
    writeFileSync(outputPath, JSON.stringify(plan, null, 2));

    logger.success(`Plan written to: ${outputPath}`);
    displaySummary(plan);

    process.exit(0);
  } catch (error) {
    logger.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

function generateMigrationScripts(misplacedFiles: any[], config: any) {
  const mvCmd = config.git.use_git_mv ? 'git mv' : 'mv';
  const bashLines = ['#!/bin/bash', '# Migration script', ''];
  const psLines = ['# Migration script (PowerShell)', ''];
  const rollbackBash = config.git.generate_rollback ? ['#!/bin/bash', '# Rollback script', ''] : [];
  const rollbackPs = config.git.generate_rollback ? ['# Rollback script (PowerShell)', ''] : [];

  for (const f of misplacedFiles) {
    bashLines.push(`mkdir -p "$(dirname ${f.suggested_location})"`);
    bashLines.push(`${mvCmd} "${f.file}" "${f.suggested_location}/${f.file.split('/').pop()}"`);

    psLines.push(`New-Item -ItemType Directory -Force -Path (Split-Path "${f.suggested_location}")`);
    psLines.push(`Move-Item "${f.file}" "${f.suggested_location}/${f.file.split('/').pop()}"`);

    if (config.git.generate_rollback) {
      rollbackBash.push(`${mvCmd} "${f.suggested_location}/${f.file.split('/').pop()}" "${f.file}"`);
      rollbackPs.push(`Move-Item "${f.suggested_location}/${f.file.split('/').pop()}" "${f.file}"`);
    }
  }

  return {
    bash: bashLines.join('\n'),
    powershell: psLines.join('\n'),
    rollback_bash: rollbackBash.length > 0 ? rollbackBash.join('\n') : undefined,
    rollback_powershell: rollbackPs.length > 0 ? rollbackPs.join('\n') : undefined,
  };
}

function generateRecommendations(results: any) {
  const recs = [];

  if (results.misplacedFiles.length > 0) {
    recs.push({
      priority: 'high' as const,
      description: `${results.misplacedFiles.length} files could be better organized`,
    });
  }

  if (results.fileGroups.length > 0) {
    recs.push({
      priority: 'medium' as const,
      description: `${results.fileGroups.length} functional groups identified for organization`,
    });
  }

  return recs;
}

function displaySummary(plan: GroupingPlan) {
  logger.section('Summary');
  logger.info(`Files analyzed: ${plan.summary.files_analyzed}`);
  logger.info(`Groups suggested: ${plan.summary.groups_suggested}`);
  logger.info(`Misplaced files: ${plan.summary.misplaced_files}`);
  logger.info(`Migrations needed: ${plan.summary.migrations_needed}`);
}

main();
