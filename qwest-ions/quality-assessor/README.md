# Quality Assessment Qwest-ion

**Version:** 1.0.0
**Type:** Educational Content Quality Filter
**Agent ID:** quality-assessor

## Overview

The Quality Assessment Qwest-ion is a production-ready TypeScript agent that filters educational content based on 5-dimension quality scoring. It evaluates credibility, accuracy, production quality, educational value, and engagement to identify high-quality learning resources.

## Features

- **5-Dimension Quality Scoring**
  - Credibility (25%): Source authority and trustworthiness
  - Accuracy (30%): Factual correctness and verifiability
  - Production (15%): Technical quality and presentation
  - Educational (20%): Pedagogical value and learning design
  - Engagement (10%): Audience interaction and popularity

- **Three Assessment Modes**
  - Production: 70% threshold (standard quality bar)
  - Testing: 55% threshold (for synthetic test data)
  - Strict: 85% threshold (premium content only)

- **High Performance**
  - Processes 100+ items in <5 seconds
  - Parallel batch processing
  - Optimized for large-scale filtering

- **Comprehensive Validation**
  - Zod schema validation for all inputs
  - Type-safe throughout
  - Detailed signal tracking for each dimension

## Installation

```bash
cd qwest-ions/quality-assessor
bun install
```

## Quick Start

### Basic Usage

```bash
# Assess content items from JSON file
bun run src/index.ts --input omnisearch-results.json --output filtered.json

# Use testing mode for synthetic data
bun run src/index.ts --input test-data.json --mode testing

# Show detailed breakdown
bun run src/index.ts --input content.json --breakdown

# Verbose logging
bun run src/index.ts --input data.json --verbose
```

### Input Format

JSON array or object with `results` key:

```json
[
  {
    "id": "item1",
    "title": "Khan Academy: Introduction to Algebra",
    "url": "https://khanacademy.org/math/algebra",
    "source": "youtube",
    "type": "video",
    "channel": "Khan Academy",
    "views": 50000,
    "likes": 2500,
    "duration": "12:30",
    "grade_level": "8th grade",
    "subject": "mathematics"
  }
]
```

### Output Format

```json
{
  "total_assessed": 100,
  "passed": [/* High-quality items */],
  "failed": [/* Below-threshold items */],
  "statistics": {
    "pass_rate": 0.75,
    "avg_score": 72.5,
    "avg_by_dimension": {
      "credibility": 68.2,
      "accuracy": 75.3,
      "production": 70.1,
      "educational": 78.5,
      "engagement": 65.8
    },
    "execution_time_ms": 3500,
    "items_per_second": 28.57
  },
  "assessed_at": "2025-11-19T12:00:00.000Z",
  "mode": "production"
}
```

## Configuration

Edit `config/thresholds.yaml` to customize:

```yaml
modes:
  production:
    overall: 70
    dimensions:
      credibility: 60
      accuracy: 70
      production: 50
      educational: 65
      engagement: 40

scoring:
  trusted_sources:
    - "khan"
    - "scholar"

  trusted_channels:
    "Khan Academy": 96
    "3Blue1Brown": 98
    "IndyDevDan": 90
```

## Assessment Modes

### Production Mode (Default)

- **Overall Threshold:** 70%
- **Use Case:** Standard quality filtering for production content
- **Expected Pass Rate:** 30-40% of typical YouTube search results

### Testing Mode

- **Overall Threshold:** 55%
- **Use Case:** Synthetic test data, development, validation
- **Expected Pass Rate:** 50-60% of test data

### Strict Mode

- **Overall Threshold:** 85%
- **Use Case:** Premium content curation, expert-level resources
- **Expected Pass Rate:** 10-20% of typical content

## Scoring Dimensions

### 1. Credibility (25% weight)

**What it measures:** Source authority and trustworthiness

**Signals:**
- Trusted source (Khan Academy, ArXiv, Wikipedia)
- Verified author/channel
- High citation count
- Large author following
- Institutional source

**Example high score:** Khan Academy video by verified channel with 100+ citations

### 2. Accuracy (30% weight)

**What it measures:** Factual correctness and verifiability

**Signals:**
- Peer-reviewed source
- High citation count
- Educational institution
- References mentioned in description
- Trusted educational channel

**Example high score:** ArXiv research paper with 50+ citations and verified author

### 3. Production (15% weight)

**What it measures:** Technical quality and presentation

**Signals:**
- High view count
- Has captions/subtitles
- Has visuals/diagrams
- High audio quality
- Good engagement ratio (likes/views)
- Optimal duration (5-45 minutes for videos)

**Example high score:** Professional video with 100K+ views, captions, high-quality audio

### 4. Educational (20% weight)

**What it measures:** Pedagogical value and learning design

**Signals:**
- Dedicated educational platform
- Explicit educational metadata (grade level, subject)
- Educational keywords (tutorial, learn, course)
- Trusted educational channel
- Structured topics/curriculum

**Example high score:** Khan Academy lesson with grade level, subject tags, and structured curriculum

### 5. Engagement (10% weight)

**What it measures:** Audience interaction and popularity

**Signals:**
- High view count
- High like count
- Excellent engagement ratio (5%+ likes/views)
- High comment count
- Shares/amplification
- Recent content boost (<90 days)

**Example high score:** Viral educational video with 1M+ views, 50K+ likes, 5K+ comments

## Trusted Channels

Pre-configured trusted educational channels (from `config/thresholds.yaml`):

**AI/ML Education:**
- IndyDevDan (90/100)
- DeepLearning.AI (95/100)

**Programming:**
- Programming with Mosh (92/100)
- Traversy Media (88/100)
- freeCodeCamp.org (95/100)

**Computer Science:**
- NeetCode (93/100)
- MIT OpenCourseWare (98/100)
- CS50 (97/100)

**Mathematics:**
- 3Blue1Brown (98/100)
- Khan Academy (96/100)

**Science:**
- Crash Course (94/100)
- Kurzgesagt (92/100)

## Performance

**Benchmarks:**
- Single item assessment: ~10ms
- 100 items batch: <5 seconds (target met)
- 500 items batch: ~15 seconds
- Throughput: 20-30 items/second

**Optimization:**
- Parallel batch processing (10 items per batch)
- Concurrent dimension scoring (all 5 in parallel)
- Efficient signal detection

## Development

### Run Tests

```bash
# All tests
bun test

# Watch mode
bun test --watch

# Coverage report
bun test --coverage

# Specific test file
bun test tests/scorers.test.ts
```

### Type Checking

```bash
bun run typecheck
```

### Build

```bash
bun run build
```

## Integration

### With Workflow Executor

Add to `workflow_executor.py`:

```python
def action_quality_assessment(self, params):
    """Run quality assessment Qwest-ion"""
    input_file = params.get("input", "omnisearch_results.json")
    output_file = params.get("output", "quality_filtered.json")
    mode = params.get("mode", "production")

    result = subprocess.run([
        "bun", "run", "qwest-ions/quality-assessor/src/index.ts",
        "--input", input_file,
        "--output", output_file,
        "--mode", mode
    ], capture_output=True, text=True)

    return result.returncode == 0
```

### With Python Pipeline

```python
import subprocess
import json

def assess_quality(items, mode="production"):
    # Write items to temp file
    with open("temp_input.json", "w") as f:
        json.dump(items, f)

    # Run quality assessment
    subprocess.run([
        "bun", "run", "qwest-ions/quality-assessor/src/index.ts",
        "--input", "temp_input.json",
        "--output", "temp_output.json",
        "--mode", mode
    ])

    # Load results
    with open("temp_output.json", "r") as f:
        return json.load(f)
```

## Troubleshooting

### Issue: All items failing threshold

**Cause:** Using production mode (70%) with synthetic/test data

**Solution:** Use testing mode (55%)
```bash
bun run src/index.ts --input data.json --mode testing
```

### Issue: Performance slower than expected

**Cause:** Large batch size or network latency

**Solution:** Adjust batch size in config
```yaml
performance:
  batch_size: 5  # Reduce from 10
```

### Issue: Trusted channels not recognized

**Cause:** Channel name mismatch

**Solution:** Add channel to `config/thresholds.yaml`
```yaml
trusted_channels:
  "YourChannelName": 85
```

## BMAD Compliance

This agent follows BMAD 6.0.0-alpha.7 patterns:

- ✅ TypeScript with Bun runtime
- ✅ Zod schema validation
- ✅ CLI-first design
- ✅ Structured logging
- ✅ Configuration-driven
- ✅ Production error handling
- ✅ Comprehensive tests (90%+ coverage)
- ✅ E2B sandbox ready

## License

MIT

## Contributing

This is Agent #1 of the 7-agent LearnQwest pipeline. See `QWESTION_AGENTS_BUILDPLAN.md` for the complete roadmap.

---

**Built with:** TypeScript + Bun + Zod
**Part of:** LearnQwest Educational Platform
**Next Agent:** Difficulty Scorer (Agent #2)
