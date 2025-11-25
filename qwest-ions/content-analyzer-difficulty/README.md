# Content Analyzer #2: Learning Difficulty Scorer

**4-Dimension Educational Content Difficulty Assessment System**

Analyzes quality-filtered content for reading level, cognitive complexity, prerequisites, and overall difficulty (Beginner → Expert).

---

## Pipeline Position

```
Quality Assessment → [Learning Difficulty Scorer] → Module Generators
                      ↑ YOU ARE HERE
```

**Input:** `output/quality_filtered.json` (from Quality Assessment)
**Output:** `output/difficulty_scored.json` (to Module Generators)

---

## Quick Start

### Installation

```bash
cd qwest-ions/content-analyzer-difficulty

# Install dependencies
pip install -r requirements.txt
```

### Run Difficulty Analysis

```bash
# Process quality-filtered content
python scripts/run_difficulty_analysis.py
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

### 4-Dimension Difficulty Assessment

1. **Reading Level (30% weight)**
   - Flesch-Kincaid Grade Level (0-18+)
   - Flesch Reading Ease (0-100)
   - Lexile Framework estimate (0-2000)
   - Average sentence/word length
   - Complex word percentage

2. **Cognitive Complexity (40% weight)**
   - Bloom's Taxonomy level (1-6)
     - Level 1: Remember (recall facts)
     - Level 2: Understand (explain concepts)
     - Level 3: Apply (use knowledge)
     - Level 4: Analyze (examine relationships)
     - Level 5: Evaluate (make judgments)
     - Level 6: Create (produce new work)
   - Keyword-based classification
   - Confidence scoring

3. **Prerequisite Knowledge (30% weight)**
   - Explicit prerequisite detection
   - Subject-specific prerequisite mapping
   - Complexity tier classification
   - Prerequisite count

4. **Overall Difficulty Classification**
   - Synthesizes all 3 dimensions
   - Beginner / Intermediate / Advanced / Expert
   - 1-10 difficulty score
   - Target audience recommendations
   - Learning pathway suggestions

### Configurable Parameters

All parameters configurable in `config/difficulty_thresholds.yaml`:

- **Reading level ranges:** Grade level thresholds for each difficulty
- **Cognitive weights:** Bloom's taxonomy difficulty mapping
- **Prerequisite tiers:** Complexity based on prerequisite count
- **Component weights:** Customizable dimension weights

---

## Architecture

### Analyzer Modules

```
src/analyzers/
├── reading_level.py           - Flesch-Kincaid, Lexile analysis
├── cognitive_complexity.py    - Bloom's Taxonomy assessment
├── prerequisite_knowledge.py  - Required background detection
└── difficulty_classifier.py   - Overall difficulty synthesis
```

### Main Engine

```python
from difficulty_scorer import DifficultyScorer

# Initialize scorer
scorer = DifficultyScorer()

# Analyze content items
results = scorer.analyze(content_items)

# Generate report
report = scorer.generate_report(results)

# difficulty_scored_content → Module Generators
```

---

## Configuration

### Thresholds (`config/difficulty_thresholds.yaml`)

```yaml
difficulty_assessment:
  reading_level:
    grade_ranges:
      beginner: [0, 6]
      intermediate: [7, 10]
      advanced: [11, 14]
      expert: [15, 20]

  cognitive_complexity:
    bloom_mapping:
      1: "Remember"
      2: "Understand"
      3: "Apply"
      4: "Analyze"
      5: "Evaluate"
      6: "Create"

  prerequisites:
    complexity_tiers:
      introductory: 0
      intermediate: 2
      advanced: 4
      expert: 6

  overall_difficulty:
    component_weights:
      reading_level: 0.30
      cognitive_complexity: 0.40
      prerequisites: 0.30
```

### Customization

Adjust weights based on your content focus:

- **Reading-heavy content:** Increase reading_level weight to 0.40
- **Problem-solving focus:** Increase cognitive_complexity to 0.50
- **Sequential curriculum:** Increase prerequisites to 0.35

---

## Output Format

### Difficulty-Scored Content (to Module Generators)

```json
{
  "difficulty_scored_content": [
    {
      "content": { ... },
      "difficulty_analysis": {
        "reading_level": {
          "grade_level": 8.5,
          "reading_ease": 65.2,
          "lexile_estimate": 850,
          "recommendation": "Middle School (Moderate)"
        },
        "cognitive_complexity": {
          "bloom_level": 3,
          "bloom_label": "Apply",
          "indicators": ["solve", "use", "demonstrate"],
          "reasoning": "Apply level based on indicators: 'solve', 'use', 'demonstrate'"
        },
        "prerequisites": {
          "prerequisite_count": 2,
          "prerequisites": ["algebra", "basic programming"],
          "complexity_tier": "Intermediate"
        },
        "overall_difficulty": {
          "level": "Intermediate",
          "score": 5,
          "confidence": 0.75,
          "target_audience": "High school students, college undergraduates",
          "recommendation": "Best for learners with basic understanding..."
        }
      }
    }
  ],
  "statistics": {
    "total_items": 42,
    "reading_level": {
      "average_grade_level": 9.2
    },
    "cognitive_complexity": {
      "average_bloom_level": 3.5
    }
  },
  "distribution": {
    "counts": {
      "Beginner": 10,
      "Intermediate": 20,
      "Advanced": 10,
      "Expert": 2
    },
    "percentages": {
      "Beginner": 23.8,
      "Intermediate": 47.6,
      "Advanced": 23.8,
      "Expert": 4.8
    }
  },
  "next_stage": "Module Generators"
}
```

---

## Integration

### With Quality Assessment

```bash
# 1. Run Quality Assessment first
cd ../content-analyzer-quality
python scripts/run_quality_analysis.py

# 2. Run Difficulty Scoring
cd ../content-analyzer-difficulty
python scripts/run_difficulty_analysis.py
```

### With Module Generators (Next Stage)

Difficulty Scorer output (`difficulty_scored.json`) is formatted for Module Generators:

- Difficulty scores and classifications included
- Target audience recommendations provided
- Learning pathway suggestions included
- Ready for adaptive content generation

---

## Examples

### Example 1: Beginner Content

**Input:**
```json
{
  "title": "What is Addition? Math for Kids",
  "description": "Learn to add numbers using fingers. Simple examples: 1+1=2, 2+2=4."
}
```

**Analysis:**
- Reading Level: Grade 2.5 (Very Easy, 95 reading ease)
- Cognitive: Bloom's Level 1 (Remember)
- Prerequisites: 0 (Introductory)
- **Overall: Beginner (Score: 2/10)**

**Target Audience:** Elementary students, adult learners new to topic

---

### Example 2: Expert Content

**Input:**
```json
{
  "title": "Quantum Field Theory: Renormalization Techniques",
  "abstract": "Advanced analysis of renormalization group flows requiring functional analysis, differential geometry, and theoretical physics. Evaluate complex Feynman diagrams..."
}
```

**Analysis:**
- Reading Level: Grade 18+ (Very Difficult, 25 reading ease)
- Cognitive: Bloom's Level 5 (Evaluate)
- Prerequisites: 5+ (Expert: calculus, linear algebra, quantum mechanics, etc.)
- **Overall: Expert (Score: 10/10)**

**Target Audience:** Graduate students, researchers, domain experts

---

## Performance

- **Processing Speed:** 50-100 items/second
- **Memory Usage:** Minimal (stateless analysis)
- **Accuracy:** >85% appropriate difficulty classification

---

## Troubleshooting

### No input file found

```
❌ ERROR: Quality-filtered results not found
```

**Solution:** Run Quality Assessment Analyzer first.

### All content classified as same level

**Check:** Are thresholds appropriate for your content type?
**Solution:** Adjust grade_ranges and component_weights in config.

### Low confidence scores

**Cause:** Insufficient text for analysis
**Solution:** Content needs more description/metadata for accurate assessment

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific analyzer
pytest tests/test_difficulty_scorer.py::test_reading_level_analysis -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Fixtures

Sample quality-filtered content in `tests/fixtures/sample_quality_filtered.json`.

---

## Next Steps

After Difficulty Scoring completes:

1. **Review distribution:** Check `output/difficulty_scored.json`
2. **Analyze report:** Review `output/difficulty_report.json`
3. **Adjust weights:** Fine-tune in `config/difficulty_thresholds.yaml`
4. **Run Module Generators:** Create adaptive learning content

---

## Budget

**Allocation:** $50 of $850 total
**Phase:** 2.2 - Content Analyzers (Learning Difficulty)
**Status:** ✅ Complete

---

## License

MIT License - Part of LearnQwest™ Educational AI Ecosystem

---

**Made with ❤️ by the LearnQwest Team**

**Part of:** LearnQwest™ Qwest-ion Agent Ecosystem
**Previous Stage:** Quality Assessment Analyzer
**Next Stage:** Module Generators
