# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LearnQwest™** is LINK's lifelong learning and automation platform, building an AI-powered educational ecosystem with Qwest-ion agents following BMAD 6.0.0-alpha.7 patterns. The system extracts knowledge from expert sources (especially IndyDevDan's agent orchestration patterns), structures it into educational content, and deploys specialized AI agents for content discovery, analysis, and module generation.

**Key Philosophy:** Build systems that build you - this is not a side project but a permanent learning infrastructure.

---

## Architecture

### Dual Technology Stack

**Python Legacy System (agents/):**
- YouTube knowledge extraction pipeline
- Content conversion and search tools
- Knowledge base processing (31 IndyDevDan videos processed)

**TypeScript/Bun Qwest-ion Agents (qwest-ions/):**
- Modern BMAD-compliant agent implementations
- Production-ready with E2B sandbox deployment
- CLI-first design for token optimization

### Three-Phase Development Plan ($850 Budget)

**Phase 1: Core Agents ($300)** - Foundation layer
- ✅ Omnisearch Qwest-ion ($100) - Multi-source search across 8 platforms
- ⏳ Content Analyzers x3 ($150) - Quality, TEKS alignment, difficulty scoring
- ⏳ Module Generators x3 ($150) - Video, text, interactive content creation

**Phase 2: Orchestration ($250)** - Intelligence layer
- Quality Synthesizer ($50) - Merge best elements from parallel creators
- ADA Orchestrator ($200) - Master coordinator (Dan's pattern)

**Phase 3: Production ($300)** - Deployment layer
- E2B Integration ($100) - Sandbox deployment configs
- Testing Suite ($100) - Comprehensive test coverage
- Documentation ($100) - API docs and user guides

---

## Knowledge Base Structure

### BMAD 6.0.0-alpha.7 Official Templates
**Location:** `docs/orchestrated-v3.1/bmad-official/`
- 304 official BMAD methodology templates
- Agent definition structures, configuration patterns, tool implementations
- **Always reference these as the foundation for new agents**

### LearnQwest Knowledge Base
**Location:** `docs/orchestrated-v3.1/knowledge-base/`
- 780 files from 2 years of development work
- RAGEFORCE/RAGENTS patterns, YouTube learning content, core systems
- Domain expertise and proven approaches

### Context File for Claude Code
**Location:** `docs/orchestrated-v3.1/CLAUDE_CONTEXT.md`
- Load this file at the start of agent development sessions
- Contains tech stack, budget allocation, key references

---

## Common Development Commands

### Omnisearch Qwest-ion (TypeScript/Bun)

```bash
# Navigate to omnisearch agent
cd qwest-ions/omnisearch

# Install dependencies
bun install

# Development mode (watch for changes)
bun run dev

# Build for production
bun run build

# Run tests
bun test

# Run tests in watch mode
bun test --watch

# Type checking
bun run typecheck

# Lint code
bun run lint

# Format code
bun run format

# Execute search
bun run src/index.ts --query "your search query"

# Test individual search tool
./tools/cli/youtube-search --query "test" --max-results 5
```

### Python Agents (Legacy)

```bash
# Extract YouTube video transcript
python agents/extract_simple.py <video_url>

# Batch extract from ID list
python agents/extract_youtube_batch.py

# Convert VTT files to clean text
python agents/convert_to_txt.py

# Search processed videos
python agents/search_in_video.py "search term"
```

### Code Generation Scripts

```bash
# Generate codemap from codebase
python scripts/gen_codemap.py

# Generate quests from codemap
python scripts/gen_quests.py codemap_learnqwest.json

# Analyze codemap for gaps
python scripts/analyze_codemap_gaps.py
```

### Web Interfaces

```bash
# Start local web server for visualization tools
cd web
python -m http.server 8000

# Access tools:
# - http://localhost:8000/architect_wheel.html - Architect's Wheel (Commander/Lex)
# - http://localhost:8000/codemap-drawbridge.html - Code visualization
# - http://localhost:8000/index.html - Main interface
```

---

## Project Structure

```
LearnQwest/
│
├── qwest-ions/                         # BMAD-compliant TypeScript agents
│   └── omnisearch/                     # ✅ Multi-source search agent (COMPLETE)
│       ├── src/                        # TypeScript source
│       ├── tools/cli/                  # 8 search tool executables
│       ├── tests/                      # Test suites
│       └── package.json                # Bun dependencies
│
├── agents/                             # Python legacy extraction tools
│   ├── extract_simple.py               # YouTube transcript extraction
│   ├── convert_to_txt.py               # VTT → clean text conversion
│   ├── search_in_video.py              # Knowledge base search
│   └── extract_youtube_batch.py        # Batch processing
│
├── docs/orchestrated-v3.1/             # Master knowledge repository
│   ├── bmad-official/                  # 304 BMAD templates (FOUNDATION)
│   ├── knowledge-base/                 # 780 files of domain expertise
│   ├── CLAUDE_CONTEXT.md               # Load this for agent development
│   └── VICTORY_SUMMARY.md              # Battle plan and budget breakdown
│
├── processed_content/                  # Knowledge base (31 Dan videos)
│   └── indydevdan/
│       ├── raw/                        # Original VTT transcripts
│       └── txt/                        # Clean text versions
│
├── intake_zones/                       # Input dropzones
│   └── youtube_drop/
│       └── indydevdan_ids.txt          # Video IDs to process
│
├── web/                                # Visualization interfaces
│   ├── architect_wheel.html            # Agent orchestration UI
│   ├── codemap-drawbridge.html         # Code structure viewer
│   └── codemap_*.json                  # Generated codemaps
│
├── scripts/                            # Code generation utilities
│   ├── gen_codemap.py                  # Generate project maps
│   └── gen_quests.py                   # Generate learning quests
│
├── ada_orchestrator.py                 # [FUTURE] ADA orchestrator
├── quest_manager.py                    # Quest tracking system
└── README.md                           # Project overview
```

---

## BMAD Agent Development Pattern

When building new Qwest-ion agents, follow this structure:

### 1. Reference BMAD Templates First
```bash
# Always start by reviewing official templates
cat docs/orchestrated-v3.1/bmad-official/agent-architecture.md
cat docs/orchestrated-v3.1/bmad-official/agents-guide.md
```

### 2. Agent Directory Structure
```
qwest-ions/new-agent/
├── src/
│   ├── index.ts          # Main entry point
│   ├── orchestrator.ts   # Coordination logic
│   ├── types.ts          # Zod schemas
│   ├── config.ts         # Configuration
│   └── logger.ts         # Structured logging
├── tools/cli/            # CLI executables (if needed)
├── tests/
│   ├── index.test.ts     # Unit tests
│   └── integration.test.ts
├── package.json          # Bun dependencies
├── config.yaml           # Agent configuration
├── agent.md              # Agent definition
└── README.md             # Usage documentation
```

### 3. Core Principles
- **CLI-first:** Tools callable directly from command line
- **Token-optimized:** Design responses for <3k token context
- **Configuration-driven:** All settings in `config.yaml`
- **Production-ready:** Comprehensive error handling and logging
- **E2B compatible:** Sandbox deployment ready
- **Zod validation:** All inputs/outputs type-safe

### 4. Testing Requirements
- >90% code coverage target
- Unit tests for all core functions
- Integration tests for end-to-end flows
- Mock mode for development without API keys

---

## IndyDevDan's Core Patterns (Extracted from 31 Videos)

These patterns should inform all agent development:

### ADA Pattern (Agent Director & Orchestrator)
- Build one brain commanding many specialized agents
- Orchestrated systems, not individual scripts
- Clear separation: orchestrator vs. workers

### Multi-Provider Strategy
- Use Claude + OpenAI + Gemini simultaneously (AND not OR)
- Leverage strengths of each model
- Fallback chains for reliability

### Observability is Mandatory
- Always see what agents are doing in real-time
- Structured logging with context
- Performance metrics and success tracking

### Closed-Loop Validation
- Agents must test their own work
- Automatic quality assurance
- Iterative refinement until quality threshold met

### Structured Outputs
- Force JSON schemas with Zod
- Never accept unstructured responses
- Type safety throughout

---

## File Organization Notes

### Processed Content Location
YouTube transcripts from IndyDevDan stored in:
- **Raw:** `processed_content/indydevdan/raw/*.en.vtt`
- **Clean:** `processed_content/indydevdan/txt/*.txt`

### Video ID Management
Add new video IDs to extract:
```
intake_zones/youtube_drop/indydevdan_ids.txt
```

### Codemap Generation
Codemaps track project structure and generate learning quests:
- `web/codemap_learnqwest.json` - LearnQwest structure
- `web/codemap_rageforce.json` - Legacy RAGEFORCE patterns

---

## Development Workflow

### Building a New Qwest-ion Agent

1. **Load context:**
   ```bash
   cat docs/orchestrated-v3.1/CLAUDE_CONTEXT.md
   ```

2. **Review BMAD templates:**
   ```bash
   ls docs/orchestrated-v3.1/bmad-official/ | grep -i <agent-type>
   ```

3. **Create agent directory:**
   ```bash
   mkdir -p qwest-ions/<agent-name>/{src,tools/cli,tests}
   ```

4. **Follow omnisearch pattern:**
   - Copy structure from `qwest-ions/omnisearch/`
   - Implement core functionality in `src/`
   - Build CLI tools if needed
   - Write comprehensive tests

5. **Test thoroughly:**
   ```bash
   cd qwest-ions/<agent-name>
   bun test
   bun run typecheck
   bun run lint
   ```

6. **Document:**
   - Update `agent.md` with agent definition
   - Complete `README.md` with usage examples
   - Add to main project docs

### Processing New YouTube Content

1. **Add video IDs:**
   ```bash
   echo "VIDEO_ID_HERE" >> intake_zones/youtube_drop/indydevdan_ids.txt
   ```

2. **Extract transcripts:**
   ```bash
   python agents/extract_youtube_batch.py
   ```

3. **Convert to clean text:**
   ```bash
   python agents/convert_to_txt.py
   ```

4. **Search processed content:**
   ```bash
   python agents/search_in_video.py "agent orchestration"
   ```

---

## Budget Tracking

Current spend: $100 of $850 (Phase 1)

**Completed:**
- ✅ Omnisearch Qwest-ion - $100 (5,849 lines, production-ready)

**Remaining Phase 1:**
- Content Analyzer #1 (Quality Assessment) - $50
- Content Analyzer #2 (TEKS Alignment) - $50
- Content Analyzer #3 (Learning Difficulty) - $50
- Module Generator #1 (Video) - $50
- Module Generator #2 (Text) - $50
- Module Generator #3 (Interactive) - $50

**Future Phases:**
- Phase 2: Orchestration - $250
- Phase 3: Production - $300

---

## Important Notes

### BMAD Compliance
Every new Qwest-ion agent MUST follow BMAD 6.0.0-alpha.7 patterns found in `docs/orchestrated-v3.1/bmad-official/`. These are the official methodology templates and represent production-quality standards.

### Knowledge Base is Your Advantage
The `docs/orchestrated-v3.1/knowledge-base/` contains 2 years of development experience. Reference this for proven patterns before building from scratch.

### Bun Runtime
Qwest-ion agents use Bun for maximum performance. Ensure Bun v1.0+ is installed:
```bash
bun --version  # Should be 1.0.0 or higher
```

### E2B Sandbox Deployment
All agents designed for E2B sandbox deployment. Keep dependencies minimal and use CLI-first patterns for token efficiency.

### Dan's Wisdom
The 31 processed IndyDevDan videos contain the architectural patterns this system is built on. When in doubt about orchestration patterns, search these transcripts.

---

## Related Projects

This is part of LINK's broader Projects ecosystem but is NOT:
- ❌ A clone of RAGEFORCE (that's deprecated)
- ❌ A temporary experiment
- ❌ A side project

LearnQwest™ IS:
- ✅ LINK's permanent learning platform
- ✅ Built on Dan's proven patterns
- ✅ Production-focused from day one
- ✅ Designed for lifelong use

Other active projects in the ecosystem:
- **RAGEFORCE** - Multi-agent orchestration (separate, see `C:\Users\talon\OneDrive\Projects\RAGEFORCE`)
- **OM1** - Robotics/computer vision
- **ADA** - Always-on AI assistant (to integrate)

---

Last updated: November 19, 2025
