# Code Grouper Ion

**BMAD Ion for analyzing code organization and suggesting improvements**

## Features

- Functional grouping (files that work together)
- Layered grouping (ui/services/models)
- Misplaced file detection
- Git-aware migration scripts
- Rollback script generation

## Usage

```bash
bun run src/index.ts -i scan-results.json -o grouping-plan.json
```

## Output

- File groups by functionality and layer
- Misplaced file recommendations
- Migration scripts (Bash + PowerShell)
- Proposed directory structure

**Ion 4 of 5** in Code Cleanup Suite

MIT License
