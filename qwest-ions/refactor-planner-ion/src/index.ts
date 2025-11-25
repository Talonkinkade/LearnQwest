#!/usr/bin/env bun
import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { Command } from 'commander';
import { parse as parseYaml } from 'yaml';
import { ConfigSchema, RefactorRoadmapSchema, type RefactorRoadmap } from './types';
import { RefactorPlanner } from './planner';
import { logger } from './logger';

const program = new Command();

program
  .name('refactor-planner-ion')
  .description('BMAD Ion orchestrator - creates prioritized refactor roadmap')
  .version('1.0.0')
  .requiredOption('--scan <path>', 'Path to scan-results.json')
  .requiredOption('--duplicates <path>', 'Path to duplicates-report.json')
  .requiredOption('--dead-code <path>', 'Path to dead-code-report.json')
  .requiredOption('--grouping <path>', 'Path to grouping-plan.json')
  .option('-o, --output <path>', 'Output path (default: ./refactor-roadmap.json)')
  .option('-c, --config <path>', 'Config path (default: ./config.yaml)')
  .option('--dashboard', 'Generate HTML dashboard')
  .parse(process.argv);

const options = program.opts();

async function main() {
  try {
    logger.section('Refactor Planner Ion - BMAD Method Orchestrator');

    // Load config
    const configPath = resolve(options.config || './config.yaml');
    const config = ConfigSchema.parse(parseYaml(readFileSync(configPath, 'utf-8')));

    // Load all reports
    logger.info('Loading analysis reports...');

    const scanResult = JSON.parse(readFileSync(resolve(options.scan), 'utf-8'));
    const duplicateReport = JSON.parse(readFileSync(resolve(options.duplicates), 'utf-8'));
    const deadCodeReport = JSON.parse(readFileSync(resolve(options.dead_code), 'utf-8'));
    const groupingPlan = JSON.parse(readFileSync(resolve(options.grouping), 'utf-8'));

    logger.success('All reports loaded');

    // Run planning
    const planner = new RefactorPlanner(config);
    const { actions, phases } = planner.plan(duplicateReport, deadCodeReport, groupingPlan);

    // Calculate aggregates
    const totalEffortHours = phases.reduce((sum, p) => sum + p.total_effort_hours, 0);
    const totalDiskSavings =
      (duplicateReport.scan_summary?.total_space_savings || 0) +
      (deadCodeReport.analysis_summary?.disk_space_reclaimable || 0);

    const roadmap: RefactorRoadmap = {
      generated_at: new Date().toISOString(),
      project_root: scanResult.project_root,
      aggregate_metrics: {
        total_duplicates: duplicateReport.scan_summary?.duplicates_found || 0,
        total_unused_code: deadCodeReport.analysis_summary?.unused_entities || 0,
        total_misplaced_files: groupingPlan.summary?.misplaced_files || 0,
        total_disk_savings_kb: Math.round(totalDiskSavings / 1024),
        total_actions: actions.length,
      },
      phases,
      timeline: {
        estimated_total_hours: totalEffortHours,
        estimated_weeks: Math.ceil(totalEffortHours / 20), // 20 hours per week
      },
    };

    // Validate
    RefactorRoadmapSchema.parse(roadmap);

    // Write output
    const outputPath = resolve(options.output || './refactor-roadmap.json');
    writeFileSync(outputPath, JSON.stringify(roadmap, null, 2));
    logger.success(`Roadmap written to: ${outputPath}`);

    // Generate dashboard if requested
    if (options.dashboard) {
      const dashboardPath = await generateDashboard(roadmap, config);
      roadmap.dashboard_path = dashboardPath;
      writeFileSync(outputPath, JSON.stringify(roadmap, null, 2));
      logger.success(`Dashboard generated: ${dashboardPath}`);
    }

    // Display summary
    displaySummary(roadmap);

    process.exit(0);
  } catch (error) {
    logger.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

async function generateDashboard(roadmap: RefactorRoadmap, config: any): Promise<string> {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${config.dashboard.title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; background: #1a1a1a; color: #fff; padding: 2rem; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { font-size: 2.5rem; margin-bottom: 2rem; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 3rem; }
    .metric { background: #2a2a2a; padding: 1.5rem; border-radius: 8px; }
    .metric-value { font-size: 2rem; font-weight: bold; color: #4CAF50; }
    .metric-label { color: #999; margin-top: 0.5rem; }
    .phase { background: #2a2a2a; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; }
    .phase-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .phase-title { font-size: 1.5rem; }
    .phase-effort { color: #999; }
    .action { background: #333; padding: 1rem; border-radius: 4px; margin-bottom: 0.5rem; }
    .action-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
    .priority { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600; }
    .priority-critical { background: #f44336; }
    .priority-high { background: #ff9800; }
    .priority-medium { background: #2196F3; }
    .priority-low { background: #4CAF50; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${config.dashboard.title}</h1>

    <div class="metrics">
      <div class="metric">
        <div class="metric-value">${roadmap.aggregate_metrics.total_actions}</div>
        <div class="metric-label">Total Actions</div>
      </div>
      <div class="metric">
        <div class="metric-value">${roadmap.aggregate_metrics.total_duplicates}</div>
        <div class="metric-label">Duplicates</div>
      </div>
      <div class="metric">
        <div class="metric-value">${roadmap.aggregate_metrics.total_unused_code}</div>
        <div class="metric-label">Unused Code</div>
      </div>
      <div class="metric">
        <div class="metric-value">${roadmap.aggregate_metrics.total_disk_savings_kb} KB</div>
        <div class="metric-label">Disk Savings</div>
      </div>
      <div class="metric">
        <div class="metric-value">${roadmap.timeline.estimated_total_hours}h</div>
        <div class="metric-label">Est. Time</div>
      </div>
      <div class="metric">
        <div class="metric-value">${roadmap.timeline.estimated_weeks}w</div>
        <div class="metric-label">Est. Weeks</div>
      </div>
    </div>

    ${roadmap.phases.map(phase => `
      <div class="phase">
        <div class="phase-header">
          <div class="phase-title">Phase ${phase.phase_number}: ${phase.name}</div>
          <div class="phase-effort">${phase.total_effort_hours.toFixed(1)}h effort</div>
        </div>
        ${phase.actions.map(action => `
          <div class="action">
            <div class="action-header">
              <div>${action.title}</div>
              <span class="priority priority-${action.priority}">${action.priority.toUpperCase()}</span>
            </div>
            <div style="color: #999; font-size: 0.875rem;">${action.description}</div>
            <div style="margin-top: 0.5rem; font-size: 0.875rem;">
              <span>⏱️ ${action.effort_hours}h</span>
              <span style="margin-left: 1rem;">💾 ${action.estimated_savings}</span>
              <span style="margin-left: 1rem;">📈 ROI: ${action.roi.toFixed(1)}</span>
            </div>
          </div>
        `).join('')}
      </div>
    `).join('')}
  </div>
</body>
</html>`;

  const dashboardPath = 'refactor-dashboard.html';
  writeFileSync(dashboardPath, html);
  return dashboardPath;
}

function displaySummary(roadmap: RefactorRoadmap) {
  logger.section('Refactor Roadmap Summary');
  logger.info(`Total actions: ${roadmap.aggregate_metrics.total_actions}`);
  logger.info(`Duplicates: ${roadmap.aggregate_metrics.total_duplicates}`);
  logger.info(`Unused code: ${roadmap.aggregate_metrics.total_unused_code}`);
  logger.info(`Misplaced files: ${roadmap.aggregate_metrics.total_misplaced_files}`);
  logger.info(`Disk savings: ${roadmap.aggregate_metrics.total_disk_savings_kb} KB`);
  logger.info(`Estimated time: ${roadmap.timeline.estimated_total_hours} hours (${roadmap.timeline.estimated_weeks} weeks)`);

  logger.subsection('Phases');
  roadmap.phases.forEach(phase => {
    logger.info(`Phase ${phase.phase_number}: ${phase.name} - ${phase.actions.length} actions, ${phase.total_effort_hours.toFixed(1)}h`);
  });
}

main();
