import type { Config, RefactorAction } from './types';
import { logger } from './logger';

export class RefactorPlanner {
  constructor(private config: Config) {}

  plan(duplicateReport: any, deadCodeReport: any, groupingPlan: any) {
    logger.section('Refactor Planning - Aggregating All Analysis');

    // Step 1: Extract actions from all reports
    const actions: RefactorAction[] = [];
    let actionId = 1;

    // From duplicate report
    if (duplicateReport?.duplicate_groups) {
      for (const group of duplicateReport.duplicate_groups) {
        actions.push({
          id: `action-${actionId++}`,
          type: 'duplicate',
          priority: group.refactor_priority,
          title: `Refactor duplicate code group`,
          description: `${group.files.length} files contain duplicate code`,
          impact_score: this.calculateImpact(group.space_savings_potential, 'duplicate'),
          effort_hours: this.estimateEffort(group.files.length, 'duplicate'),
          roi: 0,
          phase: 0,
          dependencies: [],
          files_affected: group.files.map((f: any) => f.path),
          estimated_savings: `${Math.round(group.space_savings_potential / 1024)} KB`,
        });
      }
    }

    // From dead code report
    if (deadCodeReport?.unused_files) {
      for (const file of deadCodeReport.unused_files) {
        actions.push({
          id: `action-${actionId++}`,
          type: 'dead_code',
          priority: file.size > 50000 ? 'high' : 'medium',
          title: `Remove unused file`,
          description: file.reason,
          impact_score: this.calculateImpact(file.size, 'dead_code'),
          effort_hours: 0.5,
          roi: 0,
          phase: 0,
          dependencies: [],
          files_affected: [file.path],
          estimated_savings: `${Math.round(file.size / 1024)} KB`,
        });
      }
    }

    // From grouping plan
    if (groupingPlan?.misplaced_files) {
      for (const file of groupingPlan.misplaced_files) {
        actions.push({
          id: `action-${actionId++}`,
          type: 'reorganization',
          priority: 'medium',
          title: `Reorganize misplaced file`,
          description: file.reason,
          impact_score: this.calculateImpact(file.confidence * 100, 'reorganization'),
          effort_hours: 1,
          roi: 0,
          phase: 0,
          dependencies: [],
          files_affected: [file.file],
          estimated_savings: 'Improved maintainability',
        });
      }
    }

    logger.info(`Extracted ${actions.length} refactor actions`);

    // Step 2: Calculate ROI for each action
    for (const action of actions) {
      action.roi = action.impact_score / (action.effort_hours || 1);
    }

    // Step 3: Sort by priority and ROI
    actions.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.roi - a.roi;
    });

    // Step 4: Assign to phases
    const phases = this.assignPhases(actions);

    logger.success(`Organized into ${phases.length} phases`);

    return { actions, phases };
  }

  private calculateImpact(value: number, type: string): number {
    // Simple impact scoring (0-100)
    switch (type) {
      case 'duplicate':
        return Math.min(100, value / 1024); // KB-based
      case 'dead_code':
        return Math.min(100, value / 5120); // Larger files = more impact
      case 'reorganization':
        return Math.min(100, value); // Confidence-based
      default:
        return 50;
    }
  }

  private estimateEffort(filesCount: number, type: string): number {
    // Estimate effort in hours
    switch (type) {
      case 'duplicate':
        return filesCount * 0.5; // 30 min per file
      case 'dead_code':
        return 0.5; // Fixed 30 min
      case 'reorganization':
        return 1; // 1 hour per file
      default:
        return 1;
    }
  }

  private assignPhases(actions: RefactorAction[]) {
    const phases = [
      { phase_number: 1, name: 'Quick Wins', actions: [] as RefactorAction[], total_effort_hours: 0, expected_impact: 'High impact, low effort' },
      { phase_number: 2, name: 'Medium Refactors', actions: [] as RefactorAction[], total_effort_hours: 0, expected_impact: 'Balanced impact and effort' },
      { phase_number: 3, name: 'Large Refactors', actions: [] as RefactorAction[], total_effort_hours: 0, expected_impact: 'High effort, high impact' },
    ];

    for (const action of actions) {
      const config = this.config.phases;

      if (action.effort_hours <= config.quick_wins.max_effort_hours && action.roi >= config.quick_wins.min_roi) {
        action.phase = 1;
        phases[0].actions.push(action);
        phases[0].total_effort_hours += action.effort_hours;
      } else if (action.effort_hours <= config.medium_refactors.max_effort_hours) {
        action.phase = 2;
        phases[1].actions.push(action);
        phases[1].total_effort_hours += action.effort_hours;
      } else {
        action.phase = 3;
        phases[2].actions.push(action);
        phases[2].total_effort_hours += action.effort_hours;
      }
    }

    return phases.filter(p => p.actions.length > 0);
  }
}
