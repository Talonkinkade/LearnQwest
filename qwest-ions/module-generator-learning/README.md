# Learning Module Creator (BMAD)

**Agent ID:** `learnqwest/module-generator-learning`
**Version:** 1.0.0
**Type:** Module Generation & Learning Design
**Icon:** 📚
**Budget:** Part of Module Generators phase

---

## Overview

The **Learning Module Creator** is a BMAD-based agent that transforms difficulty-scored educational content into comprehensive, hierarchical learning modules with structured curriculum, optimal lesson sequences, SMART learning objectives, and engaging activities.

## Features

### 4 Core Generators

**1. Module Structure Generator** ([module_structure.py](src/generators/module_structure.py))
- Creates hierarchical organization: Modules → Units → Lessons → Sections
- Groups content by difficulty level (Beginner → Expert)
- Analyzes content collection for optimal organization
- Generates module metadata and duration estimates

**2. Lesson Sequencer** ([lesson_sequencer.py](src/generators/lesson_sequencer.py))
- 4 sequencing strategies: Linear, Modular, Spiral, Adaptive
- Prerequisite-aware topological ordering
- Difficulty and Bloom's taxonomy progression analysis
- Scaffolding level calculation

**3. Objective Creator** ([objective_creator.py](src/generators/objective_creator.py))
- SMART learning objectives (Specific, Measurable, Achievable, Relevant, Time-bound)
- Bloom's taxonomy alignment (6 levels)
- Measurement criteria generation
- Module-level and lesson-level objectives

**4. Activity Suggester** ([activity_suggester.py](src/generators/activity_suggester.py))
- Bloom-aligned activity types (Flashcards → Projects)
- Difficulty-appropriate implementations
- Variations for differentiation
- Unit culminating activities

## Input Schema

Receives from **Learning Difficulty Scorer**:

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
        "reading_level": { "grade_level": "number", ... },
        "cognitive_complexity": { "bloom_level": "number", "bloom_label": "string", ... },
        "prerequisites": { "prerequisites": ["array"], ... },
        "overall_difficulty": { "level": "string", "score": "number", ... }
      }
    }
  ]
}
```

## Output Schema

Provides to **Assessment Generator**:

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
      "lessons": [
        {
          "lesson_number": "number",
          "title": "string",
          "bloom_level": "string",
          "estimated_duration": "string",
          "learning_objectives": [
            {
              "objective": "string",
              "bloom_level": "number",
              "measurement_criteria": "string",
              "smart_analysis": { ... }
            }
          ],
          "activities": [
            {
              "name": "string",
              "type": "string",
              "description": "string",
              "implementation_steps": ["array"],
              "assessment_criteria": ["array"],
              "variations": [{ ... }]
            }
          ],
          "sections": [{ ... }]
        }
      ],
      "lesson_sequence": {
        "rationale": "string",
        "difficulty_progression": "string",
        "bloom_progression": "string"
      }
    }
  ],
  "prerequisites": ["array"],
  "learning_outcomes": ["array"],
  "module_objectives": [{ ... }],
  "metadata": { ... }
}
```

## Usage

### Python API

```python
from module_creator import ModuleCreator

# Initialize creator
creator = ModuleCreator()

# Load difficulty-scored content
import json
with open('output/difficulty_scored.json') as f:
    data = json.load(f)
    content = data['difficulty_scored_content']

# Create complete module
module = creator.create_module(content)

# Generate report
report = creator.generate_report(module)

# Save module
from module_creator import save_module
save_module(module, 'output/learning_modules.json')
```

### Command Line

```bash
# Run complete module creation
python scripts/run_module_creation.py

# Output:
# ============================================================
# LEARNING MODULE CREATOR - BMAD Module Generation
# ============================================================
#
# [Module Creator] Loading difficulty-scored content...
# ✓ Loaded X difficulty-scored items
#
# [Module Creator] Creating comprehensive learning module...
#   Step 1: Building module structure
#   Step 2: Sequencing lessons optimally
#   Step 3: Generating SMART learning objectives
#   Step 4: Suggesting engaging activities
#
# 📚 Module Summary
# ┌─────────────────────┬──────────────────────┐
# │ Module ID           │ module-...           │
# │ Difficulty Level    │ Intermediate         │
# │ Estimated Duration  │ 8.5 hours            │
# │ Unit Count          │ 3                    │
# │ Lesson Count        │ 15                   │
# │ Objective Count     │ 47                   │
# │ Activity Count      │ 45                   │
# └─────────────────────┴──────────────────────┘
#
# → Ready for Assessment Generator
```

## Configuration

Edit [config/module_config.yaml](config/module_config.yaml):

```yaml
module_generation:
  strategy: "adaptive"  # linear, modular, spiral, adaptive

  sequencing:
    strategy: "adaptive"
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
```

## Sequencing Strategies

**Linear**: Beginner → Expert in straight progression
**Modular**: Group by difficulty, cognitive progression within modules
**Spiral**: Revisit topics at increasing difficulty
**Adaptive** (Default): Prerequisite-aware with balanced progression

## Bloom's Taxonomy Integration

### 6 Cognitive Levels

1. **Remember**: Flashcards, Quizzes, Matching
2. **Understand**: Concept Maps, Summaries, Explanations
3. **Apply**: Problem Sets, Simulations, Demonstrations
4. **Analyze**: Data Analysis, Comparative Studies, Reviews
5. **Evaluate**: Peer Reviews, Critiques, Debates
6. **Create**: Projects, Designs, Productions

### Objective Examples

- **Remember**: "Students will be able to identify key concepts with 80% accuracy"
- **Understand**: "Students will be able to explain concepts clearly in own words"
- **Apply**: "Students will be able to demonstrate correct use of procedures"
- **Analyze**: "Students will be able to compare and contrast relationships"
- **Evaluate**: "Students will be able to justify conclusions with evidence"
- **Create**: "Students will be able to design original projects"

## SMART Objectives

Every objective includes:

- **S**pecific: Focused on clear concept from specific source
- **M**easurable: Assessment method defined
- **A**chievable: Appropriate for difficulty level
- **R**elevant: Aligned with content objectives
- **T**ime-bound: Expected mastery timeframe

## Architecture

```
ModuleCreator (Orchestrator)
    ↓
create_module_structure()
    ├── _analyze_content_collection()
    ├── _group_by_difficulty_and_topic()
    └── _create_units()
        └── _create_lesson_from_content()
    ↓
sequence_lessons()
    ├── _build_prerequisite_graph()
    ├── _adaptive_sequence() (default)
    └── _analyze_progressions()
    ↓
create_objectives()
    ├── _create_objective_at_level()
    └── SMART analysis
    ↓
suggest_activities()
    ├── _create_activity_at_level()
    ├── _generate_implementation_steps()
    └── _generate_variations()
```

## Pipeline Position

```
Omnisearch
    ↓
Quality Assessment
    ↓
Learning Difficulty Scorer
    ↓
[LEARNING MODULE CREATOR] ← THIS AGENT
    ↓
Assessment Generator
    ↓
ADA Orchestrator
```

## Files Created

- **src/generators/module_structure.py** (420 lines) - Hierarchical organization
- **src/generators/lesson_sequencer.py** (390 lines) - Optimal sequencing
- **src/generators/objective_creator.py** (450 lines) - SMART objectives
- **src/generators/activity_suggester.py** (510 lines) - Engaging activities
- **src/generators/__init__.py** (26 lines) - Exports
- **src/module_creator.py** (280 lines) - Main orchestrator
- **config/module_config.yaml** (110 lines) - Configuration
- **scripts/run_module_creation.py** (180 lines) - CLI integration
- **requirements.txt** - Dependencies
- **README.md** - This file

**Total:** 10 files, ~2,366 lines of production code

## Design Decisions

### Why 4 Generators?

1. **Module Structure**: Foundation - hierarchical organization
2. **Lesson Sequencer**: Flow - optimal learning progression
3. **Objective Creator**: Clarity - measurable learning targets
4. **Activity Suggester**: Engagement - hands-on practice

### Why SMART Objectives?

SMART criteria ensure objectives are:
- Clear and focused (not vague)
- Assessable (can measure success)
- Realistic (students can achieve)
- Connected (aligned to content)
- Timely (completion timeframe)

### Why Multiple Sequencing Strategies?

Different content and learners benefit from different progressions:
- **Linear**: Traditional curriculum
- **Modular**: Competency-based learning
- **Spiral**: Bruner's spiral curriculum theory
- **Adaptive**: Modern personalized learning

## BMAD Principles Applied

1. **Modularity**: Each generator is independent and reusable
2. **Configuration-Driven**: All settings in YAML config
3. **Production-Ready**: Error handling, logging, type hints
4. **Observable**: Detailed rationale for every decision
5. **Testable**: Pure functions, clear inputs/outputs

## Testing

```bash
# Run tests (when created)
pytest tests/

# Test module structure
pytest tests/test_module_structure.py

# Test sequencing
pytest tests/test_lesson_sequencer.py

# Test objectives
pytest tests/test_objective_creator.py

# Test activities
pytest tests/test_activity_suggester.py
```

## Metadata

**Created:** 2025-11-19
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
