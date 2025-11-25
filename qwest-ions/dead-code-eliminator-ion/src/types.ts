import { z } from 'zod';

// Input schema - scan results from Code Scanner Ion
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
  completed_steps: z.array(z.any()),
  current_step: z.string(),
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

// Code entity schemas
export const CodeEntitySchema = z.object({
  name: z.string(),
  type: z.enum(['function', 'class', 'variable', 'interface', 'type', 'export']),
  file: z.string(),
  line: z.number(),
  exported: z.boolean(),
  used: z.boolean(),
  usages: z.array(z.object({
    file: z.string(),
    line: z.number(),
  })),
});

export type CodeEntity = z.infer<typeof CodeEntitySchema>;

// File reference schema
export const FileReferenceSchema = z.object({
  path: z.string(),
  imports: z.array(z.string()),
  exports: z.array(z.string()),
  referenced_by: z.array(z.string()),
  is_entry_point: z.boolean(),
  is_orphaned: z.boolean(),
});

export type FileReference = z.infer<typeof FileReferenceSchema>;

// Dependency schema
export const DependencySchema = z.object({
  name: z.string(),
  version: z.string(),
  type: z.enum(['dependency', 'devDependency', 'peerDependency']),
  used: z.boolean(),
  imported_in: z.array(z.string()),
});

export type Dependency = z.infer<typeof DependencySchema>;

// Unused code item schema
export const UnusedCodeItemSchema = z.object({
  id: z.string(),
  type: z.enum(['function', 'class', 'variable', 'file', 'dependency']),
  name: z.string(),
  file: z.string().optional(),
  line: z.number().optional(),
  size_bytes: z.number(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  reason: z.string(),
  safe_to_delete: z.boolean(),
  recommendation: z.string(),
});

export type UnusedCodeItem = z.infer<typeof UnusedCodeItemSchema>;

// Output schema
export const DeadCodeReportSchema = z.object({
  generated_at: z.string(),
  project_root: z.string(),
  analysis_summary: z.object({
    files_analyzed: z.number(),
    entities_found: z.number(),
    unused_entities: z.number(),
    unused_files: z.number(),
    unused_dependencies: z.number(),
    disk_space_reclaimable: z.number(),
  }),
  unused_code: z.array(UnusedCodeItemSchema),
  unused_files: z.array(z.object({
    path: z.string(),
    size: z.number(),
    reason: z.string(),
    safe_to_delete: z.boolean(),
  })),
  unused_dependencies: z.array(DependencySchema),
  deletion_scripts: z.object({
    bash: z.string(),
    powershell: z.string(),
    backup: z.string().optional(),
  }),
  recommendations: z.array(z.object({
    priority: z.enum(['critical', 'high', 'medium', 'low']),
    category: z.string(),
    description: z.string(),
    affected_items: z.array(z.string()),
    estimated_savings: z.string(),
  })),
});

export type DeadCodeReport = z.infer<typeof DeadCodeReportSchema>;

// Config schema
export const ConfigSchema = z.object({
  ion_name: z.string(),
  version: z.string(),
  analysis: z.object({
    check_functions: z.boolean(),
    check_classes: z.boolean(),
    check_variables: z.boolean(),
    check_imports: z.boolean(),
    check_files: z.boolean(),
    check_dependencies: z.boolean(),
  }),
  entry_points: z.array(z.string()),
  ignore_patterns: z.array(z.string()),
  file_extensions: z.array(z.string()),
  dependencies: z.object({
    check_package_json: z.boolean(),
    check_devDependencies: z.boolean(),
    ignore_types_packages: z.boolean(),
  }),
  size_thresholds: z.object({
    critical_kb: z.number(),
    high_kb: z.number(),
    medium_kb: z.number(),
  }),
  safety: z.object({
    generate_backup_script: z.boolean(),
    require_confirmation: z.boolean(),
    preserve_git_history: z.boolean(),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
