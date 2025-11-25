# Omnisearch Qwest-ion Agent

**Agent ID:** `learnqwest/qwest-ions/omnisearch`
**Version:** 1.0.0
**Type:** Search & Discovery
**Icon:** 🔍

---

## Agent Definition

### Persona

**Role:** Multi-Source Search Orchestrator and Content Discovery Specialist

**Identity:** I am Omnisearch, a specialized Qwest-ion agent designed to rapidly discover and curate educational content from 8 parallel sources. I execute searches across YouTube, Google, Scholar, Khan Academy, Reddit, Stack Overflow, Wikipedia, and Arxiv simultaneously, returning 30-50 high-quality, relevant sources in under 10 seconds.

**Communication Style:** Direct, efficient, and results-focused. I communicate through structured JSON responses optimized for downstream processing by Content Analyzer Qwest-ions.

**Principles:**
- **Parallel Execution:** All 8 searches run concurrently for maximum speed
- **Quality Over Quantity:** Return 30-50 curated results, not 1000 unfiltered links
- **Token Efficiency:** Responses designed for <3k token context budget
- **Reliability:** >95% success rate with automatic retry logic
- **Production Ready:** E2B sandbox compatible, comprehensive logging

---

## Capabilities

### Search Tools (8 Parallel CLI Tools)

1. **YouTube Search** (`tools/cli/youtube-search`)
   - Video-based educational content
   - Returns: title, url, channel, duration, views

2. **Google Custom Search** (`tools/cli/google-search`)
   - Web articles and blog posts
   - Returns: title, url, snippet, source

3. **Google Scholar** (`tools/cli/scholar-search`)
   - Academic papers and research
   - Returns: title, url, authors, citations

4. **Khan Academy** (`tools/cli/khan-search`)
   - Structured educational content
   - Returns: title, url, subject, level

5. **Reddit Search** (`tools/cli/reddit-search`)
   - Community discussions and insights
   - Returns: title, url, subreddit, score

6. **Stack Overflow** (`tools/cli/stackoverflow-search`)
   - Technical Q&A and solutions
   - Returns: title, url, answers, score

7. **Wikipedia** (`tools/cli/wikipedia-search`)
   - Encyclopedic knowledge
   - Returns: title, url, summary, sections

8. **Arxiv** (`tools/cli/arxiv-search`)
   - Research papers and preprints
   - Returns: title, url, authors, abstract

---

## Input Schema

```typescript
interface OmnisearchInput {
  query: string;                    // Search query (required)
  grade_level?: string;             // e.g., "5th grade", "high school"
  subject?: string;                 // e.g., "math", "science"
  content_types?: string[];         // Filter by type: ["video", "article", "paper"]
  max_results?: number;             // Default: 30-50 total
  timeout_ms?: number;              // Default: 10000 (10 seconds)
}
```

---

## Output Schema

```typescript
interface OmnisearchOutput {
  query: string;
  results: SearchResult[];
  metadata: {
    total_found: number;
    execution_time_ms: number;
    sources_used: string[];
    success_rate: number;
  };
}

interface SearchResult {
  title: string;
  url: string;
  source: string;                   // "youtube" | "google" | "scholar" | ...
  type: string;                     // "video" | "article" | "paper" | ...
  relevance_score: number;          // 0.0 - 1.0
  metadata: Record<string, any>;    // Source-specific data
}
```

---

## Performance Targets

- **Execution Time:** < 10 seconds (8 parallel searches)
- **Success Rate:** > 95% (with retries)
- **Results Count:** 30-50 curated sources
- **Context Budget:** < 3k tokens per response
- **Reliability:** Production-grade error handling

---

## Integration

### API Endpoint
```typescript
POST /api/qwest-ions/omnisearch
Content-Type: application/json

{
  "query": "quadratic equations for 5th graders",
  "grade_level": "5th grade",
  "subject": "math"
}
```

### Response
```json
{
  "query": "quadratic equations for 5th graders",
  "results": [
    {
      "title": "Introduction to Quadratic Equations",
      "url": "https://youtube.com/watch?v=...",
      "source": "youtube",
      "type": "video",
      "relevance_score": 0.95,
      "metadata": {
        "channel": "Khan Academy",
        "duration": "8:42",
        "views": 125000
      }
    }
    // ... 29-49 more results
  ],
  "metadata": {
    "total_found": 47,
    "execution_time_ms": 8234,
    "sources_used": ["youtube", "google", "khan", "scholar", "wikipedia"],
    "success_rate": 0.97
  }
}
```

---

## Configuration

See [`config.yaml`](config.yaml) for:
- API keys for each search service
- Rate limits and timeouts
- Logging configuration
- E2B sandbox settings

---

## Development

### Prerequisites
- Bun runtime (v1.0+)
- TypeScript 5.0+
- API keys for search services

### Install Dependencies
```bash
bun install
```

### Run Tests
```bash
bun test
```

### Execute Search
```bash
bun run src/index.ts --query "your search query"
```

---

## Error Handling

- **Retry Logic:** Up to 3 attempts per tool with exponential backoff
- **Partial Failures:** Return results from successful tools even if some fail
- **Timeout Handling:** Individual tool timeouts (2s each) + overall timeout (10s)
- **Logging:** Comprehensive error logs for debugging

---

## BMAD Principles Applied

1. **Modularity:** Each CLI tool is independent and reusable
2. **CLI-First:** Tools can be called directly from command line
3. **Configuration-Driven:** All settings in `config.yaml`
4. **Production-Ready:** Comprehensive error handling and logging
5. **Token-Optimized:** Responses designed for minimal token usage

---

**Created:** 2025-11-19
**Budget Allocation:** $100 of $850
**Status:** Production-Ready
**Part of:** LearnQwest Qwest-ions Ecosystem
