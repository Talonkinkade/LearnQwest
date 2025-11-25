import { z } from 'zod';

// Input schemas (from other Ions)
export const ScanResultSchema = z.object({
  project_root: z.string(),
  findings: z.object({ files: z.array(z.any()).optional() }).optional(),
});

export const DuplicateReportSchema = z.object({
  scan_summary: z.object({
    duplicates_found: z.number(),
    total_space_savings: z.number(),
  }),
  duplicate_groups: z.array(z.object({
    refactor_priority: z.enum(['critical', 'high', 'medium', 'low']),
    space_savings_potential: z.number(),
  })),
  recommendations: z.array(z.any()),
});

export const DeadCodeReportSchema = z.object({
  analysis_summary: z.object({
    unused_entities: z.number(),
    unused_files: z.number(),
    disk_space_reclaimable: z.number(),
  }),
  unused_code: z.array(z.any()),
  recommendations: z.array(z.any()),
});

export const GroupingPlanSchema = z.object({
  summary: z.object({
    groups_suggested: z.number(),
    misplaced_files: z.number(),
  }),
  file_groups: z.array(z.any()),
  recommendations: z.array(z.any()),
});

// Output schemas
export const RefactorActionSchema = z.object({
  id: z.string(),
  type: z.enum(['duplicate', 'dead_code', 'reorganization']),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  title: z.string(),
  description: z.string(),
  impact_score: z.number(),
  effort_hours: z.number(),
  roi: z.number(),
  phase: z.number(),
  dependencies: z.array(z.string()),
  files_affected: z.array(z.string()),
  estimated_savings: z.string(),
});

export type RefactorAction = z.infer<typeof RefactorActionSchema>;

export const RefactorRoadmapSchema = z.object({
  generated_at: z.string(),
  project_root: z.string(),
  aggregate_metrics: z.object({
    total_duplicates: z.number(),
    total_unused_code: z.number(),
    total_misplaced_files: z.number(),
    total_disk_savings_kb: z.number(),
    total_actions: z.number(),
  }),
  phases: z.array(z.object({
    phase_number: z.number(),
    name: z.string(),
    actions: z.array(RefactorActionSchema),
    total_effort_hours: z.number(),
    expected_impact: z.string(),
  })),
  timeline: z.object({
    estimated_total_hours: z.number(),
    estimated_weeks: z.number(),
  }),
  dashboard_path: z.string().optional(),
});

export type RefactorRoadmap = z.infer<typeof RefactorRoadmapSchema>;

export const ConfigSchema = z.object({
  ion_name: z.string(),
  version: z.string(),
  weights: z.object({
    impact: z.number(),
    effort: z.number(),
    risk: z.number(),
    dependencies: z.number(),
  }),
  phases: z.object({
    quick_wins: z.object({ max_effort_hours: z.number(), min_roi: z.number() }),
    medium_refactors: z.object({ max_effort_hours: z.number(), min_roi: z.number() }),
    large_refactors: z.object({ max_effort_hours: z.number(), min_roi: z.number() }),
  }),
  dashboard: z.object({
    title: z.string(),
    show_metrics: z.boolean(),
    show_timeline: z.boolean(),
    show_progress: z.boolean(),
    theme: z.string(),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
