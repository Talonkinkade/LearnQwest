/**
 * Quality Assessment Qwest-ion Types
 * Type definitions for educational content quality scoring
 */

import { z } from "zod";

// ============================================================================
// Input Schemas
// ============================================================================

export const ContentItemSchema = z.object({
  id: z.string(),
  title: z.string(),
  url: z.string().url(),
  source: z.enum(["youtube", "google", "scholar", "khan", "reddit",
                  "stackoverflow", "wikipedia", "arxiv"]),
  type: z.enum(["video", "article", "paper", "discussion", "wiki", "qa", "code"]),

  // Basic metadata
  author: z.string().optional(),
  channel: z.string().optional(),
  published_date: z.string().optional(),
  description: z.string().optional(),

  // Engagement metrics
  views: z.number().optional(),
  likes: z.number().optional(),
  comments: z.number().optional(),
  shares: z.number().optional(),

  // Credibility signals
  verified: z.boolean().optional(),
  citations: z.number().optional(),
  author_followers: z.number().optional(),

  // Educational metadata
  grade_level: z.string().optional(),
  subject: z.string().optional(),
  topics: z.array(z.string()).optional(),
  duration: z.string().optional(), // "10:32" for videos

  // Production quality indicators
  has_captions: z.boolean().optional(),
  has_visuals: z.boolean().optional(),
  audio_quality: z.enum(["low", "medium", "high"]).optional(),

  // Additional metadata (for tool results)
  metadata: z.record(z.any()).optional(),
});

export type ContentItem = z.infer<typeof ContentItemSchema>;

// ============================================================================
// Quality Assessment Schemas
// ============================================================================

export const DimensionScoreSchema = z.object({
  dimension: z.enum(["credibility", "accuracy", "production", "educational", "engagement"]),
  score: z.number().min(0).max(100),
  weight: z.number().min(0).max(1),
  weighted_score: z.number().min(0).max(100),
  confidence: z.number().min(0).max(1),
  signals: z.array(z.object({
    indicator: z.string(),
    value: z.union([z.string(), z.number(), z.boolean()]),
    impact: z.enum(["positive", "negative", "neutral"]),
  })),
});

export type DimensionScore = z.infer<typeof DimensionScoreSchema>;

export const QualityAssessmentSchema = z.object({
  item: ContentItemSchema,
  dimensions: z.array(DimensionScoreSchema),
  overall_score: z.number().min(0).max(100),
  passed: z.boolean(),
  threshold: z.number().min(0).max(100),
  assessed_at: z.string(),
  assessment_version: z.string(),
});

export type QualityAssessment = z.infer<typeof QualityAssessmentSchema>;

// ============================================================================
// Batch Assessment Schemas
// ============================================================================

export const BatchAssessmentInputSchema = z.object({
  items: z.array(ContentItemSchema),
  threshold: z.number().min(0).max(100).default(70),
  mode: z.enum(["production", "testing", "strict"]).optional().default("production"),
  dimension_thresholds: z.object({
    credibility: z.number().min(0).max(100).optional(),
    accuracy: z.number().min(0).max(100).optional(),
    production: z.number().min(0).max(100).optional(),
    educational: z.number().min(0).max(100).optional(),
    engagement: z.number().min(0).max(100).optional(),
  }).optional(),
});

export type BatchAssessmentInput = z.infer<typeof BatchAssessmentInputSchema>;

export const BatchAssessmentOutputSchema = z.object({
  total_assessed: z.number(),
  passed: z.array(QualityAssessmentSchema),
  failed: z.array(QualityAssessmentSchema),
  statistics: z.object({
    pass_rate: z.number().min(0).max(1),
    avg_score: z.number().min(0).max(100),
    avg_by_dimension: z.record(z.number()),
    execution_time_ms: z.number(),
    items_per_second: z.number(),
  }),
  assessed_at: z.string(),
  mode: z.string(),
});

export type BatchAssessmentOutput = z.infer<typeof BatchAssessmentOutputSchema>;

// ============================================================================
// Configuration Schemas
// ============================================================================

export const QualityConfigSchema = z.object({
  agent: z.object({
    id: z.string(),
    name: z.string(),
    version: z.string(),
    description: z.string(),
  }),

  modes: z.object({
    production: z.object({
      overall: z.number().min(0).max(100),
      dimensions: z.object({
        credibility: z.number().min(0).max(100),
        accuracy: z.number().min(0).max(100),
        production: z.number().min(0).max(100),
        educational: z.number().min(0).max(100),
        engagement: z.number().min(0).max(100),
      }),
    }),
    testing: z.object({
      overall: z.number().min(0).max(100),
      dimensions: z.object({
        credibility: z.number().min(0).max(100),
        accuracy: z.number().min(0).max(100),
        production: z.number().min(0).max(100),
        educational: z.number().min(0).max(100),
        engagement: z.number().min(0).max(100),
      }),
    }),
    strict: z.object({
      overall: z.number().min(0).max(100),
      dimensions: z.object({
        credibility: z.number().min(0).max(100),
        accuracy: z.number().min(0).max(100),
        production: z.number().min(0).max(100),
        educational: z.number().min(0).max(100),
        engagement: z.number().min(0).max(100),
      }),
    }),
  }),

  weights: z.object({
    credibility: z.number().min(0).max(1),
    accuracy: z.number().min(0).max(1),
    production: z.number().min(0).max(1),
    educational: z.number().min(0).max(1),
    engagement: z.number().min(0).max(1),
  }),

  scoring: z.object({
    trusted_sources: z.array(z.string()),
    verified_authors: z.array(z.string()),
    trusted_channels: z.record(z.number()),
    min_citations_high_credibility: z.number(),
    min_views_high_engagement: z.number(),
    max_age_days_recent_boost: z.number(),
  }),

  performance: z.object({
    batch_size: z.number().int().positive(),
    max_concurrent: z.number().int().positive(),
  }),

  logging: z.object({
    level: z.enum(["debug", "info", "warn", "error"]),
    format: z.enum(["json", "text"]),
  }),
});

export type QualityConfig = z.infer<typeof QualityConfigSchema>;

// ============================================================================
// Scorer Interface
// ============================================================================

export interface Scorer {
  readonly dimension: "credibility" | "accuracy" | "production" | "educational" | "engagement";
  readonly weight: number;

  score(item: ContentItem, config: QualityConfig): Promise<DimensionScore>;
}

// ============================================================================
// Logger Types
// ============================================================================

export interface Logger {
  debug: (message: string, data?: any) => void;
  info: (message: string, data?: any) => void;
  warn: (message: string, data?: any) => void;
  error: (message: string, data?: any) => void;
}
