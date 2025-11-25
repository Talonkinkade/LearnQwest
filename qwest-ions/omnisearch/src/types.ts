/**
 * Omnisearch Qwest-ion Types
 * Type definitions for all data structures
 */

import { z } from "zod";

// ============================================================================
// Input Schemas
// ============================================================================

export const OmnisearchInputSchema = z.object({
  query: z.string().min(1, "Query cannot be empty"),
  grade_level: z.string().optional(),
  subject: z.string().optional(),
  content_types: z.array(z.enum(["video", "article", "paper", "discussion", "wiki"])).optional(),
  max_results: z.number().int().positive().default(40),
  timeout_ms: z.number().int().positive().default(10000),
});

export type OmnisearchInput = z.infer<typeof OmnisearchInputSchema>;

// ============================================================================
// Search Result Schemas
// ============================================================================

export const SearchResultSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  source: z.enum(["youtube", "google", "scholar", "khan", "reddit", "stackoverflow", "wikipedia", "arxiv"]),
  type: z.enum(["video", "article", "paper", "discussion", "wiki", "qa"]),
  relevance_score: z.number().min(0).max(1),
  metadata: z.record(z.any()),
});

export type SearchResult = z.infer<typeof SearchResultSchema>;

// ============================================================================
// Output Schemas
// ============================================================================

export const OmnisearchOutputSchema = z.object({
  query: z.string(),
  results: z.array(SearchResultSchema),
  metadata: z.object({
    total_found: z.number(),
    execution_time_ms: z.number(),
    sources_used: z.array(z.string()),
    success_rate: z.number().min(0).max(1),
  }),
});

export type OmnisearchOutput = z.infer<typeof OmnisearchOutputSchema>;

// ============================================================================
// Tool-Specific Result Types
// ============================================================================

export interface YouTubeResult {
  title: string;
  url: string;
  channel: string;
  duration: string;
  views: number;
  published_at: string;
}

export interface GoogleResult {
  title: string;
  url: string;
  snippet: string;
  source_domain: string;
}

export interface ScholarResult {
  title: string;
  url: string;
  authors: string[];
  citations: number;
  year: number;
}

export interface KhanResult {
  title: string;
  url: string;
  subject: string;
  level: string;
  duration: string;
}

export interface RedditResult {
  title: string;
  url: string;
  subreddit: string;
  score: number;
  num_comments: number;
}

export interface StackOverflowResult {
  title: string;
  url: string;
  answers: number;
  score: number;
  tags: string[];
}

export interface WikipediaResult {
  title: string;
  url: string;
  summary: string;
  sections: string[];
}

export interface ArxivResult {
  title: string;
  url: string;
  authors: string[];
  abstract: string;
  published: string;
}

// ============================================================================
// Tool Result Union Type
// ============================================================================

export type ToolResult =
  | YouTubeResult
  | GoogleResult
  | ScholarResult
  | KhanResult
  | RedditResult
  | StackOverflowResult
  | WikipediaResult
  | ArxivResult;

// ============================================================================
// Configuration Types
// ============================================================================

export interface ToolConfig {
  enabled: boolean;
  api_key_env?: string;
  max_results: number;
  timeout_ms: number;
  retry_attempts: number;
}

export interface Config {
  agent: {
    id: string;
    name: string;
    version: string;
    description: string;
  };
  tools: Record<string, ToolConfig>;
  execution: {
    parallel: boolean;
    overall_timeout_ms: number;
    min_results: number;
    max_results: number;
  };
  ranking: {
    boost_educational: boolean;
    boost_recent: boolean;
    diversity_weight: number;
  };
  logging: {
    level: "debug" | "info" | "warn" | "error";
    format: "json" | "text";
    output: "stdout" | "file";
    file: string | null;
  };
}

// ============================================================================
// Execution Types
// ============================================================================

export interface SearchToolResult {
  source: string;
  results: SearchResult[];
  execution_time_ms: number;
  success: boolean;
  error?: string;
}

export interface AggregatedResults {
  all_results: SearchResult[];
  by_source: Map<string, SearchResult[]>;
  total_count: number;
  successful_sources: string[];
  failed_sources: string[];
}

// ============================================================================
// Logger Types
// ============================================================================

export interface LogEntry {
  timestamp: string;
  level: "debug" | "info" | "warn" | "error";
  message: string;
  data?: any;
  source?: string;
}

export type LogFunction = (message: string, data?: any) => void;

export interface Logger {
  debug: LogFunction;
  info: LogFunction;
  warn: LogFunction;
  error: LogFunction;
}
