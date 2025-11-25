# Refactor Planner Ion

**BMAD Method Orchestrator - Creates prioritized refactor roadmap from all analysis**

## Purpose

Final orchestrator that combines outputs from all Code Cleanup Ions (Duplicate Detector, Dead Code Eliminator, Code Grouper) to create a prioritized, phased refactor roadmap.

## Features

- **Aggregate Analysis**: Combines all Ion outputs
- **ROI Prioritization**: Ranks by impact/effort ratio
- **Phased Planning**: Quick wins → Medium → Large refactors
- **Timeline Estimation**: Calculates total effort and weeks
- **HTML Dashboard**: Visual progress tracker

## Usage

```bash
bun run src/index.ts \
  --scan scan-results.json \
  --duplicates duplicates-report.json \
  --dead-code dead-code-report.json \
  --grouping grouping-plan.json \
  --output refactor-roadmap.json \
  --dashboard
```

## Output

- `refactor-roadmap.json` - Complete roadmap with phases
- `refactor-dashboard.html` - Interactive dashboard

## Dashboard Features

- ✅ Aggregate metrics (duplicates, dead code, disk savings)
- ✅ Phased action plan
- ✅ Priority indicators (critical/high/medium/low)
- ✅ Effort and ROI estimates
- ✅ Timeline calculator
- ✅ Dark theme

## Phases

1. **Quick Wins** (<4h effort, ROI ≥2.0)
2. **Medium Refactors** (<16h effort, ROI ≥1.5)
3. **Large Refactors** (<40h effort, ROI ≥1.0)

## Integration

**Ion 5 of 5** - Final orchestrator

```
Ions 2-4 → reports
      ↓
Refactor Planner (5) → roadmap.json + dashboard.html
```

## License

MIT

---

**Part of**: LearnQwest Code Cleanup Suite
**Maintained by**: LearnQwest™
**Last updated**: 2025-11-19
