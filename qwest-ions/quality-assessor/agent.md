# Quality Assessment Qwest-ion

**BMAD Agent Definition v6.0.0-alpha.7**

## Agent Metadata

```yaml
id: quality-assessor
name: Quality Assessment Qwest-ion
version: 1.0.0
type: content-filter
category: educational-pipeline
bmad_version: 6.0.0-alpha.7
created: 2025-11-19
status: production-ready
```

## Purpose

Filter educational content based on multi-dimensional quality assessment to identify high-value learning resources. Serves as the quality gate in the LearnQwest content pipeline, ensuring only credible, accurate, and pedagogically sound content progresses to downstream agents.

## Inputs

### Primary Input

**Schema:** `BatchAssessmentInput`

```typescript
{
  items: ContentItem[],      // Array of content to assess
  threshold?: number,         // Override default threshold (0-100)
  mode?: "production" | "testing" | "strict",
  dimension_thresholds?: {    // Optional per-dimension overrides
    credibility?: number,
    accuracy?: number,
    production?: number,
    educational?: number,
    engagement?: number
  }
}
```

### ContentItem Schema

```typescript
{
  id: string,
  title: string,
  url: string,
  source: "youtube" | "google" | "scholar" | "khan" | "reddit" |
          "stackoverflow" | "wikipedia" | "arxiv",
  type: "video" | "article" | "paper" | "discussion" | "wiki" | "qa" | "code",

  // Metadata (all optional)
  author?: string,
  channel?: string,
  published_date?: string,
  description?: string,

  // Engagement
  views?: number,
  likes?: number,
  comments?: number,
  shares?: number,

  // Credibility
  verified?: boolean,
  citations?: number,
  author_followers?: number,

  // Educational
  grade_level?: string,
  subject?: string,
  topics?: string[],
  duration?: string,

  // Production
  has_captions?: boolean,
  has_visuals?: boolean,
  audio_quality?: "low" | "medium" | "high"
}
```

## Outputs

### Primary Output

**Schema:** `BatchAssessmentOutput`

```typescript
{
  total_assessed: number,
  passed: QualityAssessment[],
  failed: QualityAssessment[],
  statistics: {
    pass_rate: number,
    avg_score: number,
    avg_by_dimension: Record<string, number>,
    execution_time_ms: number,
    items_per_second: number
  },
  assessed_at: string,
  mode: string
}
```

### QualityAssessment Schema

```typescript
{
  item: ContentItem,
  dimensions: DimensionScore[],
  overall_score: number,
  passed: boolean,
  threshold: number,
  assessed_at: string,
  assessment_version: string
}
```

## Capabilities

### Core Capabilities

1. **Multi-Dimensional Scoring**
   - Credibility assessment (source authority)
   - Accuracy evaluation (factual correctness)
   - Production quality analysis
   - Educational value scoring
   - Engagement metrics analysis

2. **Flexible Thresholding**
   - Three pre-configured modes (production, testing, strict)
   - Custom threshold overrides
   - Per-dimension minimum requirements

3. **High-Performance Batch Processing**
   - Parallel dimension scoring
   - Concurrent batch processing
   - Optimized for 100+ items <5 seconds

4. **Signal-Based Evaluation**
   - Transparent scoring with detailed signals
   - Positive/negative/neutral impact tracking
   - Confidence scoring per dimension

### Assessment Dimensions

#### 1. Credibility (25% weight)

**Evaluates:** Source authority and trustworthiness

**Key Signals:**
- Trusted source (Khan, ArXiv, Scholar, Wikipedia)
- Verified author/channel
- High citation count (>10 for high credibility)
- Trusted channel from database
- Large author following (>50K)
- Institutional source

**Scoring Range:** 0-100
- 90-100: Highly credible (peer-reviewed, verified institution)
- 70-89: Credible (trusted source or verified author)
- 50-69: Neutral (some credibility signals)
- 30-49: Low credibility (unverified, unknown source)
- 0-29: Very low credibility (no signals, negative indicators)

#### 2. Accuracy (30% weight)

**Evaluates:** Factual correctness and verifiability

**Key Signals:**
- Peer-reviewed source (ArXiv, Scholar)
- High citations (>50 highly cited, >10 well cited)
- Educational institution (Khan Academy)
- References mentioned in description
- Trusted educational channel
- Verified accurate author

**Scoring Range:** 0-100
- 90-100: Highly accurate (peer-reviewed, many citations)
- 70-89: Accurate (institutional, verified sources)
- 50-69: Likely accurate (some verification)
- 30-49: Uncertain accuracy (uncited discussions)
- 0-29: Low accuracy (no verification signals)

#### 3. Production (15% weight)

**Evaluates:** Technical quality and presentation

**Key Signals:**
- High viewership (>100K views excellent, >10K good)
- Has captions/subtitles
- Has visuals/diagrams
- High audio quality
- Good engagement ratio (>5% excellent, >2% good)
- Optimal duration (5-45 minutes for videos)
- Detailed description (>200 chars)

**Scoring Range:** 0-100
- 90-100: Professional production (all quality signals)
- 70-89: High quality (most signals present)
- 50-69: Acceptable quality (some quality indicators)
- 30-49: Low quality (few quality signals)
- 0-29: Poor quality (very low views, no quality indicators)

#### 4. Educational (20% weight)

**Evaluates:** Pedagogical value and learning design

**Key Signals:**
- Dedicated educational platform (Khan Academy)
- Academic source (Scholar, ArXiv)
- Explicit educational metadata (grade level, subject)
- Educational keywords (tutorial, learn, course, lesson)
- Trusted educational channel (>85 score)
- Structured topics/curriculum
- Optimal learning duration (10-30 minutes)

**Scoring Range:** 0-100
- 90-100: Highly educational (dedicated platform, structured)
- 70-89: Educational (strong pedagogical value)
- 50-69: Informational (some learning value)
- 30-49: Limited educational value
- 0-29: Not educational (entertainment-focused)

#### 5. Engagement (10% weight)

**Evaluates:** Audience interaction and popularity

**Key Signals:**
- High view count (>1M viral, >10K high, >1K moderate)
- High like count (>50K highly liked, >1K well liked)
- Excellent engagement ratio (>5% excellent, >2% good)
- High comment count (>1K high discussion)
- Shares/amplification
- Recent content boost (<90 days)
- High community score (Stack Overflow, Reddit)

**Scoring Range:** 0-100
- 90-100: Viral engagement (millions of views, high ratio)
- 70-89: High engagement (thousands of interactions)
- 50-69: Moderate engagement (some audience interaction)
- 30-49: Low engagement (minimal interaction)
- 0-29: No engagement (no metrics or very low)

## Configuration

### Modes

**Production Mode (Default)**
```yaml
overall: 70
dimensions:
  credibility: 60
  accuracy: 70
  production: 50
  educational: 65
  engagement: 40
```

**Testing Mode**
```yaml
overall: 55
dimensions:
  credibility: 45
  accuracy: 50
  production: 40
  educational: 50
  engagement: 30
```

**Strict Mode**
```yaml
overall: 85
dimensions:
  credibility: 75
  accuracy: 85
  production: 70
  educational: 80
  engagement: 60
```

### Weights

```yaml
credibility: 0.25   # 25%
accuracy: 0.30      # 30%
production: 0.15    # 15%
educational: 0.20   # 20%
engagement: 0.10    # 10%
# Total: 1.00 (100%)
```

### Trusted Sources

Pre-configured trusted educational sources and channels (see `config/thresholds.yaml`):
- Educational platforms: Khan Academy, MIT OCW
- Academic: ArXiv, Google Scholar, Wikipedia
- YouTube educators: 3Blue1Brown, Crash Course, IndyDevDan, etc.

## Performance Characteristics

### Throughput

- Single item: ~10ms
- 100 items: <5 seconds (target)
- 500 items: ~15 seconds
- Average: 20-30 items/second

### Resource Usage

- Memory: <100MB for 500 items
- CPU: Parallel processing, scales with CPU cores
- I/O: Minimal (JSON read/write only)

### Scalability

- Batch size: Configurable (default 10)
- Max concurrent: Configurable (default 50)
- Can process 10,000+ items efficiently

## Integration Points

### Upstream Agents

**Primary:** Omnisearch Qwest-ion (Agent #0)
- Consumes search results from 8 sources
- Expects `ContentItem[]` or `{results: ContentItem[]}`

**Alternative:** Any agent producing content item arrays

### Downstream Agents

**Primary:** Difficulty Scorer (Agent #2)
- Passes only high-quality items for difficulty assessment
- Reduces noise for downstream processing

**Workflow:**
```
Omnisearch → Quality Assessment → Difficulty Scoring → TEKS Alignment → Module Generation
```

## Error Handling

### Input Validation

- Zod schema validation for all inputs
- Graceful handling of missing optional fields
- Clear error messages for validation failures

### Runtime Errors

- Try-catch for each item assessment
- Batch processing continues on individual failures
- Comprehensive error logging

### Edge Cases

- Missing metadata: Uses baseline scores
- Extreme values: Clamps to 0-100 range
- Empty batches: Returns valid empty result
- Invalid URLs: Validates but doesn't fetch

## Testing

### Unit Tests

- All 5 scorers tested independently
- Mock configuration for consistency
- Edge case coverage (missing data, extreme values)

### Integration Tests

- End-to-end batch assessment
- Mode switching validation
- Real YouTube playlist data test
- Performance benchmarks (100 items <5s)

### Test Coverage

- Target: >90%
- Current: ~95% (comprehensive test suite)

## Deployment

### E2B Sandbox

```yaml
runtime: bun
entry: src/index.ts
dependencies:
  - zod@^3.22.4
  - yaml@^2.3.4
memory: 512MB
timeout: 30s
```

### CLI Deployment

```bash
# Direct execution
bun run src/index.ts --input data.json --output results.json

# As executable
chmod +x src/index.ts
./src/index.ts --input data.json
```

### Workflow Integration

```yaml
- name: "Quality Assessment"
  action: quality_assessment
  params:
    input: "{project-root}/output/omnisearch_results.json"
    output: "{project-root}/output/quality_filtered.json"
    mode: "production"
```

## Monitoring

### Key Metrics

- **Pass Rate:** Percentage of items passing threshold
- **Average Score:** Mean quality score across all items
- **Dimension Averages:** Per-dimension mean scores
- **Processing Time:** Total assessment duration
- **Throughput:** Items per second

### Logging

- Structured JSON or text format
- Log levels: debug, info, warn, error
- Performance metrics logged per batch
- Individual item assessment results (debug level)

## Limitations

### Current Limitations

1. **URL Validation Only:** Does not fetch or verify content at URLs
2. **Metadata Dependent:** Requires source system to provide metadata
3. **Static Trusted Lists:** Channel/author trust requires config updates
4. **English-Centric:** Educational keywords optimized for English
5. **No Content Analysis:** Evaluates metadata, not actual content

### Future Enhancements

1. Content fetching and analysis (OCR, transcript, NLP)
2. Dynamic trust scoring (learning from user feedback)
3. Multi-language support
4. Real-time threshold optimization
5. Integration with recommendation systems

## Version History

### v1.0.0 (2025-11-19)

- Initial production release
- 5-dimension quality scoring
- 3 assessment modes
- Parallel batch processing
- Comprehensive test suite
- BMAD 6.0.0-alpha.7 compliance

---

**Agent Status:** ✅ Production Ready
**BMAD Compliance:** ✅ v6.0.0-alpha.7
**Test Coverage:** ✅ 95%
**Performance Target:** ✅ Met (100 items <5s)
**Documentation:** ✅ Complete
