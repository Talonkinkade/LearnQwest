import { z } from 'zod';

export const ScanResultSchema = z.object({
  workflow_version: z.string(),
  project_root: z.string(),
  findings: z.object({
    files: z.array(z.object({
      path: z.string(),
      size: z.number(),
      lines: z.number(),
      extension: z.string(),
    })).optional(),
  }).optional(),
});

export type ScanResult = z.infer<typeof ScanResultSchema>;

export const FileGroupSchema = z.object({
  id: z.string(),
  name: z.string(),
  strategy: z.enum(['functional', 'layered', 'domain']),
  files: z.array(z.string()),
  suggested_location: z.string(),
  confidence: z.number(),
  reason: z.string(),
});

export type FileGroup = z.infer<typeof FileGroupSchema>;

export const MisplacedFileSchema = z.object({
  file: z.string(),
  current_location: z.string(),
  suggested_location: z.string(),
  confidence: z.number(),
  reason: z.string(),
});

export type MisplacedFile = z.infer<typeof MisplacedFileSchema>;

export const MigrationScriptSchema = z.object({
  bash: z.string(),
  powershell: z.string(),
  rollback_bash: z.string().optional(),
  rollback_powershell: z.string().optional(),
});

export type MigrationScript = z.infer<typeof MigrationScriptSchema>;

export const GroupingPlanSchema = z.object({
  generated_at: z.string(),
  project_root: z.string(),
  summary: z.object({
    files_analyzed: z.number(),
    groups_suggested: z.number(),
    misplaced_files: z.number(),
    migrations_needed: z.number(),
  }),
  file_groups: z.array(FileGroupSchema),
  misplaced_files: z.array(MisplacedFileSchema),
  proposed_structure: z.record(z.array(z.string())),
  migration_scripts: MigrationScriptSchema,
  recommendations: z.array(z.object({
    priority: z.enum(['high', 'medium', 'low']),
    description: z.string(),
  })),
});

export type GroupingPlan = z.infer<typeof GroupingPlanSchema>;

export const ConfigSchema = z.object({
  ion_name: z.string(),
  version: z.string(),
  strategies: z.array(z.enum(['functional', 'layered', 'domain'])),
  analysis: z.object({
    min_group_size: z.number(),
    confidence_threshold: z.number(),
    max_depth: z.number(),
  }),
  preserve_patterns: z.array(z.string()),
  ignore_patterns: z.array(z.string()),
  git: z.object({
    use_git_mv: z.boolean(),
    generate_rollback: z.boolean(),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
