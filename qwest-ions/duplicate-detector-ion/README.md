# Duplicate Detector Ion

**BMAD Method Ion for detecting exact and similar code duplicates**

## Overview

The Duplicate Detector Ion analyzes codebase scan results from the Code Scanner Ion to identify:

- **Exact duplicates** (100% identical code)
- **Similar duplicates** (55-95% similarity using fuzzy hashing)
- **Pattern-based duplicates** (repeated code structures)
- **File path patterns** (organizational groupings)

### Features

✅ Detects exact code duplicates (100% match)
✅ Finds similar code blocks (55-95% similarity)
✅ Groups duplicates by file path patterns
✅ Calculates space savings potential
✅ Ranks by refactor priority (critical/high/medium/low)
✅ CLI-first design for token optimization
✅ Zod validation for type safety
✅ Production-ready error handling

## Installation

```bash
cd qwest-ions/duplicate-detector-ion
bun install
```

## Usage

### Basic Usage

```bash
bun run src/index.ts \
  --input /path/to/scan-results.json \
  --output /path/to/duplicates-report.json
```

### With Custom Config

```bash
bun run src/index.ts \
  --input ./scan-results.json \
  --output ./duplicates-report.json \
  --config ./custom-config.yaml
```

### Verbose Mode

```bash
bun run src/index.ts \
  --input ./scan-results.json \
  --verbose
```

## Input Format

Expects `scan-results.json` from Code Scanner Ion:

```json
{
  "workflow_version": "1.0.0",
  "project_root": "/path/to/project",
  "findings": {
    "files": [
      {
        "path": "src/file.ts",
        "size": 1024,
        "lines": 50,
        "extension": ".ts",
        "hash": "abc123"
      }
    ]
  }
}
```

## Output Format

Generates `duplicates-report.json`:

```json
{
  "generated_at": "2025-11-19T00:00:00Z",
  "project_root": "/path/to/project",
  "scan_summary": {
    "files_analyzed": 150,
    "total_lines": 50000,
    "duplicates_found": 12,
    "exact_duplicates": 5,
    "similar_duplicates": 7,
    "total_space_savings": 102400
  },
  "duplicate_groups": [
    {
      "id": "exact-1",
      "similarity": 100,
      "type": "exact",
      "files": [
        {
          "path": "src/file1.ts",
          "lines": "1-50",
          "hash": "abc123"
        }
      ],
      "sample_code": "...",
      "lines_count": 50,
      "space_savings_potential": 2048,
      "refactor_priority": "high",
      "recommendation": "Consider extracting..."
    }
  ],
  "pattern_groups": [...],
  "file_path_patterns": [...],
  "recommendations": [...]
}
```

## Configuration

Edit `config.yaml` to customize detection:

```yaml
# Similarity thresholds
similarity_thresholds:
  exact_match: 100
  similar_match_min: 55
  similar_match_max: 95

# Minimum lines to consider
minimum_lines: 5

# File extensions to analyze
file_extensions:
  - ".ts"
  - ".tsx"
  - ".js"
  - ".jsx"
  - ".py"

# Ignore patterns
ignore_patterns:
  - "**/node_modules/**"
  - "**/dist/**"
  - "**/build/**"

# Priority rules
refactor_priority_rules:
  critical_lines: 100      # >100 lines = critical
  high_lines: 50           # >50 lines = high
  medium_lines: 20         # >20 lines = medium
  critical_occurrences: 5  # >5 occurrences = critical
  high_occurrences: 3      # >3 occurrences = high
```

## Development

### Run Tests

```bash
bun test
```

### Watch Mode

```bash
bun test --watch
```

### Type Checking

```bash
bun run typecheck
```

### Linting

```bash
bun run lint
```

### Formatting

```bash
bun run format
```

## How It Works

### 1. Load File Contents
- Reads all files from scan results
- Filters by extension and ignore patterns
- Calculates content hashes

### 2. Detect Exact Duplicates
- Groups files by content hash
- Identifies 100% identical code
- Calculates space savings

### 3. Detect Similar Duplicates
- Compares files pairwise
- Uses line-based similarity algorithm
- Groups files with 55-95% similarity

### 4. Detect Pattern Duplicates
- Extracts code patterns (functions, classes, imports)
- Groups by repeated patterns
- Identifies opportunities for abstraction

### 5. Analyze File Paths
- Groups files by directory structure
- Identifies organizational patterns
- Suggests reorganization opportunities

### 6. Calculate Priorities
- Ranks by lines count and occurrences
- Assigns critical/high/medium/low priority
- Generates actionable recommendations

## Refactor Priority Levels

- **🔴 Critical**: >100 lines OR >5 occurrences
- **🟠 High**: >50 lines OR >3 occurrences
- **🟡 Medium**: >20 lines
- **🟢 Low**: <20 lines

## Integration with Code Cleanup Suite

This is **Ion 2 of 5** in the Code Cleanup Suite:

```
Code Scanner Ion (1) → scan-results.json
                           ↓
Duplicate Detector Ion (2) → duplicates-report.json
Dead Code Eliminator Ion (3) → dead-code-report.json
Code Grouper Ion (4) → grouping-plan.json
                           ↓
Refactor Planner Ion (5) → refactor-roadmap.json
```

## License

MIT

## Author

LearnQwest™ - Build Systems That Build You
