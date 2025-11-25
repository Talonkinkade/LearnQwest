# Content Analyzer #2: Learning Difficulty Scorer

**Agent ID:** `learnqwest/content-analyzer-difficulty`
**Version:** 1.0.0
**Type:** Content Analysis & Difficulty Classification
**Icon:** 📊
**Budget:** $50 of $850

---

## Agent Definition

### Persona

**Role:** Educational Content Difficulty Assessor and Learning Pathway Recommender

**Identity:** I am the Learning Difficulty Scorer, a specialized analyzer that evaluates educational content across 4 critical dimensions: reading level, cognitive complexity, prerequisite knowledge, and overall difficulty. I classify content from Beginner to Expert and recommend appropriate learning pathways for different audiences.

**Communication Style:** Analytical, educational, and learner-focused. I provide detailed difficulty assessments with clear reasoning, helping educators and learners understand exactly what level a piece of content is appropriate for and what background knowledge is needed.

**Principles:**
- **Multi-Dimensional Assessment:** Difficulty is not one-dimensional (4 factors considered)
- **Evidence-Based:** All classifications backed by measurable metrics
- **Learner-Centered:** Recommendations focus on student success
- **Transparent Reasoning:** Every score includes detailed explanation
- **Adaptive Pathways:** Suggest learning progressions based on current level

---

## Capabilities

### 4-Dimension Assessment System

**1. Reading Level Analyzer** (30% weight)
- Flesch-Kincaid Grade Level (0-18+)
- Flesch Reading Ease score (0-100)
- Lexile Framework estimate (0-2000)
- Text complexity metrics (sentence length, syllables, complex words)
- Age-appropriate recommendations

**2. Cognitive Complexity Analyzer** (40% weight)
- Bloom's Taxonomy classification (6 levels)
  - Remember: Recall facts and information
  - Understand: Explain concepts and ideas
  - Apply: Use knowledge in new situations
  - Analyze: Examine relationships and patterns
  - Evaluate: Make judgments and decisions
  - Create: Produce new work or ideas
- Keyword-based indicator detection
- Confidence scoring based on evidence strength

**3. Prerequisite Knowledge Analyzer** (30% weight)
- Explicit prerequisite detection (stated requirements)
- Subject-specific prerequisite mapping (Math, CS, Science)
- Complexity tier classification (Introductory → Expert)
- Prerequisite count and listing

**4. Overall Difficulty Classifier**
- Synthesizes all 3 dimensions with weighted average
- 4-level classification: Beginner / Intermediate / Advanced / Expert
- 1-10 difficulty score for granularity
- Target audience definition
- Learning pathway recommendations

---

## Input Schema

```json
{
  "passed_content": [
    {
      "content": {
        "title": "string",
        "url": "string",
        "source": "string",
        "type": "string",
        "metadata": {
          "description": "string",
          "snippet": "string",
          "abstract": "string",
          "channel": "string (YouTube)",
          "duration": "string (videos)"
        }
      },
      "scores": {
        "credibility": {"score": "number"},
        "accuracy": {"score": "number"},
        "production": {"score": "number"},
        "educational": {"score": "number"},
        "engagement": {"score": "number"}
      },
      "overall_score": "number"
    }
  ]
}
```

---

## Output Schema

```json
{
  "difficulty_scored_content": [
    {
      "content": "object (original item)",
      "difficulty_analysis": {
        "reading_level": {
          "grade_level": "number (0-18+)",
          "reading_ease": "number (0-100)",
          "lexile_estimate": "number (0-2000)",
          "recommendation": "string",
          "confidence": "number (0-1)",
          "details": "object"
        },
        "cognitive_complexity": {
          "bloom_level": "number (1-6)",
          "bloom_label": "string",
          "indicators": "array[string]",
          "confidence": "number (0-1)",
          "reasoning": "string"
        },
        "prerequisites": {
          "prerequisite_count": "number",
          "prerequisites": "array[string]",
          "complexity_tier": "string",
          "confidence": "number (0-1)",
          "reasoning": "string"
        },
        "overall_difficulty": {
          "level": "Beginner | Intermediate | Advanced | Expert",
          "score": "number (1-10)",
          "confidence": "number (0-1)",
          "factors": "object",
          "recommendation": "string",
          "target_audience": "string"
        }
      },
      "quality_scores": "object (from Quality Assessment)"
    }
  ],
  "statistics": {
    "total_items": "number",
    "reading_level": { "average_grade_level": "number" },
    "cognitive_complexity": { "average_bloom_level": "number" },
    "prerequisites": { "average_prerequisite_count": "number" },
    "overall_difficulty": { "average_score": "number" }
  },
  "distribution": {
    "counts": {
      "Beginner": "number",
      "Intermediate": "number",
      "Advanced": "number",
      "Expert": "number"
    },
    "percentages": { ... }
  },
  "next_stage": "Module Generators"
}
```

---

## Configuration

### Default Parameters

```yaml
difficulty_assessment:
  reading_level:
    grade_ranges:
      beginner: [0, 6]        # Elementary
      intermediate: [7, 10]   # Middle/High School
      advanced: [11, 14]      # High School/College
      expert: [15, 20]        # College/Graduate

  cognitive_complexity:
    bloom_mapping:
      1: Remember    # Recall facts
      2: Understand  # Explain concepts
      3: Apply       # Use knowledge
      4: Analyze     # Examine relationships
      5: Evaluate    # Make judgments
      6: Create      # Produce new work

  overall_difficulty:
    component_weights:
      reading_level: 0.30          # 30%
      cognitive_complexity: 0.40   # 40% (most important)
      prerequisites: 0.30          # 30%
```

### Customization

Adjust in `config/difficulty_thresholds.yaml`:

- **K-12 focus:** Lower grade_ranges, emphasize reading_level
- **Higher education:** Raise thresholds, emphasize cognitive_complexity
- **Sequential curriculum:** Increase prerequisites weight to 0.35-0.40

---

## Performance Targets

- **Processing Speed:** 50-100 items/second
- **Classification Accuracy:** >85% appropriate difficulty level
- **Memory:** Stateless, minimal footprint
- **Reliability:** Graceful handling of missing metadata

---

## Integration

### Pipeline Position

```
Quality Assessment Analyzer
    ↓
output/quality_filtered.json
    ↓
[LEARNING DIFFICULTY SCORER] ← THIS AGENT
    ↓
output/difficulty_scored.json
    ↓
Module Generators
```

### Upstream: Quality Assessment

**Receives:**
- Quality-validated content (5-dimension scores)
- High-quality educational materials only
- Content metadata and descriptions

**Format:** JSON with passed_content array

### Downstream: Module Generators

**Provides:**
- Difficulty-scored content with 4-dimension analysis
- Target audience recommendations
- Learning pathway suggestions
- Beginner → Expert classifications

**Format:** JSON with difficulty_scored_content array

---

## Usage Examples

### Python API

```python
from difficulty_scorer import DifficultyScorer

# Initialize scorer
scorer = DifficultyScorer()

# Load quality-filtered content
import json
with open('output/quality_filtered.json') as f:
    quality_data = json.load(f)

# Analyze difficulty
results = scorer.analyze(quality_data['passed_content'])

# Generate report
report = scorer.generate_report(results)

# Save for Module Generators
with open('output/difficulty_scored.json', 'w') as f:
    json.dump(report, f, indent=2)

# Print summary
print(scorer.get_summary(results))
```

### Command Line

```bash
# Run complete analysis
python scripts/run_difficulty_analysis.py

# Output:
# ============================================================
# DIFFICULTY SCORER - Learning Difficulty Assessment
# ============================================================
#
# [Difficulty Scorer] Processing X quality-filtered items...
#
# 📚 Reading Level: Average Grade Level 9.2
# 🧠 Cognitive Complexity: Average Bloom's Level 3.5
# 📋 Prerequisites: Average Prerequisites 1.8
# 🎯 Overall Difficulty: Average Score 5.4/10
#
# 📊 Distribution:
#   Beginner: 10 (23.8%)
#   Intermediate: 20 (47.6%)
#   Advanced: 10 (23.8%)
#   Expert: 2 (4.8%)
#
# → Ready for Module Generators
```

---

## Difficulty Classification Examples

### Beginner (Score 1-3)

**Characteristics:**
- Reading: Elementary level (K-6)
- Cognitive: Remember/Understand (Bloom's 1-2)
- Prerequisites: 0-1, Introductory
- Target: Elementary students, beginners

**Example:** "What is Addition? Simple Math for Kids"

---

### Intermediate (Score 4-6)

**Characteristics:**
- Reading: Middle/High School (7-10)
- Cognitive: Understand/Apply (Bloom's 2-3)
- Prerequisites: 1-2, Intermediate
- Target: High school, early college

**Example:** "Introduction to Python Programming"

---

### Advanced (Score 7-8)

**Characteristics:**
- Reading: College level (11-14)
- Cognitive: Apply/Analyze (Bloom's 3-4)
- Prerequisites: 3-4, Advanced
- Target: Upper-division college, professionals

**Example:** "Advanced Data Structures and Algorithms"

---

### Expert (Score 9-10)

**Characteristics:**
- Reading: Graduate level (15+)
- Cognitive: Evaluate/Create (Bloom's 5-6)
- Prerequisites: 5+, Expert
- Target: Graduate students, researchers

**Example:** "Quantum Field Theory: Renormalization Techniques"

---

## Quality Assurance

### Testing

- **Unit tests:** Individual analyzer validation
- **Integration tests:** End-to-end pipeline
- **Fixtures:** Sample content at each difficulty level
- **Coverage:** >90% code coverage target

### Validation

- **Flesch-Kincaid accuracy:** Validated against standard implementations
- **Bloom's taxonomy:** Keyword mappings reviewed by educators
- **Prerequisites:** Subject-specific mappings from curriculum standards
- **Overall classification:** Cross-validated with human assessments

---

## Design Decisions

### Why 4 Dimensions?

1. **Reading Level:** Text readability is foundational
2. **Cognitive Complexity:** Thinking skills required vary widely
3. **Prerequisites:** Background knowledge determines accessibility
4. **Overall Classification:** Synthesizes all factors for actionable insight

### Why Weight Cognitive Complexity Highest (40%)?

Cognitive demand is the strongest predictor of learning difficulty. A well-written text (easy reading) can still be cognitively demanding (complex concepts).

### Why Beginner → Expert (4 levels)?

Four levels provide useful granularity without overwhelming choice:
- **Beginner:** Starting point, minimal background
- **Intermediate:** Building skills, some background
- **Advanced:** Mastery-level, solid foundation required
- **Expert:** Professional/research level

---

## Future Enhancements

### Potential Additions

- **AI-powered content analysis:** LLM-based deep text understanding
- **Domain-specific scoring:** Specialized metrics for Math, Science, Programming
- **Adaptive recommendations:** Personalized based on learner profile
- **Learning time estimation:** Predict hours needed to master content

### Expansion Opportunities

- **Accessibility scoring:** Reading disabilities, ESL considerations
- **Visual complexity:** Analyze diagrams, charts, multimedia
- **Interactive complexity:** Assess hands-on activities, simulations

---

## BMAD Principles Applied

1. **Modularity:** Each analyzer is independent and reusable
2. **Configuration-Driven:** All thresholds in YAML config
3. **Production-Ready:** Comprehensive error handling and logging
4. **Observable:** Detailed reasoning for every classification
5. **Testable:** Complete test suite with fixtures

---

## Metadata

**Created:** 2025-11-19
**Budget Allocation:** $50 of $850
**Phase:** 2.2 - Content Analyzers (Learning Difficulty)
**Status:** ✅ Production-Ready
**Part of:** LearnQwest™ Qwest-ion Ecosystem

**Previous Agent:** Quality Assessment Analyzer (5-dimension quality scoring)
**Next Agent:** Module Generators (adaptive content creation)

**Pipeline Stage:** 3 of 4 (Omnisearch → Quality → Difficulty → Generators)

---

**Agent Signature:** Learning Difficulty Scorer v1.0
**Maintainer:** LearnQwest Team
**License:** MIT
