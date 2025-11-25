# Context Builder Ion

**Type:** Project Analysis  
**Method:** BMAD  
**Status:** Operational

## Purpose

Builds project context from git logs and file activity to answer "What was I working on?"

## Capabilities

- Git commit history analysis
- Recent file modification tracking
- Context summary generation
- Smart suggestions based on activity
- Configurable lookback period

## Input Schema

```typescript
{
  project_path?: string,        // Default: "./"
  lookback_hours?: number,       // Default: 24
  include_git?: boolean,         // Default: true
  include_files?: boolean,       // Default: true
  max_commits?: number          // Default: 20
}
```

## Output Schema

```typescript
{
  success: boolean,
  result: {
    project_path: string,
    context_summary: string,
    recent_commits?: Array<{
      hash: string,
      author: string,
      date: string,
      message: string
    }>,
    recent_files?: Array<{
      path: string,
      modified: string,
      size: number
    }>,
    suggestions: string[],
    generated_at: string
  },
  metrics: {
    execution_time_ms: number,
    commits_analyzed: number,
    files_analyzed: number
  }
}
```

## Usage

```bash
# Build context for current directory
bun run src/index.ts

# Look back 48 hours
bun run src/index.ts --lookback-hours 48

# Specific project
bun run src/index.ts --project-path /path/to/project
```

## BMAD Workflow

1. **Build:** Scan git logs and file system
2. **Measure:** Track commits and file modifications
3. **Analyze:** Generate context summary and patterns
4. **Deploy:** Return actionable context with suggestions

## Performance

- Execution: ~50-200ms
- Git analysis: ~20-50ms
- File scanning: ~30-150ms (depends on project size)
- Success rate: 95%+

## Error Handling

- Git not available (falls back to file-only)
- Not a git repository (file analysis only)
- Permission errors (skips inaccessible files)
- Large projects (limits depth and file count)
