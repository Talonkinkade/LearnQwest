# Module Generator #1: Learning Module Creator

**Agent ID:** `learnqwest/module-generator-learning`
**Version:** 1.0.0
**Type:** Module Generation & Curriculum Design
**Icon:** 📚
**Budget:** Part of Module Generators phase

---

## Agent Definition

### Persona

**Role:** Educational Curriculum Designer and Learning Experience Architect

**Identity:** I am the Learning Module Creator, a BMAD-based curriculum design specialist that transforms difficulty-scored educational content into comprehensive, hierarchical learning modules. I create structured learning experiences with optimal lesson sequences, SMART learning objectives aligned to Bloom's Taxonomy, and engaging activities differentiated for all learners.

**Communication Style:** Pedagogical, structured, and learner-focused. I provide clear rationale for every curriculum design decision, explaining how module structure, lesson sequencing, learning objectives, and activities work together to create effective learning pathways.

**Principles:**
- **Hierarchical Design:** Clear structure (Modules → Units → Lessons → Sections)
- **Progressive Complexity:** Scaffold from beginner to expert thoughtfully
- **Bloom's Alignment:** All objectives and activities aligned to cognitive taxonomy
- **SMART Objectives:** Specific, Measurable, Achievable, Relevant, Time-bound
- **Differentiation:** Multiple pathways for diverse learners
- **Evidence-Based:** Use cognitive science and learning theory

---

## Capabilities

### 1. Module Structure Generation

**Creates hierarchical learning organization:**
- **Modules**: Top-level learning containers
- **Units**: Thematic groupings by difficulty/topic
- **Lessons**: Individual learning experiences
- **Sections**: Lesson components (Intro, Core, Practice, Check)

**Features:**
- Difficulty-based grouping (Beginner → Expert)
- Content collection analysis
- Duration estimation
- Prerequisite extraction
- Learning outcomes generation
- Module metadata creation

### 2. Lesson Sequencing

**4 Sequencing Strategies:**

1. **Linear**: Beginner → Expert straight progression
2. **Modular**: Group by difficulty, cognitive progression within
3. **Spiral**: Revisit topics at increasing difficulty (Bruner's theory)
4. **Adaptive** (Default): Prerequisite-aware balanced progression

**Analysis:**
- Prerequisite dependency graphs
- Topological ordering
- Difficulty progression metrics
- Bloom's progression tracking
- Scaffolding level calculation

### 3. Learning Objectives Creation

**SMART Objectives:**
- **S**pecific: Focused on clear concepts
- **M**easurable: Assessment criteria defined
- **A**chievable: Appropriate for difficulty level
- **R**elevant: Aligned to content
- **T**ime-bound: Mastery timeframe specified

**Bloom's Taxonomy Integration:**
- Level 1 (Remember): Identify, recall, list
- Level 2 (Understand): Explain, summarize, interpret
- Level 3 (Apply): Apply, demonstrate, solve
- Level 4 (Analyze): Analyze, compare, examine
- Level 5 (Evaluate): Evaluate, critique, justify
- Level 6 (Create): Create, design, develop

**Generates:**
- 3 objectives per lesson (primary, supporting, extension)
- 2 objectives per unit (overarching)
- Module-level learning outcomes

### 4. Activity Suggestions

**Activity Types by Bloom's Level:**

1. **Remember**: Flashcards, Matching, Quiz, Labeling, Fact Sheets
2. **Understand**: Concept Maps, Summaries, Explanations, Compare/Contrast
3. **Apply**: Problem Sets, Simulations, Demonstrations, Case Studies
4. **Analyze**: Data Analysis, Comparative Studies, Critical Reviews
5. **Evaluate**: Peer Reviews, Critiques, Debates, Justifications
6. **Create**: Projects, Designs, Productions, Innovations

**For Each Activity:**
- Implementation steps (5-7 steps)
- Materials needed
- Assessment criteria
- Variations for differentiation (Simplified, Standard, Advanced, Collaborative)
- Time estimates

---

## Input Schema

```json
{
  "difficulty_scored_content": [
    {
      "content": {
        "title": "string",
        "url": "string",
        "source": "string",
        "type": "string"
      },
      "difficulty_analysis": {
        "reading_level": {
          "grade_level": "number (0-18+)",
          "reading_ease": "number (0-100)"
        },
        "cognitive_complexity": {
          "bloom_level": "number (1-6)",
          "bloom_label": "string"
        },
        "prerequisites": {
          "prerequisites": ["array"],
          "complexity_tier": "string"
        },
        "overall_difficulty": {
          "level": "Beginner | Intermediate | Advanced | Expert",
          "score": "number (1-10)"
        }
      },
      "quality_scores": { ... }
    }
  ]
}
```

---

## Output Schema

```json
{
  "module_id": "string",
  "title": "string",
  "description": "string",
  "difficulty_level": "Beginner | Intermediate | Advanced | Expert",
  "estimated_duration": "string",

  "units": [
    {
      "unit_number": "number",
      "title": "string",
      "difficulty": "string",
      "description": "string",
      "estimated_duration": "string",

      "lessons": [
        {
          "lesson_number": "number",
          "title": "string",
          "bloom_level": "string",
          "estimated_duration": "string",

          "content_source": {
            "url": "string",
            "source": "string",
            "type": "string"
          },

          "learning_objectives": [
            {
              "objective": "string",
              "bloom_level": "number",
              "bloom_label": "string",
              "measurement_criteria": "string",
              "difficulty_level": "string",
              "time_expectation": "string",
              "smart_analysis": {
                "Specific": "string",
                "Measurable": "string",
                "Achievable": "string",
                "Relevant": "string",
                "Time-bound": "string"
              }
            }
          ],

          "activities": [
            {
              "name": "string",
              "type": "string",
              "description": "string",
              "bloom_level": "number",
              "difficulty_level": "string",
              "estimated_time": "string",
              "materials_needed": ["array"],
              "implementation_steps": ["array"],
              "assessment_criteria": ["array"],
              "variations": [
                {
                  "name": "string",
                  "description": "string"
                }
              ]
            }
          ],

          "sections": [
            {
              "section": "string",
              "purpose": "string",
              "duration": "string"
            }
          ]
        }
      ],

      "lesson_sequence": {
        "rationale": "string",
        "difficulty_progression": "string",
        "bloom_progression": "string",
        "learning_path_type": "string"
      },

      "learning_objectives": ["array"],
      "unit_activities": [{ ... }]
    }
  ],

  "prerequisites": ["array"],
  "learning_outcomes": ["array"],
  "module_objectives": [{ ... }],

  "metadata": {
    "content_count": "number",
    "unit_count": "number",
    "bloom_levels": ["array"],
    "reading_levels": ["array"],
    "created_at": "ISO timestamp",
    "generator": "string"
  }
}
```

---

## Configuration

### Default Settings

```yaml
module_generation:
  strategy: "adaptive"

  sequencing:
    strategy: "adaptive"  # linear, modular, spiral, adaptive
    respect_prerequisites: true
    balance_difficulty: true

  objectives:
    objectives_per_lesson: 3
    use_smart_criteria: true
    align_to_bloom: true

  activities:
    activities_per_lesson: 3
    include_unit_activities: true
    provide_variations: true

differentiation:
  simplified_version: true
  standard_version: true
  advanced_challenge: true
  collaborative_options: true
```

---

## Performance Targets

- **Processing Speed**: 20-40 lessons/second
- **Module Creation**: Complete module in < 5 seconds
- **Sequencing Accuracy**: >90% prerequisite respect
- **Objective Quality**: 100% SMART-compliant
- **Activity Variety**: Minimum 3 Bloom's levels per module

---

## Integration

### Pipeline Position

```
Quality Assessment Analyzer
    ↓
output/quality_filtered.json
    ↓
Learning Difficulty Scorer
    ↓
output/difficulty_scored.json
    ↓
[LEARNING MODULE CREATOR] ← THIS AGENT
    ↓
output/learning_modules.json
    ↓
Assessment Generator
```

### Upstream: Learning Difficulty Scorer

**Receives:**
- Difficulty-scored content (4-dimension analysis)
- Reading levels, cognitive complexity, prerequisites
- Overall difficulty classifications

**Format:** JSON with difficulty_scored_content array

### Downstream: Assessment Generator

**Provides:**
- Complete learning modules with hierarchical structure
- SMART learning objectives (ready for assessment creation)
- Activity suggestions with assessment criteria
- Bloom's taxonomy alignment (for question generation)

**Format:** JSON with enhanced module structure

---

## Usage Examples

### Python API

```python
from module_creator import ModuleCreator

# Initialize
creator = ModuleCreator()

# Load difficulty-scored content
import json
with open('output/difficulty_scored.json') as f:
    data = json.load(f)
    content = data['difficulty_scored_content']

# Create module
module = creator.create_module(content)

# Generate report
report = creator.generate_report(module)
print(f"Created module with {report['summary']['unit_count']} units")
print(f"Total lessons: {report['summary']['lesson_count']}")
print(f"Total objectives: {report['summary']['objective_count']}")

# Save
from module_creator import save_module
save_module(module, 'output/learning_modules.json')
```

### Command Line

```bash
python scripts/run_module_creation.py

# Output:
# ============================================================
# LEARNING MODULE CREATOR - BMAD Module Generation
# ============================================================
#
# ✓ Loaded 42 difficulty-scored items
#
# [Module Creator] Creating comprehensive learning module...
#   Step 1: Building module structure
#   Step 2: Sequencing lessons optimally
#   Step 3: Generating SMART learning objectives
#   Step 4: Suggesting engaging activities
#
# 📚 Module Summary
# ┌─────────────────────┬──────────────────────┐
# │ Difficulty Level    │ Intermediate         │
# │ Estimated Duration  │ 8.5 hours            │
# │ Unit Count          │ 3                    │
# │ Lesson Count        │ 15                   │
# │ Objective Count     │ 47                   │
# │ Activity Count      │ 45                   │
# └─────────────────────┴──────────────────────┘
#
# 🧠 Bloom's Taxonomy Coverage:
#   Understand: 5 lessons
#   Apply: 7 lessons
#   Analyze: 3 lessons
#
# → Ready for Assessment Generator
```

---

## Module Structure Example

### Beginner Module (Score 1-3)

```
Module: Introduction to Python Programming
├── Unit 1: Beginner Level Content
│   ├── Lesson 1: What is Python?
│   │   ├── Objectives (3): Remember, Understand, Apply
│   │   ├── Activities (3): Quiz, Concept Map, First Program
│   │   └── Sections: Intro, Core, Practice, Check
│   └── Lesson 2: Variables and Data Types
│       └── ...
└── Duration: 4 hours
```

### Advanced Module (Score 7-8)

```
Module: Advanced Data Structures
├── Unit 1: Advanced Level Content
│   ├── Lesson 1: Graph Algorithms
│   │   ├── Objectives (3): Analyze, Evaluate, Create
│   │   ├── Activities (3): Data Analysis, Critique, Project
│   │   └── Sections: Intro, Core, Practice, Check
│   └── Lesson 2: Dynamic Programming
│       └── ...
└── Duration: 12 hours
```

---

## Quality Assurance

### Module Validation

- **Structure**: All units have 2+ lessons
- **Progression**: Difficulty increases or stays balanced
- **Bloom's Coverage**: Minimum 3 different levels represented
- **Objectives**: 100% SMART-compliant
- **Activities**: Varied types across units
- **Prerequisites**: Honored in sequencing

### Testing

```bash
# Run tests
pytest tests/

# Test structure generation
pytest tests/test_module_structure.py -v

# Test sequencing
pytest tests/test_lesson_sequencer.py -v

# Test objectives
pytest tests/test_objective_creator.py -v

# Test activities
pytest tests/test_activity_suggester.py -v
```

---

## Design Decisions

### Why Hierarchical Structure?

**Modules → Units → Lessons → Sections**

Hierarchy provides:
1. Clear navigation for learners
2. Logical grouping by difficulty/topic
3. Flexibility for different pacing
4. Easy progress tracking

### Why 4 Sequencing Strategies?

Different content requires different progressions:
- **Linear**: Traditional textbook approach
- **Modular**: Competency-based mastery
- **Spiral**: Constructivist revisiting
- **Adaptive**: Modern personalized learning

### Why SMART Objectives?

Non-SMART objectives are often:
- Vague ("understand concepts")
- Unmeasurable (no assessment criteria)
- Unrealistic (too advanced/easy)
- Disconnected (not aligned to content)

SMART ensures quality and assessability.

---

## BMAD Principles Applied

1. **Modularity**: 4 independent generators (structure, sequence, objectives, activities)
2. **Configuration-Driven**: All settings in module_config.yaml
3. **Production-Ready**: Error handling, type hints, comprehensive logging
4. **Observable**: Detailed rationale for every design decision
5. **Testable**: Pure functions, clear contracts, fixtures available

---

## Metadata

**Created:** 2025-11-19
**Budget Allocation:** Part of Module Generators phase
**Phase:** 3.1 - Module Generators (Learning Module Creator)
**Status:** ✅ Production-Ready
**Part of:** LearnQwest™ Qwest-ion Ecosystem

**Previous Agent:** Learning Difficulty Scorer (4-dimension difficulty analysis)
**Next Agent:** Assessment Generator (quiz/test creation)

**Pipeline Stage:** 4 of 5 (Omnisearch → Quality → Difficulty → **Modules** → Assessment)

---

**Agent Signature:** Learning Module Creator v1.0
**Maintainer:** LearnQwest Team
**License:** MIT
**BMAD Version:** 6.0.0-alpha.7
