# LearnQwest™ Visual Workflow Architecture

## Overview

This document provides a **visual, interactive map** of the LearnQwest™ system architecture, showing how all components work together to create an educational platform where Qwestians™ (students) embark on epic learning journeys guided by 8 AI Qwestian Companions.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LEARNQWEST™ ECOSYSTEM                               │
│                  "Every Qwestian™ is a Hero"                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼────────┐            ┌────────▼────────┐
            │   QWESTIANS™   │            │  QWEST-IONS™    │
            │   (Students)   │◄──────────►│  (Challenges)   │
            └───────┬────────┘            └────────┬────────┘
                    │                               │
                    │         ┌────────────────────┐│
                    │         │                    ││
                    └────────►│  8 AI COMPANIONS   ││
                              │  (RAGENTS)         ││
                              └──────┬─────────────┘│
                                     │              │
        ┌────────────────────────────┼──────────────┘
        │            │               │              │
┌───────▼────┐  ┌───▼────┐  ┌──────▼──┐  ┌───────▼────┐
│   Scout    │  │Connector│  │Motivator│  │  Storyteller│
│ Companion  │  │Companion│  │Companion│  │  Companion │
└───────┬────┘  └───┬────┘  └────┬────┘  └──────┬─────┘
        │           │             │               │
        └───────────┴─────────────┴───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────┐  ┌──────────▼──┐  ┌────────────▼─────┐
│   Social   │  │   Advisor   │  │     Builder      │
│ Companion  │  │  Companion  │  │    Companion     │
└───────┬────┘  └──────┬──────┘  └────────┬─────────┘
        │              │                   │
        └──────────────┴───────────────────┘
                       │
              ┌────────▼────────┐
              │   Reflector     │
              │   Companion     │
              └────────┬────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   QWESTIAN NATION            │
        │   (Community & Achievements) │
        └──────────────────────────────┘
```

## Data Flow Architecture

### 1. Content Ingestion → Qwest-ion™ Generation

```
┌──────────────────┐
│  Content Sources │
└────────┬─────────┘
         │
    ┌────▼─────────────────────────────────────────┐
    │                                               │
┌───▼────────┐  ┌──────────────┐  ┌──────────────┐│
│  YouTube   │  │   Textbooks  │  │    TEKS      ││
│  Videos    │  │   & Docs     │  │  Standards   ││
└───┬────────┘  └──────┬───────┘  └──────┬───────┘│
    │                  │                  │        │
    └──────────────────┴──────────────────┘        │
                       │                           │
              ┌────────▼────────┐                  │
              │  Intake Zones   │                  │
              │  (Dropzones)    │◄─────────────────┘
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   Ion           │
              │   Processors    │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │Extract  │  │Analyze  │  │Generate │
    │Content  │  │Patterns │  │Qwestions│
    └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │
         └────────────┴────────────┘
                      │
         ┌────────────▼────────────┐
         │  Qwest-ions™ Database   │
         │  (Educational Content)  │
         └─────────────────────────┘
```

### 2. Qwestian™ Learning Journey

```
┌──────────────┐
│  Qwestian™   │
│  Enters      │
│  System      │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ Initial         │
│ Assessment      │──────┐
│ (Level Check)   │      │
└─────────┬───────┘      │
          │              ▼
          │         ┌─────────────────┐
          │         │  Scout Companion│
          │         │  Analyzes       │
          │         │  Qwestian       │
          │         └────────┬────────┘
          │                  │
          └──────────────────┘
                     │
          ┌──────────▼─────────┐
          │  Personalized      │
          │  Learning Path     │
          │  Generated         │
          └──────────┬─────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
   ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
   │Qwest- │    │Qwest- │    │Qwest- │
   │ion #1 │    │ion #2 │    │ion #N │
   └───┬───┘    └───┬───┘    └───┬───┘
       │            │            │
       │     ┌──────▼──────┐     │
       │     │ Companions  │     │
       │     │ Assist      │     │
       │     │ & Guide     │     │
       │     └──────┬──────┘     │
       │            │            │
       └────────────┴────────────┘
                    │
         ┌──────────▼──────────┐
         │  Achievement        │
         │  Unlocked           │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Level Up           │
         │  Progress           │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Reflection         │
         │  (Metacognition)    │
         └─────────────────────┘
```

### 3. Companion Orchestration (RAGENTS)

```
┌─────────────────────────────────────────┐
│         Qwestian™ Faces Challenge       │
└─────────────────┬───────────────────────┘
                  │
       ┌──────────▼──────────┐
       │  RAGENTS Orchestrator│
       │  (Scout-Plan-Build)  │
       └──────────┬───────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────┐                 ┌────▼────┐
│ SCOUT  │                 │  PLAN   │
│ Phase  │────────────────►│  Phase  │
└────────┘                 └────┬────┘
    │                           │
    │  Observes:                │  Selects:
    │  - Current challenge      │  - Which Companions
    │  - Qwestian level         │  - Sequential/Parallel
    │  - Learning patterns      │  - Task breakdown
    │  - Emotional state        │
    │                           │
    └───────────────┬───────────┘
                    │
            ┌───────▼────────┐
            │  BUILD Phase   │
            │  (Execution)   │
            └───────┬────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐      ┌───▼───┐      ┌───▼───┐
│Conn-  │      │Story- │      │Motiv- │
│ector  │◄────►│teller │◄────►│ator   │
└───────┘      └───────┘      └───────┘
    │               │               │
    │    Collaborate & Share        │
    │    Context with Each Other    │
    │                               │
    └───────────────┬───────────────┘
                    │
            ┌───────▼────────┐
            │  OBSERVE Phase │
            │  (Continuous)  │
            └───────┬────────┘
                    │
         ┌──────────┴──────────┐
         │  Performance        │
         │  Metrics & Quality  │
         │  Assessment         │
         └─────────────────────┘
```

## Component Details

### Intake Zones (Ion Architecture)

```
LearnQwest/
├── intake_zones/
│   ├── youtube/
│   │   ├── inbox/         # Drop YouTube URLs
│   │   ├── processing/    # Ion extracting content
│   │   └── completed/     # Transcripts + analysis
│   │
│   ├── textbooks/
│   │   ├── inbox/         # Drop PDF/docs
│   │   ├── processing/    # Ion extracting text
│   │   └── completed/     # Structured content
│   │
│   └── teks/
│       ├── inbox/         # Drop TEKS standards
│       ├── processing/    # Ion aligning content
│       └── completed/     # Aligned Qwest-ions™
│
└── ions/
    ├── youtube_extractor/
    │   ├── ion.yaml       # Configuration
    │   └── handler.py     # Processing logic
    │
    ├── content_analyzer/
    │   ├── ion.yaml
    │   └── handler.py
    │
    └── qwestion_generator/
        ├── ion.yaml
        └── handler.py
```

### Qwestian™ Companions Architecture

```
agents/
├── scout_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── analyze_qwestian()
│       ├── detect_struggles()
│       └── observe_patterns()
│
├── connector_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── create_mindmap()
│       ├── find_connections()
│       └── link_concepts()
│
├── motivator_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── motivate()
│       ├── celebrate_win()
│       └── reframe_challenge()
│
├── social_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── find_quest_party()
│       ├── share_strategy()
│       └── build_community()
│
├── storyteller_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── tell_story()
│       ├── create_scenario()
│       └── make_real()
│
├── advisor_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── recommend_path()
│       ├── suggest_strategy()
│       └── provide_guidance()
│
├── builder_companion/
│   ├── agent.py
│   ├── prompts.py
│   └── tools.py
│       ├── scaffold_project()
│       ├── generate_artifact()
│       └── support_creation()
│
└── reflector_companion/
    ├── agent.py
    ├── prompts.py
    └── tools.py
        ├── reflect_on_journey()
        ├── track_growth()
        └── consolidate_learning()
```

### Database Schema

```
┌──────────────────┐
│   Qwestians™     │
├──────────────────┤
│ id               │
│ username         │
│ level            │
│ experience_pts   │
│ achievements[]   │
│ learning_style   │
│ companion_prefs  │
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼─────────┐
│  Quest_Progress  │
├──────────────────┤
│ qwestian_id      │
│ qwestion_id      │
│ attempts         │
│ best_score       │
│ completion_time  │
│ companion_used   │
└────────┬─────────┘
         │
         │ N:1
         │
┌────────▼─────────┐
│   Qwest-ions™    │
├──────────────────┤
│ id               │
│ teks_standard    │
│ difficulty       │
│ cognitive_level  │
│ question_text    │
│ correct_answer   │
│ distractors[]    │
│ explanation      │
└──────────────────┘
```

## Workflow Examples

### Example 1: YouTube Video → Qwest-ions™

```
1. Teacher drops YouTube URL
   └─► "youtube/inbox/ai_workshop.txt"

2. YouTube Ion activates
   └─► Downloads transcript
   └─► Extracts key concepts
   └─► Identifies learning objectives

3. Content Analyzer Ion
   └─► Analyzes for TEKS alignment
   └─► Identifies appropriate grade level
   └─► Maps to cognitive complexity

4. Qwestion Generator Ion
   └─► Creates 5 unique Qwest-ions™
   └─► Generates distractors
   └─► Writes explanations
   └─► Outputs to database

5. Ready for Qwestians™
   └─► Qwest-ions™ appear in challenge pool
   └─► Companions can now guide Qwestians through them
```

### Example 2: Qwestian™ Struggles with Math

```
1. Qwestian attempts Qwest-ion™
   └─► Gets it wrong twice

2. Scout Companion observes
   └─► Detects struggle pattern
   └─► Identifies misconception
   └─► Signals need for help

3. RAGENTS Orchestrator activates
   └─► SCOUT: Analyzes the specific struggle
   └─► PLAN: Selects Storyteller + Connector + Motivator
   └─► BUILD: Companions collaborate

4. Storyteller Companion
   └─► Creates real-world scenario
   └─► "Imagine you're splitting pizza..."

5. Connector Companion
   └─► Links to prior knowledge
   └─► Shows visual model
   └─► Creates concept map

6. Motivator Companion
   └─► Encourages the Qwestian
   └─► Reframes challenge as achievable
   └─► Celebrates small wins

7. Qwestian tries again
   └─► Success!
   └─► Reflector Companion helps consolidate learning
```

### Example 3: Social Learning Quest Party

```
1. Three Qwestians need help on similar topic
   └─► Scout detects pattern

2. Social Companion activates
   └─► Identifies compatible Qwestians
   └─► Creates "Quest Party"
   └─► Sets up collaborative challenge

3. Qwestians work together
   └─► Share strategies via Social Companion
   └─► Storyteller provides shared narrative
   └─► Advisor guides the group

4. Achievement unlocked
   └─► "First Quest Party" badge
   └─► Community bonds strengthen
   └─► Qwestian Nation grows
```

## Integration Points

### External Systems

```
┌─────────────────────────────────────────────────┐
│            LEARNQWEST™ CORE                     │
└─────────────┬───────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼───┐  ┌──▼───┐
│RAGE- │  │ ADA  │  │ O*NET│
│FORCE │  │Voice │  │Career│
└───┬──┘  └──┬───┘  └──┬───┘
    │        │         │
    │        │         │
    └────────┴─────────┘
             │
    ┌────────▼────────┐
    │  LMS/SIS        │
    │  Integration    │
    └─────────────────┘
```

**RAGEFORCE**: Agent orchestration backend
**ADA**: Voice interface for accessibility
**O*NET**: Career pathway integration
**LMS/SIS**: School system integration

### API Architecture

```
┌──────────────────────────────────┐
│       Frontend (React)           │
│  - Qwestian Dashboard            │
│  - Quest Map (visual progress)   │
│  - Companion Chat Interface      │
│  - Achievement Gallery           │
└───────────┬──────────────────────┘
            │ REST/GraphQL
┌───────────▼──────────────────────┐
│       API Layer (FastAPI)        │
│  - /qwestians                    │
│  - /qwestions                    │
│  - /companions                   │
│  - /achievements                 │
│  - /analytics                    │
└───────────┬──────────────────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼────┐    ┌────▼─────┐
│Postgres│    │  Redis   │
│Database│    │  Cache   │
└────────┘    └──────────┘
```

## Visual Status Dashboard

```
╔════════════════════════════════════════════════════════╗
║           LEARNQWEST™ LIVE DASHBOARD                   ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  Active Qwestians™: 1,247                             ║
║  Qwest-ions™ Completed Today: 3,892                   ║
║  Companions Active: 8 / 8                             ║
║  Quest Parties Running: 23                            ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║  INTAKE ZONES STATUS                                   ║
╠════════════════════════════════════════════════════════╣
║  YouTube:    [████████──] 12 processing               ║
║  Textbooks:  [██────────]  3 processing               ║
║  TEKS:       [██████████] All aligned                 ║
╠════════════════════════════════════════════════════════╣
║  COMPANION ACTIVITY                                    ║
╠════════════════════════════════════════════════════════╣
║  Scout:      🟢 287 observations today                ║
║  Connector:  🟢 156 mindmaps created                  ║
║  Motivator:  🟢 423 encouragements sent               ║
║  Social:     🟢 23 quest parties formed               ║
║  Storyteller:🟢 89 scenarios created                  ║
║  Advisor:    🟢 201 recommendations given             ║
║  Builder:    🟢 67 projects scaffolded                ║
║  Reflector:  🟢 312 reflections facilitated           ║
╠════════════════════════════════════════════════════════╣
║  TOP QWESTIANS™ THIS WEEK                             ║
╠════════════════════════════════════════════════════════╣
║  1. EpicLearner_42    Level 12  ⭐⭐⭐⭐⭐            ║
║  2. QwestHero_99      Level 11  ⭐⭐⭐⭐              ║
║  3. MathMaster_17     Level 10  ⭐⭐⭐⭐              ║
╚════════════════════════════════════════════════════════╝
```

## Technical Stack

### Frontend
- **React** with TypeScript
- **D3.js** for quest map visualization
- **Socket.io** for real-time updates
- **Tailwind CSS** for styling

### Backend
- **FastAPI** (Python) for API
- **PostgreSQL** for main database
- **Redis** for caching + real-time
- **Celery** for background tasks

### AI/ML
- **Anthropic Claude** for companions
- **Pydantic AI** for agent framework
- **LangGraph** for orchestration
- **FAISS** for similarity search

### Infrastructure
- **Docker** for containerization
- **AWS** for cloud hosting
- **Vercel** for frontend
- **Supabase** for database + auth

## Deployment Pipeline

```
Developer Push
      │
      ▼
┌─────────────┐
│   GitHub    │
│  Repository │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  GitHub     │
│  Actions CI │
│  - Tests    │
│  - Lint     │
│  - Build    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Docker    │
│   Build     │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
   ▼        ▼
┌─────┐  ┌─────┐
│Stag-│  │Prod-│
│ ing │  │uction│
└─────┘  └─────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────┐
│      Application Metrics            │
├─────────────────────────────────────┤
│  - Qwestian active sessions         │
│  - Companion response times         │
│  - Qwest-ion completion rates       │
│  - API endpoint performance         │
│  - Database query latency           │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      Logging & Tracing              │
├─────────────────────────────────────┤
│  - Structured JSON logs             │
│  - Distributed tracing              │
│  - Error tracking (Sentry)          │
│  - User action tracking             │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      Dashboards & Alerts            │
├─────────────────────────────────────┤
│  - Grafana visualizations           │
│  - PagerDuty alerts                 │
│  - Slack notifications              │
│  - Weekly reports                   │
└─────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────┐
│         User Layer                  │
│  - OAuth2 + JWT                     │
│  - Role-based access (RBAC)         │
│  - Session management               │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│         API Layer                   │
│  - Rate limiting                    │
│  - Input validation                 │
│  - CORS policies                    │
│  - API key rotation                 │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│         Data Layer                  │
│  - Encryption at rest               │
│  - Encryption in transit (TLS)      │
│  - PII data protection              │
│  - FERPA compliance                 │
└─────────────────────────────────────┘
```

## Future Enhancements

### Phase 2: Voice Interface (ADA Integration)
```
Qwestian speaks → ADA hears → Companions respond → ADA speaks
```

### Phase 3: VR/AR Learning Spaces
```
Qwestians enter immersive learning environments
Companions appear as 3D avatars
Quest-based exploration of concepts
```

### Phase 4: Parent/Teacher Portal
```
Real-time progress monitoring
Companion interaction insights
Learning pattern analysis
Intervention recommendations
```

## Conclusion

The LearnQwest™ visual workflow creates a complete educational ecosystem where:

1. **Content flows in** through intake zones (ions)
2. **Qwest-ions™** are generated and stored
3. **Qwestians™** embark on learning journeys
4. **8 AI Companions** guide and support
5. **Community** forms (Qwestian Nation)
6. **Achievements** unlock and motivate
7. **Reflection** consolidates learning

Every component is designed to support the core mission: **transforming students into heroic learners** on an epic quest for knowledge.

---

**Created:** 2025-11-19
**Author:** Christian "Link" Lindquist
**Brand:** LearnQwest™ with Qwestians™
**Philosophy:** Every Qwestian is a Hero
**Architecture:** Ion-Based + RAGENTS Orchestration
