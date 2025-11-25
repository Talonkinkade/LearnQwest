# Content Fetcher Ion

**Type:** Content Extraction  
**Method:** BMAD  
**Status:** Operational

## Purpose

Extracts content from YouTube videos and web pages for analysis and processing.

## Capabilities

- YouTube video transcript extraction
- Web page content scraping
- Metadata extraction (title, author, duration, etc.)
- Clean HTML parsing
- Timestamp preservation

## Input Schema

```typescript
{
  url: string,              // YouTube URL or web URL
  source_type?: string,     // "youtube" | "web" | "auto"
  include_metadata?: boolean,
  include_timestamps?: boolean,
  max_length?: number
}
```

## Output Schema

```typescript
{
  success: boolean,
  result: {
    url: string,
    source_type: string,
    title: string,
    content: string,
    metadata: {
      author?: string,
      duration?: number,
      published_date?: string,
      description?: string
    },
    timestamps?: Array<{
      time: number,
      text: string
    }>,
    word_count: number,
    extracted_at: string
  },
  metrics: {
    execution_time_ms: number,
    content_length: number,
    source: string
  }
}
```

## Usage

```bash
# Extract YouTube transcript
bun run src/index.ts --url "https://youtube.com/watch?v=..."

# Extract web content
bun run src/index.ts --url "https://example.com/article"

# With options
bun run src/index.ts --url "..." --include-metadata --include-timestamps
```

## BMAD Workflow

1. **Build:** Parse URL and determine source type
2. **Measure:** Track extraction time and content length
3. **Analyze:** Validate content quality and completeness
4. **Deploy:** Return structured content with metadata

## Dependencies

- None (uses native fetch and text parsing)
- Future: youtube-transcript, cheerio for enhanced extraction

## Performance

- YouTube: ~500-2000ms (depends on transcript length)
- Web: ~200-1000ms (depends on page size)
- Success rate: 95%+ (with proper URLs)

## Error Handling

- Invalid URL format
- Content not accessible
- Transcript not available
- Timeout exceeded
- Content too large

## Future Enhancements

- Support for more video platforms (Vimeo, etc.)
- PDF content extraction
- Image OCR extraction
- Audio transcription
- Multi-language support
