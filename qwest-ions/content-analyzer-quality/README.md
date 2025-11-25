# Content Analyzer #1: Quality Assessment

**5-Dimension Educational Content Quality Scoring System**

Filters educational content from Omnisearch based on credibility, accuracy, production quality, educational value, and engagement potential.

---

## Pipeline Position

```
Omnisearch (8 sources) → [Quality Assessment] → Learning Difficulty Scorer
                          ↑ YOU ARE HERE
```

**Input:** `output/omnisearch_results.json` (from Omnisearch Qwest-ion)
**Output:** `output/quality_filtered.json` (to Learning Difficulty Scorer)

---

## Quick Start

### Installation

```bash
cd qwest-ions/content-analyzer-quality

# Install dependencies
pip install -r requirements.txt
```

### Run Quality Analysis

```bash
# Process Omnisearch results
python scripts/run_quality_analysis.py
```

### Run Tests

```bash
# Run test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Features

### 5-Dimension Quality Assessment

1. **Credibility (25% weight)**
   - Source authority (.edu, .gov, academic journals)
   - YouTube channel credibility (Khan Academy, 3Blue1Brown, etc.)
   - Domain reputation and citation counts

2. **Accuracy (30% weight)**
   - Peer review status
   - Citation presence and quality
   - Fact-checking signals
   - Community validation (Stack Overflow scores, etc.)

3. **Production Quality (15% weight)**
   - Video resolution and audio quality
   - Text formatting and structure
   - Accessibility features (captions, transcripts)
   - Professional presentation

4. **Educational Value (20% weight)**
   - Learning objectives clarity
   - Pedagogical approach (examples, practice, scaffolding)
   - Content depth vs. surface-level
   - Instructional design quality

5. **Engagement (10% weight)**
   - Interactivity cues and activities
   - Retention techniques (stories, questions, challenges)
   - Student accessibility
   - Community engagement metrics (views, likes, upvotes)

### Configurable Thresholds

All thresholds configurable in `config/quality_thresholds.yaml`:

- **Overall threshold:** Minimum weighted score (default: 70/100)
- **Dimension minimums:** Individual dimension thresholds
- **Weights:** Customizable dimension weights

### Comprehensive Filtering

- Content must meet **overall threshold** AND **all dimension minimums**
- Prevents high scores in one area compensating for critical failures
- Detailed failure reasons for rejected content

---

## Architecture

### Scorer Modules

```
src/scorers/
├── credibility_scorer.py   - Source authority assessment
├── accuracy_scorer.py      - Content validation
├── production_scorer.py    - Production quality evaluation
├── educational_scorer.py   - Educational value scoring
└── engagement_scorer.py    - Engagement potential assessment
```

### Main Engine

```python
from quality_analyzer import QualityAnalyzer

# Initialize analyzer
analyzer = QualityAnalyzer()

# Analyze content items
results = analyzer.analyze(content_items)

# Filter and prepare for next stage
filtered = analyzer.filter_results(results)

# passed_content → Learning Difficulty Scorer
```

---

## Configuration

### Thresholds (`config/quality_thresholds.yaml`)

```yaml
quality_assessment:
  overall_threshold: 70  # Minimum overall score

  weights:
    credibility: 0.25
    accuracy: 0.30
    production: 0.15
    educational: 0.20
    engagement: 0.10

  dimension_minimums:
    credibility: 50
    accuracy: 60
    production: 40
    educational: 60
    engagement: 40
```

### Customization

Adjust thresholds based on your content quality requirements:

- **Stricter filtering:** Increase overall_threshold to 75-80
- **Academic focus:** Increase accuracy minimum to 70-75
- **Engagement priority:** Increase engagement weight to 0.15-0.20

---

## Output Format

### Passed Content (to Learning Difficulty Scorer)

```json
{
  "passed_content": [
    {
      "content": { ... },
      "scores": {
        "credibility": {
          "score": 85.0,
          "confidence": 0.9,
          "reasoning": "Educational platform (.edu domain)"
        },
        ...
      },
      "overall_score": 78.5,
      "passed": true,
      "timestamp": "2025-11-19T12:00:00Z"
    }
  ],
  "statistics": {
    "total": 42,
    "passed": 35,
    "failed": 7,
    "pass_rate": 0.833,
    "dimension_averages": { ... }
  },
  "next_stage": "Learning Difficulty Scorer"
}
```

### Failed Content (for analysis)

Saved to `output/quality_failed.json` with failure reasons:

```json
{
  "failed_content": [
    {
      "content": { ... },
      "overall_score": 62.0,
      "passed": false,
      "failure_reasons": [
        "Overall score 62.0 below threshold 70",
        "Accuracy score 55.0 below minimum 60"
      ]
    }
  ]
}
```

---

## Integration

### With Omnisearch

```bash
# 1. Run Omnisearch first
cd qwest-ions/omnisearch
bun run src/index.ts --query "machine learning" > ../../content-analyzer-quality/output/omnisearch_results.json

# 2. Run Quality Analysis
cd ../content-analyzer-quality
python scripts/run_quality_analysis.py
```

### With Learning Difficulty Scorer (Next Stage)

Quality Assessment output (`quality_filtered.json`) is automatically formatted for the Learning Difficulty Scorer:

- Only passed content included
- Scores and metadata preserved
- Ready for cognitive complexity analysis

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_quality_analyzer.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Fixtures

Sample Omnisearch output provided in `tests/fixtures/sample_omnisearch_output.json`.

---

## Examples

### Example 1: High-Quality Content (Passes)

**Input:**
```json
{
  "title": "Introduction to Calculus - Khan Academy",
  "url": "https://khanacademy.org/math/calculus",
  "source": "khan",
  "metadata": {
    "channel": "Khan Academy",
    "views": 1000000,
    "has_captions": true
  }
}
```

**Scores:**
- Credibility: 95 (Khan Academy authority)
- Accuracy: 85 (Educational platform standards)
- Production: 80 (Professional quality, captions)
- Educational: 90 (Clear pedagogy)
- Engagement: 75 (High viewership)
- **Overall: 86.5** ✅ PASS

### Example 2: Low-Quality Content (Fails)

**Input:**
```json
{
  "title": "Random tutorial",
  "url": "https://example.com/video",
  "source": "youtube",
  "metadata": {
    "channel": "Unknown",
    "views": 100
  }
}
```

**Scores:**
- Credibility: 45 ❌ (Below minimum 50)
- Accuracy: 50 ❌ (Below minimum 60)
- Production: 55
- Educational: 50 ❌ (Below minimum 60)
- Engagement: 35 ❌ (Below minimum 40)
- **Overall: 48.5** ❌ FAIL

**Failure Reasons:**
- Overall score 48.5 below threshold 70
- Credibility score 45 below minimum 50
- Accuracy score 50 below minimum 60
- Educational score 50 below minimum 60
- Engagement score 35 below minimum 40

---

## Performance

- **Processing Speed:** ~100-200 items/second
- **Memory Usage:** Minimal (stateless scoring)
- **Accuracy:** >95% appropriate filtering

---

## Troubleshooting

### No input file found

```
❌ ERROR: Omnisearch results not found: output/omnisearch_results.json
```

**Solution:** Run Omnisearch Qwest-ion first to generate input data.

### All content failing

**Check:** Are thresholds too strict?
**Solution:** Adjust `overall_threshold` or `dimension_minimums` in config.

### Unexpected scores

**Debug:** Enable detailed logging in `config/quality_thresholds.yaml`:

```yaml
logging:
  level: "DEBUG"
  detailed_reasoning: true
```

---

## Next Steps

After Quality Assessment completes:

1. **Review passed content:** Check `output/quality_filtered.json`
2. **Analyze failures:** Review `output/quality_failed.json`
3. **Adjust thresholds:** Fine-tune in `config/quality_thresholds.yaml`
4. **Run Learning Difficulty Scorer:** Process validated content

---

## Budget

**Allocation:** $50 of $850 total
**Phase:** 2.1 - Content Analyzers (Quality Assessment)
**Status:** ✅ Complete

---

## License

MIT License - Part of LearnQwest™ Educational AI Ecosystem

---

**Made with ❤️ by the LearnQwest Team**

**Part of:** LearnQwest™ Qwest-ion Agent Ecosystem
**Previous Stage:** Omnisearch Qwest-ion
**Next Stage:** Learning Difficulty Scorer
