/**
 * Result Ranking and Deduplication Module
 * Ranks search results by relevance, diversity, and quality
 */

import type { SearchResult, OmnisearchInput, Config } from "./types.js";

/**
 * Ranks and deduplicates search results based on relevance and diversity
 */
export function rankResults(
  results: SearchResult[],
  input: OmnisearchInput,
  config: Config
): SearchResult[] {
  // Step 1: Deduplicate by URL (case-insensitive)
  const deduplicatedResults = deduplicateResults(results);

  // Step 2: Calculate relevance scores
  const scoredResults = deduplicatedResults.map(result => ({
    ...result,
    relevance_score: calculateRelevanceScore(result, input, config)
  }));

  // Step 3: Apply diversity weighting
  const diversifiedResults = applyDiversityWeighting(scoredResults, config);

  // Step 4: Sort by final score and return top N
  return diversifiedResults
    .sort((a, b) => b.relevance_score - a.relevance_score)
    .slice(0, config.execution.max_results);
}

/**
 * Removes duplicate results based on URL (case-insensitive)
 */
function deduplicateResults(results: SearchResult[]): SearchResult[] {
  const seen = new Set<string>();
  const deduplicated: SearchResult[] = [];

  for (const result of results) {
    const normalizedUrl = normalizeUrl(result.url);
    if (!seen.has(normalizedUrl)) {
      seen.add(normalizedUrl);
      deduplicated.push(result);
    }
  }

  return deduplicated;
}

/**
 * Normalizes URL for deduplication (removes query params, fragments, etc.)
 */
function normalizeUrl(url: string): string {
  try {
    const parsed = new URL(url);
    // Remove query parameters and fragments for better deduplication
    return `${parsed.protocol}//${parsed.hostname}${parsed.pathname}`.toLowerCase();
  } catch {
    return url.toLowerCase();
  }
}

/**
 * Calculates relevance score for a single result
 */
function calculateRelevanceScore(
  result: SearchResult,
  input: OmnisearchInput,
  config: Config
): number {
  let score = 0;

  // Base score from query matching
  score += calculateQueryMatchScore(result, input.query);

  // Source credibility boost
  score += calculateSourceCredibilityScore(result.source, config);

  // Content type preference
  score += calculateContentTypeScore(result, input);

  // Educational content boost
  if (config.ranking.boost_educational) {
    score += calculateEducationalScore(result);
  }

  // Recency boost
  if (config.ranking.boost_recent) {
    score += calculateRecencyScore(result);
  }

  // Normalize to 0-1 range
  return Math.min(1.0, Math.max(0.0, score));
}

/**
 * Calculates how well the result matches the search query
 */
function calculateQueryMatchScore(result: SearchResult, query: string): number {
  const queryTerms = query.toLowerCase().split(/\s+/);
  const title = result.title.toLowerCase();
  
  let matches = 0;
  let exactMatches = 0;

  for (const term of queryTerms) {
    if (title.includes(term)) {
      matches++;
      // Bonus for exact word matches vs partial matches
      if (title.match(new RegExp(`\\b${term}\\b`))) {
        exactMatches++;
      }
    }
  }

  const matchRatio = matches / queryTerms.length;
  const exactRatio = exactMatches / queryTerms.length;

  // Base score from matches + bonus for exact matches
  return (matchRatio * 0.3) + (exactRatio * 0.2);
}

/**
 * Assigns credibility scores based on source reliability
 */
function calculateSourceCredibilityScore(source: string, config: Config): number {
  const credibilityMap: Record<string, number> = {
    khan: 0.25,        // High educational credibility
    scholar: 0.20,     // Academic papers
    wikipedia: 0.15,   // Generally reliable
    youtube: 0.10,     // Variable quality but popular
    google: 0.10,      // Web results, mixed quality
    stackoverflow: 0.08, // Good for technical topics
    arxiv: 0.15,       // Academic preprints
    reddit: 0.05       // Community discussions
  };

  return credibilityMap[source] || 0.05;
}

/**
 * Scores results based on preferred content types
 */
function calculateContentTypeScore(result: SearchResult, input: OmnisearchInput): number {
  if (!input.content_types || input.content_types.length === 0) {
    return 0.05; // Small default boost
  }

  return input.content_types.includes(result.type) ? 0.15 : 0;
}

/**
 * Boosts educational content based on metadata
 */
function calculateEducationalScore(result: SearchResult): number {
  const educationalKeywords = [
    'tutorial', 'lesson', 'learn', 'education', 'course', 'academy',
    'university', 'school', 'teaching', 'guide', 'introduction'
  ];

  const title = result.title.toLowerCase();
  const matchCount = educationalKeywords.filter(keyword => 
    title.includes(keyword)
  ).length;

  // Additional boost for educational sources
  const sourceBoost = ['khan', 'scholar', 'arxiv'].includes(result.source) ? 0.05 : 0;

  return Math.min(0.15, matchCount * 0.03) + sourceBoost;
}

/**
 * Boosts more recent content
 */
function calculateRecencyScore(result: SearchResult): number {
  try {
    // Try to extract date from metadata
    const dateFields = ['published_at', 'published', 'date', 'year'];
    let publishDate: Date | null = null;

    for (const field of dateFields) {
      if (result.metadata[field]) {
        const dateValue = result.metadata[field];
        if (typeof dateValue === 'number') {
          // Year only
          publishDate = new Date(dateValue, 0, 1);
        } else if (typeof dateValue === 'string') {
          publishDate = new Date(dateValue);
        }
        
        if (publishDate && !isNaN(publishDate.getTime())) {
          break;
        }
      }
    }

    if (!publishDate || isNaN(publishDate.getTime())) {
      return 0; // No valid date found
    }

    const now = new Date();
    const ageInYears = (now.getTime() - publishDate.getTime()) / (1000 * 60 * 60 * 24 * 365);

    // Boost recent content (less than 2 years old gets boost)
    if (ageInYears < 0.5) return 0.1;  // Very recent (6 months)
    if (ageInYears < 1) return 0.07;   // Recent (1 year)
    if (ageInYears < 2) return 0.05;   // Somewhat recent (2 years)
    
    return 0; // Older content gets no recency boost
  } catch {
    return 0; // Error parsing date
  }
}

/**
 * Applies diversity weighting to ensure variety across sources
 */
function applyDiversityWeighting(
  results: SearchResult[],
  config: Config
): SearchResult[] {
  if (config.ranking.diversity_weight === 0) {
    return results;
  }

  // Count results per source
  const sourceCounts = new Map<string, number>();
  for (const result of results) {
    sourceCounts.set(result.source, (sourceCounts.get(result.source) || 0) + 1);
  }

  // Apply diversity penalty to over-represented sources
  return results.map(result => {
    const sourceCount = sourceCounts.get(result.source) || 1;
    
    // Penalty increases with source over-representation
    let diversityPenalty = 0;
    if (sourceCount > 3) {
      diversityPenalty = (sourceCount - 3) * config.ranking.diversity_weight * 0.1;
    }

    return {
      ...result,
      relevance_score: Math.max(0, result.relevance_score - diversityPenalty)
    };
  });
}

/**
 * Utility function to debug ranking scores
 */
export function debugRankingScores(
  results: SearchResult[],
  input: OmnisearchInput,
  config: Config
): Array<{ result: SearchResult; scoreBreakdown: Record<string, number> }> {
  return results.map(result => {
    const scoreBreakdown = {
      queryMatch: calculateQueryMatchScore(result, input.query),
      sourceCredibility: calculateSourceCredibilityScore(result.source, config),
      contentType: calculateContentTypeScore(result, input),
      educational: config.ranking.boost_educational ? calculateEducationalScore(result) : 0,
      recency: config.ranking.boost_recent ? calculateRecencyScore(result) : 0
    };

    return {
      result,
      scoreBreakdown
    };
  });
}