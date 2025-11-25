# Context Builder Ion

Build project context from git logs and file activity.

## Installation

```bash
bun install
```

## Usage

```bash
# Build context
bun run src/index.ts

# Look back 48 hours
bun run src/index.ts --lookback-hours 48

# Verbose output
bun run src/index.ts --verbose
```

## Features

- ✅ Git commit history analysis
- ✅ Recent file modification tracking
- ✅ Context summary generation
- ✅ Smart suggestions
- ✅ Configurable lookback period

## Output

```json
{
  "success": true,
  "result": {
    "context_summary": "Recent activity: 5 commits...",
    "recent_commits": [...],
    "recent_files": [...],
    "suggestions": [
      "Recent bug fixes detected - consider running tests"
    ]
  },
  "metrics": {
    "execution_time_ms": 120,
    "commits_analyzed": 5,
    "files_analyzed": 23
  }
}
```

## Status

✅ Operational
