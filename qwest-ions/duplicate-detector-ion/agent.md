# Agent Definition: Duplicate Detector Ion

## Identity

**Name**: Duplicate Detector Ion
**Type**: Code Analysis Agent
**Version**: 1.0.0
**Method**: BMAD (Build-Measure-Analyze-Decide)
**Role**: Duplicate Code Detection and Refactoring Recommendation

## Purpose

Analyzes codebase scan results to identify exact and similar code duplicates, providing actionable refactoring recommendations with calculated priorities and space savings potential.

## Capabilities

### Core Functions

1. **Exact Duplicate Detection**
   - 100% identical code matching
   - Content-based hashing
   - Multi-file comparison
   - Space savings calculation

2. **Similar Duplicate Detection**
   - 55-95% similarity matching
   - Fuzzy hashing algorithms
   - Line-based comparison
   - Pattern recognition

3. **Pattern Analysis**
   - Function signature patterns
   - Import pattern detection
   - Class structure patterns
   - Repeated code structures

4. **File Path Pattern Analysis**
   - Directory structure grouping
   - Organizational pattern detection
   - Misplaced file identification

5. **Priority Calculation**
   - Critical/High/Medium/Low ranking
   - Lines count evaluation
   - Occurrence frequency analysis
   - Refactoring effort estimation

### Technical Specifications

- **Input**: `scan-results.json` from Code Scanner Ion
- **Output**: `duplicates-report.json` with duplicate groups and recommendations
- **Language**: TypeScript
- **Runtime**: Bun
- **Validation**: Zod schemas
- **CLI**: Commander.js

## Configuration

### Similarity Thresholds
- Exact match: 100%
- Similar match range: 55-95%
- Configurable via `config.yaml`

### Detection Rules
- Minimum lines: 5 (configurable)
- Supported extensions: .ts, .tsx, .js, .jsx, .py, .md, .yaml, .json
- Ignore patterns: node_modules, dist, build, .git

### Priority Rules
- **Critical**: >100 lines OR >5 occurrences
- **High**: >50 lines OR >3 occurrences
- **Medium**: >20 lines
- **Low**: <20 lines

## Input Schema

```typescript
{
  workflow_version: string
  project_root: string
  findings: {
    files: Array<{
      path: string
      size: number
      lines: number
      extension: string
      hash?: string
    }>
  }
}
```

## Output Schema

```typescript
{
  generated_at: string (ISO 8601)
  project_root: string
  scan_summary: {
    files_analyzed: number
    total_lines: number
    duplicates_found: number
    exact_duplicates: number
    similar_duplicates: number
    total_space_savings: number
  }
  duplicate_groups: Array<DuplicateGroup>
  pattern_groups: Array<PatternGroup>
  file_path_patterns: Array<PathPattern>
  recommendations: Array<Recommendation>
}
```

## Algorithm

### 1. File Content Loading
```
FOR each file in scan results
  IF file matches extension criteria
    AND file not in ignore patterns
    THEN load content and calculate hash
```

### 2. Exact Duplicate Detection
```
GROUP files by content hash
FOR each hash group with >1 file
  IF lines >= minimum_lines
    THEN create exact duplicate group
```

### 3. Similar Duplicate Detection
```
FOR each file pair
  CALCULATE similarity score (0-100)
  IF similarity between 55-95%
    THEN add to similar duplicate group
```

### 4. Pattern Extraction
```
FOR each file
  EXTRACT function signatures
  EXTRACT import patterns
  EXTRACT class definitions
  GROUP by pattern type
```

### 5. Priority Calculation
```
FOR each duplicate group
  IF lines >= critical_threshold OR occurrences >= critical_count
    THEN priority = CRITICAL
  ELSE IF lines >= high_threshold OR occurrences >= high_count
    THEN priority = HIGH
  ELSE IF lines >= medium_threshold
    THEN priority = MEDIUM
  ELSE priority = LOW
```

## Error Handling

- **Invalid input**: Zod validation with descriptive errors
- **Missing files**: Logged warnings, continues processing
- **File read errors**: Skipped with warning
- **Memory limits**: Batched processing for large codebases

## Performance

- **Target**: <5 seconds for 500 files
- **Memory**: O(n²) for similarity detection (optimized with caching)
- **Disk I/O**: Sequential file reading
- **Caching**: Similarity results cached per session

## Integration

### Inputs From
- **Code Scanner Ion** (Ion 1): scan-results.json

### Outputs To
- **Refactor Planner Ion** (Ion 5): duplicates-report.json
- **Developers**: Direct review of duplicate groups

### Parallel Execution
Can run in parallel with:
- Dead Code Eliminator Ion (Ion 3)
- Code Grouper Ion (Ion 4)

## Usage Examples

### Basic Usage
```bash
bun run src/index.ts \
  --input scan-results.json \
  --output duplicates-report.json
```

### Custom Configuration
```bash
bun run src/index.ts \
  --input scan-results.json \
  --config custom-config.yaml \
  --verbose
```

### Programmatic Usage
```typescript
import { DuplicateDetector } from './detector';
import { ConfigSchema, ScanResultSchema } from './types';

const config = ConfigSchema.parse(configData);
const scanResult = ScanResultSchema.parse(scanData);

const detector = new DuplicateDetector(config, scanResult.project_root);
const results = await detector.analyze(scanResult);
```

## Limitations

- Line-based similarity (not AST-based)
- Limited to configured file extensions
- No cross-language duplicate detection
- Memory usage scales with file count

## Future Enhancements

- [ ] AST-based similarity for better accuracy
- [ ] Cross-language duplicate detection
- [ ] Visual diff generation
- [ ] Automatic refactoring script generation
- [ ] Integration with git history for duplicate timeline

## Validation

All inputs and outputs validated with Zod schemas:
- Type safety at runtime
- Descriptive error messages
- Production-ready validation

## Testing

- Unit tests for core algorithms
- Integration tests with sample codebases
- Edge case coverage (empty files, large files, etc.)
- Performance benchmarks

## BMAD Compliance

- ✅ **Build**: CLI-first, production-ready
- ✅ **Measure**: Quantifies duplicates, space savings, occurrences
- ✅ **Analyze**: Pattern detection, similarity analysis
- ✅ **Decide**: Priority ranking, actionable recommendations

## Status

**Production Ready** ✅

- [x] Core duplicate detection
- [x] Similarity algorithm
- [x] Pattern analysis
- [x] Priority calculation
- [x] CLI interface
- [x] Zod validation
- [x] Error handling
- [x] Documentation
- [x] Tests
- [x] README

---

**Part of**: LearnQwest Code Cleanup Suite (Ion 2 of 5)
**Maintained by**: LearnQwest™
**Last updated**: 2025-11-19
