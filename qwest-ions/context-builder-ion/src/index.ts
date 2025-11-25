#!/usr/bin/env bun

import { parseArgs } from "util";
import { z } from "zod";
import { execSync } from "child_process";
import { readdirSync, statSync } from "fs";
import { join } from "path";

/**
 * Context Builder Ion - BMAD Method
 * Builds project context from git logs and file activity
 */

// Input Schema
const InputSchema = z.object({
  project_path: z.string().default("./"),
  lookback_hours: z.number().min(1).max(720).default(24),
  include_git: z.boolean().default(true),
  include_files: z.boolean().default(true),
  max_commits: z.number().default(20)
});

// Output Schema
const OutputSchema = z.object({
  success: z.boolean(),
  result: z.object({
    project_path: z.string(),
    context_summary: z.string(),
    recent_commits: z.array(z.object({
      hash: z.string(),
      author: z.string(),
      date: z.string(),
      message: z.string()
    })).optional(),
    recent_files: z.array(z.object({
      path: z.string(),
      modified: z.string(),
      size: z.number()
    })).optional(),
    suggestions: z.array(z.string()),
    generated_at: z.string()
  }),
  metrics: z.object({
    execution_time_ms: z.number(),
    commits_analyzed: z.number(),
    files_analyzed: z.number()
  })
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;

class ContextBuilder {
  /**
   * Build project context
   */
  async build(input: Input): Promise<Output> {
    const startTime = Date.now();
    let commitsAnalyzed = 0;
    let filesAnalyzed = 0;

    try {
      const context: any = {
        project_path: input.project_path,
        suggestions: []
      };

      // Get git commits if enabled
      if (input.include_git) {
        try {
          context.recent_commits = this.getRecentCommits(
            input.project_path,
            input.lookback_hours,
            input.max_commits
          );
          commitsAnalyzed = context.recent_commits.length;
        } catch (error) {
          // Git not available or not a git repo
          context.recent_commits = [];
        }
      }

      // Get recent files if enabled
      if (input.include_files) {
        context.recent_files = this.getRecentFiles(
          input.project_path,
          input.lookback_hours
        );
        filesAnalyzed = context.recent_files.length;
      }

      // Generate context summary
      context.context_summary = this.generateSummary(context);

      // Generate suggestions
      context.suggestions = this.generateSuggestions(context);

      context.generated_at = new Date().toISOString();

      const executionTime = Date.now() - startTime;

      return {
        success: true,
        result: context,
        metrics: {
          execution_time_ms: executionTime,
          commits_analyzed: commitsAnalyzed,
          files_analyzed: filesAnalyzed
        }
      };
    } catch (error) {
      throw new Error(`Context build failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Get recent git commits
   */
  private getRecentCommits(projectPath: string, lookbackHours: number, maxCommits: number): any[] {
    try {
      const since = new Date(Date.now() - lookbackHours * 60 * 60 * 1000).toISOString();
      
      const gitLog = execSync(
        `git log --since="${since}" --max-count=${maxCommits} --pretty=format:"%H|%an|%ai|%s"`,
        { cwd: projectPath, encoding: 'utf-8' }
      );

      if (!gitLog.trim()) {
        return [];
      }

      return gitLog.trim().split('\n').map(line => {
        const [hash, author, date, message] = line.split('|');
        return { hash, author, date, message };
      });
    } catch (error) {
      return [];
    }
  }

  /**
   * Get recently modified files
   */
  private getRecentFiles(projectPath: string, lookbackHours: number): any[] {
    const cutoffTime = Date.now() - (lookbackHours * 60 * 60 * 1000);
    const recentFiles: any[] = [];

    const scanDir = (dir: string, depth: number = 0) => {
      if (depth > 3) return; // Limit recursion depth

      try {
        const items = readdirSync(dir);

        for (const item of items) {
          // Skip common ignore patterns
          if (item.startsWith('.') || item === 'node_modules' || item === 'venv') {
            continue;
          }

          const fullPath = join(dir, item);
          
          try {
            const stats = statSync(fullPath);

            if (stats.isDirectory()) {
              scanDir(fullPath, depth + 1);
            } else if (stats.isFile()) {
              if (stats.mtimeMs > cutoffTime) {
                recentFiles.push({
                  path: fullPath.replace(projectPath, '.'),
                  modified: new Date(stats.mtimeMs).toISOString(),
                  size: stats.size
                });
              }
            }
          } catch (err) {
            // Skip files we can't access
            continue;
          }
        }
      } catch (err) {
        // Skip directories we can't access
        return;
      }
    };

    scanDir(projectPath);

    // Sort by modification time (most recent first)
    return recentFiles
      .sort((a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime())
      .slice(0, 50); // Limit to 50 files
  }

  /**
   * Generate context summary
   */
  private generateSummary(context: any): string {
    const parts: string[] = [];

    // Commits summary
    if (context.recent_commits && context.recent_commits.length > 0) {
      const commits = context.recent_commits;
      parts.push(`Recent activity: ${commits.length} commits in the last period.`);
      
      const latestCommit = commits[0];
      parts.push(`Latest commit: "${latestCommit.message}" by ${latestCommit.author}.`);
    } else {
      parts.push("No recent git commits found.");
    }

    // Files summary
    if (context.recent_files && context.recent_files.length > 0) {
      const files = context.recent_files;
      parts.push(`${files.length} files modified recently.`);
      
      // Group by extension
      const extensions = new Map<string, number>();
      files.forEach((f: any) => {
        const ext = f.path.split('.').pop() || 'unknown';
        extensions.set(ext, (extensions.get(ext) || 0) + 1);
      });
      
      const topExt = Array.from(extensions.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([ext, count]) => `${count} ${ext}`)
        .join(', ');
      
      parts.push(`Most active file types: ${topExt}.`);
    } else {
      parts.push("No recently modified files found.");
    }

    return parts.join(' ');
  }

  /**
   * Generate suggestions based on context
   */
  private generateSuggestions(context: any): string[] {
    const suggestions: string[] = [];

    // Suggest based on commits
    if (context.recent_commits && context.recent_commits.length > 0) {
      const messages = context.recent_commits.map((c: any) => c.message.toLowerCase());
      
      if (messages.some((m: string) => m.includes('fix') || m.includes('bug'))) {
        suggestions.push("Recent bug fixes detected - consider running tests");
      }
      
      if (messages.some((m: string) => m.includes('refactor'))) {
        suggestions.push("Refactoring in progress - review code organization");
      }
      
      if (messages.some((m: string) => m.includes('feature') || m.includes('add'))) {
        suggestions.push("New features added - update documentation");
      }
    }

    // Suggest based on files
    if (context.recent_files && context.recent_files.length > 10) {
      suggestions.push("High file activity - consider committing changes");
    }

    // Default suggestion
    if (suggestions.length === 0) {
      suggestions.push("Continue working on current tasks");
    }

    return suggestions;
  }
}

/**
 * CLI Entry Point
 */
async function main() {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      'project-path': { type: 'string', default: './' },
      'lookback-hours': { type: 'string', default: '24' },
      'include-git': { type: 'boolean', default: true },
      'include-files': { type: 'boolean', default: true },
      'max-commits': { type: 'string', default: '20' },
      verbose: { type: 'boolean', default: false },
      help: { type: 'boolean', default: false }
    },
    strict: true,
    allowPositionals: false
  });

  if (values.help) {
    console.log(`
Context Builder Ion - Build project context from git and files

Usage:
  bun run src/index.ts [options]

Options:
  --project-path <path>    Project path (default: ./)
  --lookback-hours <num>   Hours to look back (default: 24)
  --include-git            Include git commits (default: true)
  --include-files          Include file activity (default: true)
  --max-commits <num>      Max commits to analyze (default: 20)
  --verbose                Verbose output
  --help                   Show this help

Examples:
  bun run src/index.ts
  bun run src/index.ts --lookback-hours 48
  bun run src/index.ts --project-path /path/to/project --verbose
`);
    process.exit(0);
  }

  try {
    // Parse input
    const input = InputSchema.parse({
      project_path: values['project-path'],
      lookback_hours: parseInt(values['lookback-hours'] || '24'),
      include_git: values['include-git'],
      include_files: values['include-files'],
      max_commits: parseInt(values['max-commits'] || '20')
    });

    if (values.verbose) {
      console.error(`[ContextBuilder] Building context for: ${input.project_path}`);
      console.error(`[ContextBuilder] Lookback: ${input.lookback_hours} hours`);
    }

    // Execute
    const builder = new ContextBuilder();
    const output = await builder.build(input);

    // Validate output
    OutputSchema.parse(output);

    if (values.verbose) {
      console.error(`[ContextBuilder] Success: ${output.metrics.commits_analyzed} commits, ${output.metrics.files_analyzed} files`);
      console.error(`[ContextBuilder] Execution time: ${output.metrics.execution_time_ms}ms`);
    }

    // Output JSON
    console.log(JSON.stringify(output, null, 2));

  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('Validation error:', error.errors);
      process.exit(1);
    }

    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.main) {
  main();
}

export { ContextBuilder, InputSchema, OutputSchema };
export type { Input, Output };
