# Agent Definition: Refactor Planner Ion

**Name**: Refactor Planner Ion
**Type**: Orchestrator Agent
**Version**: 1.0.0
**Method**: BMAD
**Role**: Master Refactor Coordinator

## Purpose

Final orchestrator that aggregates all Code Cleanup Ion outputs, calculates ROI priorities, and generates a phased refactor roadmap with interactive HTML dashboard.

## Capabilities

### Aggregation
- Combines duplicate detection results
- Integrates dead code analysis
- Merges grouping recommendations

### Prioritization
- Impact/effort ROI calculation
- Risk assessment
- Dependency analysis
- Priority ranking (critical/high/medium/low)

### Planning
- 3-phase roadmap generation
- Timeline estimation
- Effort calculation
- Space savings aggregation

### Visualization
- HTML dashboard generation
- Interactive metrics display
- Phase breakdown
- Progress tracking UI

## Input

**Multiple Sources**:
- `scan-results.json` (Ion 1)
- `duplicates-report.json` (Ion 2)
- `dead-code-report.json` (Ion 3)
- `grouping-plan.json` (Ion 4)

## Output

- `refactor-roadmap.json` - Prioritized action plan
- `refactor-dashboard.html` - Interactive visualization

## Phases

### Phase 1: Quick Wins
- Max effort: 4 hours
- Min ROI: 2.0
- High impact, low effort

### Phase 2: Medium Refactors
- Max effort: 16 hours
- Min ROI: 1.5
- Balanced approach

### Phase 3: Large Refactors
- Max effort: 40 hours
- Min ROI: 1.0
- Strategic improvements

## ROI Formula

```
ROI = Impact Score / Effort Hours

Impact = weighted sum of:
- Space savings (40%)
- Code quality improvement (30%)
- Risk reduction (20%)
- Dependency simplification (10%)
```

## Dashboard

**Metrics Displayed**:
- Total actions
- Duplicate count
- Unused code count
- Disk savings (KB)
- Estimated time (hours + weeks)

**Features**:
- Dark theme
- Responsive design
- Priority color coding
- Phase organization
- ROI indicators

## Algorithm

```
1. Load all Ion outputs
2. Extract refactor actions from each
3. Calculate impact scores
4. Calculate effort estimates
5. Compute ROI for each action
6. Sort by priority + ROI
7. Assign to phases based on effort and ROI
8. Generate timeline
9. Create dashboard HTML
10. Output roadmap JSON
```

## Status

**Production Ready** ✅

- [x] Multi-source aggregation
- [x] ROI prioritization
- [x] Phase assignment
- [x] Timeline calculation
- [x] Dashboard generation
- [x] Validation
- [x] Documentation

---

**Part of**: LearnQwest Code Cleanup Suite (Ion 5 of 5 - ORCHESTRATOR)
**Maintained by**: LearnQwest™
**Last updated**: 2025-11-19
