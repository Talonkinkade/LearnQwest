# Content Fetcher Ion

Extract content from YouTube videos and web pages for analysis.

## Installation

```bash
bun install
```

## Usage

```bash
# Extract YouTube transcript
bun run src/index.ts --url "https://youtube.com/watch?v=..."

# Extract web content
bun run src/index.ts --url "https://example.com/article"

# With options
bun run src/index.ts --url "..." --include-metadata --include-timestamps --verbose
```

## Features

- ✅ YouTube video content extraction
- ✅ Web page content extraction
- ✅ Metadata extraction (title, author, description)
- ✅ Timestamp support for YouTube
- ✅ Clean HTML parsing
- ✅ Configurable content length limits

## Output

```json
{
  "success": true,
  "result": {
    "url": "https://...",
    "source_type": "youtube",
    "title": "Video Title",
    "content": "Extracted content...",
    "metadata": {
      "author": "Channel Name",
      "duration": 600,
      "published_date": "2024-11-25T...",
      "description": "Video description"
    },
    "word_count": 1234,
    "extracted_at": "2024-11-25T..."
  },
  "metrics": {
    "execution_time_ms": 500,
    "content_length": 5000,
    "source": "youtube"
  }
}
```

## Status

✅ Operational (simulated YouTube, real web scraping)

## Future Enhancements

- Real YouTube transcript extraction (youtube-transcript package)
- Enhanced HTML parsing (cheerio package)
- PDF content extraction
- Multi-language support
