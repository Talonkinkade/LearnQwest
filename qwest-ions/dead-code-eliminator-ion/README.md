# Dead Code Eliminator Ion

**BMAD Method Ion for detecting unused code and orphaned dependencies**

## Overview

Analyzes codebase to identify:
- Unused functions/classes via static analysis
- Unreferenced files (no imports)
- Orphaned dependencies
- Disk space to reclaim
- Generates safe-to-delete scripts

## Installation

```bash
cd qwest-ions/dead-code-eliminator-ion
bun install
```

## Usage

```bash
bun run src/index.ts \
  --input scan-results.json \
  --output dead-code-report.json \
  --generate-scripts
```

## Output

Generates `dead-code-report.json` with:
- Unused code entities (functions, classes, variables)
- Unused files
- Unused dependencies
- Deletion scripts (Bash + PowerShell)
- Safety recommendations

## Integration

**Ion 3 of 5** in Code Cleanup Suite

```
Code Scanner (1) → scan-results.json
                      ↓
Dead Code Eliminator (3) → dead-code-report.json
                      ↓
Refactor Planner (5) → refactor-roadmap.json
```

## License

MIT
