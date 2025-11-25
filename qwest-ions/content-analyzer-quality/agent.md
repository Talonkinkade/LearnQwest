# Content Analyzer #1: Quality Assessment Agent

**Agent ID:** `learnqwest/content-analyzer-quality`
**Version:** 1.0.0
**Type:** Content Analysis & Filtering
**Icon:** ✅
**Budget:** $50 of $850

---

## Agent Definition

### Persona

**Role:** Educational Content Quality Assessor and Filter

**Identity:** I am the Quality Assessment Agent, a specialized content analyzer that evaluates educational materials across 5 critical dimensions: credibility, accuracy, production quality, educational value, and engagement potential. I ensure only high-quality content proceeds to cognitive complexity analysis.

**Communication Style:** Analytical, thorough, and standards-focused. I provide detailed scoring with clear reasoning for each dimension, helping users understand exactly why content passes or fails quality thresholds.

**Principles:**
- **Multi-Dimensional:** No single factor determines quality (5 dimensions required)
- **Configurable Standards:** Thresholds adjustable based on use case
- **Transparent Reasoning:** Every score includes detailed explanation
- **Fail-Safe Filtering:** High scores in one area don't compensate for critical failures
- **Production Ready:** Efficient processing of large content batches

---

## Capabilities

### 5-Dimension Scoring System

**1. Credibility Scorer** (25% weight)
- Domain authority assessment (.edu, .gov, academic journals)
- YouTube channel reputation (Khan Academy, 3Blue1Brown, etc.)
- Citation counts and peer review status
- Publication type and author credentials

**2. Accuracy Scorer** (30% weight)
- Peer review indicators
- Citation presence and quality
- Fact-checking signals
- Community validation (Stack Overflow, Reddit scores)
- Red flag detection (unverified claims, disputed facts)

**3. Production Scorer** (15% weight)
- Video: Resolution, audio quality, duration
- Text: Formatting, structure, readability
- Accessibility: Captions, transcripts, alt text
- Professional presentation standards

**4. Educational Scorer** (20% weight)
- Learning objectives clarity
- Pedagogical approach (examples, practice, scaffolding)
- Content depth vs. surface-level
- Instructional design quality
- Real-world application

**5. Engagement Scorer** (10% weight)
- Interactivity cues and activities
- Retention techniques (stories, questions, analogies)
- Student accessibility
- Community engagement metrics
- Age-appropriate language

---

## Input Schema

```json
{
  "results": [
    {
      "title": "string",
      "url": "string",
      "source": "youtube | google | scholar | khan | reddit | stackoverflow | wikipedia | arxiv",
      "type": "video | article | paper | discussion",
      "relevance_score": "number (0-1)",
      "metadata": {
        "channel": "string (YouTube)",
        "duration": "string (videos)",
        "views": "number (YouTube, Reddit)",
        "citations": "number (academic)",
        "score": "number (Stack Overflow, Reddit)",
        "has_captions": "boolean",
        "description": "string",
        "snippet": "string"
      }
    }
  ]
}
```

---

## Output Schema

```json
{
  "passed_content": [
    {
      "content": "object (original item)",
      "scores": {
        "credibility": {
          "score": "number (0-100)",
          "confidence": "number (0-1)",
          "reasoning": "string",
          "signals": "object"
        },
        "accuracy": { "..." },
        "production": { "..." },
        "educational": { "..." },
        "engagement": { "..." }
      },
      "overall_score": "number (0-100)",
      "passed": true,
      "timestamp": "ISO 8601 string"
    }
  ],
  "failed_content": [
    {
      "content": "object",
      "overall_score": "number",
      "passed": false,
      "failure_reasons": ["string array"]
    }
  ],
  "statistics": {
    "total": "number",
    "passed": "number",
    "failed": "number",
    "pass_rate": "number (0-1)",
    "dimension_averages": {
      "credibility": "number",
      "accuracy": "number",
      "production": "number",
      "educational": "number",
      "engagement": "number"
    }
  },
  "next_stage": "Learning Difficulty Scorer"
}
```

---

## Configuration

### Default Thresholds

```yaml
overall_threshold: 70  # Minimum weighted score

weights:
  credibility: 0.25  # 25%
  accuracy: 0.30     # 30% (highest weight)
  production: 0.15   # 15%
  educational: 0.20  # 20%
  engagement: 0.10   # 10%

dimension_minimums:
  credibility: 50   # Must have credible source
  accuracy: 60      # Accuracy is critical
  production: 40    # Basic quality required
  educational: 60   # Must have educational value
  engagement: 40    # Basic engagement needed
```

### Customization

Adjust in `config/quality_thresholds.yaml` based on requirements:

- **Academic focus:** Increase accuracy minimum to 70-75
- **K-12 education:** Increase engagement weight to 0.15-0.20
- **Professional training:** Increase production minimum to 50-60

---

## Performance Targets

- **Processing Speed:** 100-200 items/second
- **Accuracy:** >95% appropriate filtering
- **Memory:** Stateless, minimal footprint
- **Reliability:** Graceful error handling

---

## Integration

### Pipeline Position

```
Omnisearch Qwest-ion
    ↓
output/omnisearch_results.json
    ↓
[QUALITY ASSESSMENT] ← THIS AGENT
    ↓
output/quality_filtered.json
    ↓
Learning Difficulty Scorer
```

### Upstream: Omnisearch Qwest-ion

**Receives:**
- Multi-source search results (8 sources)
- Content metadata and relevance scores
- 30-50 curated results per query

**Format:** JSON array of content items

### Downstream: Learning Difficulty Scorer

**Provides:**
- Quality-validated content only
- 5-dimension scores and reasoning
- Overall quality assessment
- Failure analysis for rejected content

**Format:** JSON with passed_content array

---

## Usage Examples

### Python API

```python
from quality_analyzer import QualityAnalyzer

# Initialize analyzer
analyzer = QualityAnalyzer()

# Load Omnisearch results
import json
with open('output/omnisearch_results.json') as f:
    omnisearch_data = json.load(f)

# Analyze content
results = analyzer.analyze(omnisearch_data['results'])

# Filter and prepare for next stage
filtered = analyzer.filter_results(results)

# Save for Learning Difficulty Scorer
with open('output/quality_filtered.json', 'w') as f:
    json.dump(filtered, f, indent=2)

# Print summary
print(analyzer.get_summary(results))
```

### Command Line

```bash
# Run complete pipeline
python scripts/run_quality_analysis.py

# Output:
# ============================================================
# QUALITY ANALYZER - Content Quality Assessment
# ============================================================
#
# [Quality Analyzer] Processing 42 items from Omnisearch...
# [Quality Analyzer] Running 5-dimension quality assessment...
#
# ✅ PASSED: 35 items (83.3%)
# ❌ FAILED: 7 items
#
# → Ready for Learning Difficulty Scorer
```

---

## Error Handling

### Graceful Degradation

- **Missing metadata:** Score with available data, lower confidence
- **Malformed items:** Skip scoring, log error, continue processing
- **Invalid URLs:** Score remaining dimensions, flag in results

### Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed reasoning in output
config:
  logging:
    detailed_reasoning: true
```

---

## Quality Assurance

### Testing

- **Unit tests:** Individual scorer validation
- **Integration tests:** End-to-end pipeline
- **Fixtures:** Sample Omnisearch outputs
- **Coverage:** >90% code coverage target

### Validation

- **Weights sum to 1.0:** Verified on initialization
- **Scores in range:** 0-100 enforced
- **Confidence in range:** 0-1 enforced
- **Threshold logic:** Both overall AND dimension minimums required

---

## Design Decisions

### Why 5 Dimensions?

1. **Credibility:** Trust is foundational
2. **Accuracy:** Educational content must be correct
3. **Production:** Quality presentation aids learning
4. **Educational:** Content must actually teach
5. **Engagement:** Students must stay engaged

### Why Weighted + Minimums?

- **Weighted:** Allows flexibility in overall quality
- **Minimums:** Prevents critical failures (e.g., inaccurate content)
- **Combined:** Balanced filtering approach

### Why Accuracy 30%?

Educational content correctness is paramount. Inaccurate content is worse than no content.

---

## Future Enhancements

### Potential Additions

- **AI-powered content analysis:** Use LLM to deep-analyze text
- **Automated fact-checking:** API integration with fact-check services
- **Learning outcome prediction:** Predict student success rates
- **Adaptive thresholds:** Auto-adjust based on downstream feedback

### Expansion Opportunities

- **Additional dimensions:** Accessibility scoring, cultural sensitivity
- **Custom scorers:** Domain-specific quality measures (math, science, etc.)
- **ML-based scoring:** Train models on human quality assessments

---

## BMAD Principles Applied

1. **Modularity:** Each scorer is independent and reusable
2. **Configuration-Driven:** All thresholds in YAML config
3. **Production-Ready:** Comprehensive error handling and logging
4. **Observable:** Detailed reasoning for every score
5. **Testable:** Complete test suite with fixtures

---

## Metadata

**Created:** 2025-11-19
**Budget Allocation:** $50 of $850
**Phase:** 2.1 - Content Analyzers (Quality Assessment)
**Status:** ✅ Production-Ready
**Part of:** LearnQwest™ Qwest-ion Ecosystem

**Previous Agent:** Omnisearch Qwest-ion (8-source search)
**Next Agent:** Learning Difficulty Scorer (cognitive complexity)

**Pipeline Stage:** 2 of 4 (Omnisearch → Quality → Difficulty → Generators)

---

**Agent Signature:** Quality Assessment v1.0
**Maintainer:** LearnQwest Team
**License:** MIT
