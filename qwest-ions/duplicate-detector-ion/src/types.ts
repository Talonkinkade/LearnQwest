import { z } from 'zod';

// Input schema - expecting scan-results.json from Code Scanner Ion
export const ScanResultSchema = z.object({
  workflow_version: z.string(),
  timestamps: z.object({
    started: z.string(),
    last_updated: z.string(),
    completed: z.string().optional(),
  }),
  mode: z.enum(['initial_scan', 'full_rescan', 'deep_dive']),
  scan_level: z.enum(['quick', 'deep', 'exhaustive']),
  project_root: z.string(),
  output_folder: z.string(),
  completed_steps: z.array(z.object({
    step: z.string(),
    status: z.enum(['completed', 'partial', 'failed']),
    timestamp: z.string().optional(),
    outputs: z.array(z.string()).optional(),
    summary: z.string().optional(),
  })),
  current_step: z.string(),
  findings: z.object({
    project_classification: z.object({
      repository_type: z.string(),
      parts_count: z.number(),
      primary_language: z.string(),
      architecture_type: z.string(),
    }).optional(),
    technology_stack: z.array(z.object({
      part_id: z.string(),
      tech_summary: z.string(),
    })).optional(),
    batches_completed: z.array(z.object({
      path: z.string(),
      files_scanned: z.number(),
      summary: z.string(),
    })).optional(),
    files: z.array(z.object({
      path: z.string(),
      size: z.number(),
      lines: z.number(),
      extension: z.string(),
      hash: z.string().optional(),
    })).optional(),
  }).optional(),
  outputs_generated: z.array(z.string()).optional(),
});

export type ScanResult = z.infer<typeof ScanResultSchema>;

// File content schema
export const FileContentSchema = z.object({
  path: z.string(),
  content: z.string(),
  hash: z.string(),
  lines: z.number(),
  size: z.number(),
});

export type FileContent = z.infer<typeof FileContentSchema>;

// Duplicate group schema
export const DuplicateGroupSchema = z.object({
  id: z.string(),
  similarity: z.number(), // 0-100
  type: z.enum(['exact', 'similar']),
  files: z.array(z.object({
    path: z.string(),
    lines: z.string(), // e.g. "10-45"
    hash: z.string(),
  })),
  sample_code: z.string(), // First occurrence
  lines_count: z.number(),
  space_savings_potential: z.number(), // bytes that could be saved
  refactor_priority: z.enum(['critical', 'high', 'medium', 'low']),
  recommendation: z.string(),
});

export type DuplicateGroup = z.infer<typeof DuplicateGroupSchema>;

// Pattern-based duplicate group schema
export const PatternGroupSchema = z.object({
  pattern: z.string(),
  occurrences: z.number(),
  files: z.array(z.string()),
  suggested_solution: z.string(),
});

export type PatternGroup = z.infer<typeof PatternGroupSchema>;

// Output schema
export const DuplicateReportSchema = z.object({
  generated_at: z.string(),
  project_root: z.string(),
  scan_summary: z.object({
    files_analyzed: z.number(),
    total_lines: z.number(),
    duplicates_found: z.number(),
    exact_duplicates: z.number(),
    similar_duplicates: z.number(),
    total_space_savings: z.number(), // bytes
  }),
  duplicate_groups: z.array(DuplicateGroupSchema),
  pattern_groups: z.array(PatternGroupSchema),
  file_path_patterns: z.array(z.object({
    pattern: z.string(),
    files: z.array(z.string()),
    similarity: z.number(),
  })),
  recommendations: z.array(z.object({
    priority: z.enum(['critical', 'high', 'medium', 'low']),
    category: z.string(),
    description: z.string(),
    affected_files: z.array(z.string()),
    estimated_effort: z.string(),
  })),
});

export type DuplicateReport = z.infer<typeof DuplicateReportSchema>;

// Configuration schema
export const ConfigSchema = z.object({
  ion_name: z.string(),
  version: z.string(),
  similarity_thresholds: z.object({
    exact_match: z.number().min(95).max(100),
    similar_match_min: z.number().min(50).max(95),
    similar_match_max: z.number().min(50).max(95),
  }),
  ignore_patterns: z.array(z.string()),
  minimum_lines: z.number().min(3),
  file_extensions: z.array(z.string()),
  refactor_priority_rules: z.object({
    critical_lines: z.number(),
    high_lines: z.number(),
    medium_lines: z.number(),
    critical_occurrences: z.number(),
    high_occurrences: z.number(),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
