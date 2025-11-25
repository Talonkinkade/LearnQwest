# Omnisearch Qwest-ion

**🔍 Multi-Source Educational Content Discovery Agent**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/learnqwest/qwest-ions/omnisearch)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Bun](https://img.shields.io/badge/Bun-1.0-orange.svg)](https://bun.sh/)

Omnisearch is a specialized Qwest-ion agent that discovers educational content by searching 8 sources simultaneously: YouTube, Google, Scholar, Khan Academy, Reddit, Stack Overflow, Wikipedia, and Arxiv. Returns 30-50 curated, relevant results in under 10 seconds.

---

## 🚀 Features

- **🔥 Blazing Fast**: 8 parallel searches complete in <10 seconds
- **🎯 Smart Ranking**: AI-powered relevance scoring with educational content boost
- **🛠️ Production Ready**: >95% success rate with comprehensive error handling
- **📊 Token Optimized**: <3k token responses for efficient LLM processing
- **🔧 CLI-First**: Direct command-line usage or programmatic API
- **☁️ E2B Compatible**: Ready for serverless sandbox deployment
- **📈 Observable**: Comprehensive logging and performance metrics

### Supported Sources

| Source | Type | Max Results | Content Focus |
|--------|------|-------------|---------------|
| 🎥 **YouTube** | Video | 10 | Educational videos, tutorials |
| 🌐 **Google** | Web | 10 | Articles, blog posts, guides |
| 📚 **Scholar** | Academic | 5 | Research papers, citations |
| 🎓 **Khan Academy** | Educational | 5 | Structured lessons |
| 💬 **Reddit** | Discussion | 5 | Community insights |
| ❓ **Stack Overflow** | Q&A | 5 | Technical solutions |
| 📖 **Wikipedia** | Reference | 3 | Encyclopedia articles |
| 📄 **Arxiv** | Research | 5 | Preprint papers |

---

## 📦 Installation

### Prerequisites

- [Bun](https://bun.sh/) v1.0+
- Node.js v18+ (fallback)
- API keys for search services

### Quick Start

```bash
# Clone repository
git clone https://github.com/learnqwest/qwest-ions
cd qwest-ions/omnisearch

# Install dependencies
bun install

# Configure API keys (see Configuration section)
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Test installation
bun run src/index.ts --query "test search"
```

### Global Installation

```bash
# Install globally
bun install -g @learnqwest/omnisearch

# Use from anywhere
omnisearch --query "quadratic equations" --subject "math"
```

---

## ⚙️ Configuration

### API Keys Required

Create accounts and obtain API keys for:

1. **YouTube Data API**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Google Custom Search**: [Custom Search Engine](https://cse.google.com/)
3. **SerpApi** (for Scholar): [serpapi.com](https://serpapi.com/)
4. **Reddit API**: [Reddit Apps](https://www.reddit.com/prefs/apps)
5. **Stack Exchange API**: [stackapps.com](https://stackapps.com/)

### Environment Variables

```bash
# Create .env file
cat > .env << EOF
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
SERPAPI_KEY=your_serpapi_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
EOF
```

### Configuration File

Edit `config.yaml` to customize behavior:

```yaml
# Example configuration
execution:
  parallel: true
  overall_timeout_ms: 10000
  max_results: 40

ranking:
  boost_educational: true
  boost_recent: true
  diversity_weight: 0.3

tools:
  youtube:
    enabled: true
    max_results: 10
  google:
    enabled: true
    max_results: 10
  # ... etc
```

---

## 🎯 Usage

### Command Line Interface

```bash
# Basic search
omnisearch --query "machine learning basics"

# With filters
omnisearch \
  --query "photosynthesis" \
  --grade-level "5th grade" \
  --subject "science" \
  --max-results 30

# Specific content types
omnisearch \
  --query "python programming" \
  --content-types "video,article" \
  --timeout 15000
```

### Programmatic API

```typescript
import { search } from '@learnqwest/omnisearch';

// Basic usage
const results = await search({
  query: "quantum mechanics for beginners",
  grade_level: "high school",
  subject: "physics"
});

console.log(`Found ${results.metadata.total_found} results`);
results.results.forEach(result => {
  console.log(`${result.title} (${result.source})`);
});
```

### HTTP API

```bash
# Start server
bun run server

# Make requests
curl -X POST http://localhost:3000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "calculus derivatives",
    "grade_level": "college",
    "max_results": 25
  }'
```

### Response Format

```json
{
  "query": "machine learning basics",
  "results": [
    {
      "title": "Machine Learning Explained",
      "url": "https://youtube.com/watch?v=abc123",
      "source": "youtube",
      "type": "video",
      "relevance_score": 0.95,
      "metadata": {
        "channel": "3Blue1Brown",
        "duration": "15:32",
        "views": 2500000
      }
    }
    // ... 29-49 more results
  ],
  "metadata": {
    "total_found": 42,
    "execution_time_ms": 8234,
    "sources_used": ["youtube", "google", "scholar", "khan", "wikipedia"],
    "success_rate": 0.97
  }
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Omnisearch Agent                        │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface  │  HTTP API  │  Programmatic API               │
├─────────────────┴─────┬──────┴──────────────────────────────────┤
│                       │                                         │
│        Main Orchestrator (src/index.ts)                        │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│                       │                                         │
│     Parallel Execution Engine (src/orchestrator.ts)            │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│                       │                                         │
│  ┌─────────────────┐  │  ┌─────────────────┐                   │
│  │  CLI Tools      │◄─┼──┤  Individual     │                   │
│  │  (8 executables)│  │  │  Tool Spawning  │                   │
│  └─────────────────┘  │  └─────────────────┘                   │
│                       │                                         │
│  youtube-search  ──┬──┼──┐                                      │
│  google-search   ──┼──┼──┤                                      │
│  scholar-search  ──┼──┼──┤ Promise.allSettled()                │
│  khan-search     ──┼──┼──┤ (Parallel Execution)                │
│  reddit-search   ──┼──┼──┤                                      │
│  stackoverflow  ─────┼──┤                                      │
│  wikipedia-search ──┼──┼──┤                                      │
│  arxiv-search   ─────┴──┼──┘                                      │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│                       │                                         │
│        Result Aggregation & Ranking (src/ranker.ts)            │
│                       │                                         │
│  • Relevance Scoring  │  • Educational Boost                   │
│  • Deduplication      │  • Diversity Balancing                 │
│  • Content Type Mix   │  • Recency Scoring                     │
│                       │                                         │
├───────────────────────┼─────────────────────────────────────────┤
│                       │                                         │
│                 JSON Response                                   │
│             (30-50 curated results)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input Validation**: Query and options validated via Zod schemas
2. **Parallel Execution**: 8 CLI tools spawn simultaneously
3. **Individual Timeouts**: Each tool has 2-3 second timeout
4. **Result Collection**: Successful responses aggregated
5. **Smart Ranking**: AI-powered relevance scoring applied
6. **Deduplication**: Remove duplicate URLs and similar content
7. **Diversity Balancing**: Ensure mix of sources and content types
8. **JSON Output**: Structured response with metadata

---

## 🧪 Testing

### Run Test Suite

```bash
# All tests
bun test

# Specific test files
bun test tests/integration.test.ts
bun test tests/tools.test.ts

# With coverage
bun test --coverage

# Watch mode (development)
bun test --watch
```

### Test Individual Tools

```bash
# Test YouTube search
./tools/cli/youtube-search --query "calculus" --max-results 5

# Test all tools
bun run test:tools
```

### Integration Testing

```bash
# Full end-to-end test
bun run test:integration

# Performance benchmarks
bun run benchmark
```

### Mock Mode

For development without API keys:

```bash
# Enable mock responses
export OMNISEARCH_MOCK=true
bun run src/index.ts --query "test"
```

---

## ☁️ Deployment

### E2B Sandboxes

```bash
# Install E2B CLI
npm install -g @e2b/cli

# Login to E2B
e2b auth login

# Deploy sandbox
e2b template build

# Test deployment
e2b sandbox create learnqwest-omnisearch --cmd "omnisearch --query 'test'"
```

### Docker

```bash
# Build image
docker build -t omnisearch .

# Run container
docker run -e YOUTUBE_API_KEY=xxx omnisearch --query "docker tutorial"
```

### Serverless

```bash
# Deploy to Vercel
vercel deploy

# Deploy to Netlify
netlify deploy --prod

# Deploy to AWS Lambda
serverless deploy
```

---

## 🔧 Troubleshooting

### Common Issues

**"API key not found" Error**
```bash
# Check environment variables
env | grep -E "(YOUTUBE|GOOGLE|SERPAPI|REDDIT)_"

# Verify config.yaml
cat config.yaml | grep -A5 "api_key_env"
```

**Timeout Errors**
```bash
# Increase timeout
omnisearch --query "search" --timeout 20000

# Check individual tools
./tools/cli/youtube-search --query "test" --verbose
```

**Low Success Rate**
```bash
# Enable debug logging
export LOG_LEVEL=debug
omnisearch --query "search"

# Check tool permissions
chmod +x tools/cli/*
```

**Memory Issues**
```bash
# Reduce max results
omnisearch --query "search" --max-results 20

# Monitor memory usage
bun --heap-prof src/index.ts --query "search"
```

### Performance Optimization

```bash
# Profile execution
bun --prof src/index.ts --query "search"

# Memory analysis
bun --inspect src/index.ts --query "search"

# Enable caching
export OMNISEARCH_CACHE=true
```

### Debug Mode

```bash
# Full debug output
DEBUG=omnisearch:* omnisearch --query "debug test"

# Save request/response logs
SAVE_REQUESTS=true omnisearch --query "test"
```

---

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/omnisearch
cd omnisearch

# Install dev dependencies
bun install --dev

# Run in development mode
bun --watch src/index.ts --query "dev test"
```

### Code Style

```bash
# Format code
bun run format

# Lint code
bun run lint

# Type check
bun run typecheck
```

### Adding New Search Sources

1. Create CLI tool in `tools/cli/newsource-search`
2. Add configuration in `config.yaml`
3. Update types in `src/types.ts`
4. Add to orchestrator in `src/orchestrator.ts`
5. Write tests in `tests/tools.test.ts`

### Pull Request Process

1. Create feature branch: `git checkout -b feature/new-source`
2. Make changes and add tests
3. Run full test suite: `bun test`
4. Update documentation
5. Submit pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙋‍♀️ Support

- **Documentation**: [docs.learnqwest.com/omnisearch](https://docs.learnqwest.com/omnisearch)
- **Issues**: [GitHub Issues](https://github.com/learnqwest/qwest-ions/issues)
- **Discord**: [LearnQwest Community](https://discord.gg/learnqwest)
- **Email**: support@learnqwest.com

---

## 🎉 Acknowledgments

- Built with [Bun](https://bun.sh/) for maximum performance
- Follows [BMAD](https://bmad.ai/) principles for production deployment
- Part of the [LearnQwest](https://learnqwest.com/) educational ecosystem
- Inspired by the need for comprehensive educational content discovery

---

**Made with ❤️ by the LearnQwest Team**

[![LearnQwest](https://img.shields.io/badge/LearnQwest-Education%20AI-blue.svg)](https://learnqwest.com/)