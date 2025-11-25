#!/usr/bin/env bun

import { parseArgs } from "util";
import { z } from "zod";

/**
 * Content Fetcher Ion - BMAD Method
 * Extracts content from YouTube videos and web pages
 */

// Input Schema
const InputSchema = z.object({
  url: z.string().url("Must be a valid URL"),
  source_type: z.enum(['youtube', 'web', 'auto']).optional().default('auto'),
  include_metadata: z.boolean().optional().default(true),
  include_timestamps: z.boolean().optional().default(false),
  max_length: z.number().optional().default(50000)
});

// Output Schema
const OutputSchema = z.object({
  success: z.boolean(),
  result: z.object({
    url: z.string(),
    source_type: z.string(),
    title: z.string(),
    content: z.string(),
    metadata: z.object({
      author: z.string().optional(),
      duration: z.number().optional(),
      published_date: z.string().optional(),
      description: z.string().optional()
    }).optional(),
    timestamps: z.array(z.object({
      time: z.number(),
      text: z.string()
    })).optional(),
    word_count: z.number(),
    extracted_at: z.string()
  }),
  metrics: z.object({
    execution_time_ms: z.number(),
    content_length: z.number(),
    source: z.string()
  })
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;

class ContentFetcher {
  /**
   * Fetch content from URL
   */
  async fetch(input: Input): Promise<Output> {
    const startTime = Date.now();

    try {
      // Determine source type
      const sourceType = this.determineSourceType(input.url, input.source_type);

      // Fetch based on source type
      let result;
      if (sourceType === 'youtube') {
        result = await this.fetchYouTube(input);
      } else {
        result = await this.fetchWeb(input);
      }

      const executionTime = Date.now() - startTime;

      return {
        success: true,
        result: {
          ...result,
          url: input.url,
          source_type: sourceType,
          word_count: this.countWords(result.content),
          extracted_at: new Date().toISOString()
        },
        metrics: {
          execution_time_ms: executionTime,
          content_length: result.content.length,
          source: sourceType
        }
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      throw new Error(`Content fetch failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Determine source type from URL
   */
  private determineSourceType(url: string, sourceType: string): 'youtube' | 'web' {
    if (sourceType !== 'auto') {
      return sourceType as 'youtube' | 'web';
    }

    // Check if YouTube URL
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return 'youtube';
    }

    return 'web';
  }

  /**
   * Fetch YouTube video content
   * Note: Simplified implementation - real version would use youtube-transcript
   */
  private async fetchYouTube(input: Input): Promise<{
    title: string;
    content: string;
    metadata?: any;
    timestamps?: any[];
  }> {
    // Extract video ID
    const videoId = this.extractYouTubeId(input.url);
    if (!videoId) {
      throw new Error('Invalid YouTube URL');
    }

    // Simulated YouTube fetch
    // In production, would use youtube-transcript package
    const title = `YouTube Video: ${videoId}`;
    const content = `[Simulated YouTube transcript for video ${videoId}]\n\nThis is a placeholder for the actual transcript content that would be fetched from YouTube. In production, this would use the youtube-transcript package to extract the actual video transcript with timestamps.`;

    const result: any = {
      title,
      content: content.slice(0, input.max_length)
    };

    if (input.include_metadata) {
      result.metadata = {
        author: "Channel Name",
        duration: 600,
        published_date: new Date().toISOString(),
        description: "Video description would go here"
      };
    }

    if (input.include_timestamps) {
      result.timestamps = [
        { time: 0, text: "Introduction" },
        { time: 30, text: "Main content starts" },
        { time: 300, text: "Key points discussed" },
        { time: 540, text: "Conclusion" }
      ];
    }

    return result;
  }

  /**
   * Fetch web page content
   */
  private async fetchWeb(input: Input): Promise<{
    title: string;
    content: string;
    metadata?: any;
  }> {
    try {
      // Fetch the page
      const response = await fetch(input.url, {
        headers: {
          'User-Agent': 'LearnQwest-ContentFetcher/1.0'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const html = await response.text();

      // Extract title
      const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
      const title = titleMatch ? titleMatch[1].trim() : 'Untitled';

      // Simple content extraction (remove HTML tags)
      let content = html
        .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
        .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      // Limit content length
      content = content.slice(0, input.max_length);

      const result: any = {
        title,
        content
      };

      if (input.include_metadata) {
        // Extract meta tags
        const descMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i);
        const authorMatch = html.match(/<meta[^>]*name=["']author["'][^>]*content=["']([^"']+)["']/i);

        result.metadata = {
          description: descMatch ? descMatch[1] : undefined,
          author: authorMatch ? authorMatch[1] : undefined
        };
      }

      return result;
    } catch (error) {
      throw new Error(`Web fetch failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Extract YouTube video ID from URL
   */
  private extractYouTubeId(url: string): string | null {
    // youtube.com/watch?v=VIDEO_ID
    let match = url.match(/[?&]v=([^&]+)/);
    if (match) return match[1];

    // youtu.be/VIDEO_ID
    match = url.match(/youtu\.be\/([^?]+)/);
    if (match) return match[1];

    return null;
  }

  /**
   * Count words in text
   */
  private countWords(text: string): number {
    return text.split(/\s+/).filter(word => word.length > 0).length;
  }
}

/**
 * CLI Entry Point
 */
async function main() {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      url: { type: 'string' },
      'source-type': { type: 'string' },
      'include-metadata': { type: 'boolean', default: true },
      'include-timestamps': { type: 'boolean', default: false },
      'max-length': { type: 'string' },
      verbose: { type: 'boolean', default: false },
      help: { type: 'boolean', default: false }
    },
    strict: true,
    allowPositionals: false
  });

  if (values.help) {
    console.log(`
Content Fetcher Ion - Extract content from URLs

Usage:
  bun run src/index.ts --url <url> [options]

Options:
  --url <url>              URL to fetch content from (required)
  --source-type <type>     Source type: youtube, web, auto (default: auto)
  --include-metadata       Include metadata (default: true)
  --include-timestamps     Include timestamps for YouTube (default: false)
  --max-length <number>    Maximum content length (default: 50000)
  --verbose                Verbose output
  --help                   Show this help

Examples:
  bun run src/index.ts --url "https://youtube.com/watch?v=..."
  bun run src/index.ts --url "https://example.com/article" --include-metadata
  bun run src/index.ts --url "..." --include-timestamps --verbose
`);
    process.exit(0);
  }

  if (!values.url) {
    console.error('Error: --url is required');
    console.error('Use --help for usage information');
    process.exit(1);
  }

  try {
    // Parse input
    const input = InputSchema.parse({
      url: values.url,
      source_type: values['source-type'] || 'auto',
      include_metadata: values['include-metadata'],
      include_timestamps: values['include-timestamps'],
      max_length: values['max-length'] ? parseInt(values['max-length']) : 50000
    });

    if (values.verbose) {
      console.error(`[ContentFetcher] Fetching: ${input.url}`);
      console.error(`[ContentFetcher] Source type: ${input.source_type}`);
    }

    // Execute
    const fetcher = new ContentFetcher();
    const output = await fetcher.fetch(input);

    // Validate output
    OutputSchema.parse(output);

    if (values.verbose) {
      console.error(`[ContentFetcher] Success: ${output.result.word_count} words`);
      console.error(`[ContentFetcher] Execution time: ${output.metrics.execution_time_ms}ms`);
    }

    // Output JSON
    console.log(JSON.stringify(output, null, 2));

  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('Validation error:', error.errors);
      process.exit(1);
    }

    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.main) {
  main();
}

export { ContentFetcher, InputSchema, OutputSchema };
export type { Input, Output };
