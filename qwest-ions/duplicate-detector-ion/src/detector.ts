import { createHash } from 'crypto';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import type {
  ScanResult,
  FileContent,
  DuplicateGroup,
  PatternGroup,
  Config,
} from './types';
import { logger } from './logger';

export class DuplicateDetector {
  private fileContents: Map<string, FileContent> = new Map();
  private lineHashes: Map<string, string[]> = new Map(); // hash -> file paths
  private similarityCache: Map<string, number> = new Map();

  constructor(private config: Config, private projectRoot: string) {}

  /**
   * Analyze scan results for duplicates
   */
  async analyze(scanResult: ScanResult): Promise<{
    duplicateGroups: DuplicateGroup[];
    patternGroups: PatternGroup[];
    filePathPatterns: Array<{ pattern: string; files: string[]; similarity: number }>;
  }> {
    logger.section('Duplicate Detection Analysis');

    // Step 1: Load all file contents
    await this.loadFileContents(scanResult);

    // Step 2: Detect exact duplicates
    logger.subsection('Detecting Exact Duplicates');
    const exactDuplicates = this.detectExactDuplicates();
    logger.success(`Found ${exactDuplicates.length} exact duplicate groups`);

    // Step 3: Detect similar duplicates
    logger.subsection('Detecting Similar Duplicates');
    const similarDuplicates = this.detectSimilarDuplicates();
    logger.success(`Found ${similarDuplicates.length} similar duplicate groups`);

    // Step 4: Detect pattern-based duplicates
    logger.subsection('Detecting Pattern-Based Duplicates');
    const patternGroups = this.detectPatternDuplicates();
    logger.success(`Found ${patternGroups.length} pattern groups`);

    // Step 5: Analyze file path patterns
    logger.subsection('Analyzing File Path Patterns');
    const filePathPatterns = this.analyzeFilePathPatterns();
    logger.success(`Found ${filePathPatterns.length} file path patterns`);

    const allDuplicates = [...exactDuplicates, ...similarDuplicates];

    // Calculate priorities
    this.calculatePriorities(allDuplicates);

    return {
      duplicateGroups: allDuplicates,
      patternGroups,
      filePathPatterns,
    };
  }

  /**
   * Load file contents from scan results
   */
  private async loadFileContents(scanResult: ScanResult): Promise<void> {
    logger.info('Loading file contents...');

    const files = scanResult.findings?.files || [];
    let loaded = 0;

    for (const file of files) {
      const fullPath = join(scanResult.project_root, file.path);

      // Skip ignored patterns
      if (this.shouldIgnoreFile(file.path)) {
        continue;
      }

      // Skip unsupported extensions
      const ext = file.path.substring(file.path.lastIndexOf('.'));
      if (!this.config.file_extensions.includes(ext)) {
        continue;
      }

      try {
        if (existsSync(fullPath)) {
          const content = readFileSync(fullPath, 'utf-8');
          const hash = this.hashContent(content);

          this.fileContents.set(file.path, {
            path: file.path,
            content,
            hash,
            lines: file.lines,
            size: file.size,
          });

          loaded++;
          logger.progress(loaded, files.length, file.path);
        }
      } catch (error) {
        logger.warning(`Failed to read ${file.path}: ${error}`);
      }
    }

    logger.success(`Loaded ${loaded} files for analysis`);
  }

  /**
   * Detect exact duplicates (100% match)
   */
  private detectExactDuplicates(): DuplicateGroup[] {
    const hashGroups = new Map<string, string[]>();

    // Group files by content hash
    for (const [path, fileContent] of this.fileContents) {
      const existing = hashGroups.get(fileContent.hash) || [];
      existing.push(path);
      hashGroups.set(fileContent.hash, existing);
    }

    const duplicateGroups: DuplicateGroup[] = [];
    let groupId = 1;

    for (const [hash, paths] of hashGroups) {
      if (paths.length < 2) continue; // Not a duplicate

      const firstFile = this.fileContents.get(paths[0])!;

      // Skip if below minimum lines
      if (firstFile.lines < this.config.minimum_lines) {
        continue;
      }

      duplicateGroups.push({
        id: `exact-${groupId++}`,
        similarity: 100,
        type: 'exact',
        files: paths.map(path => ({
          path,
          lines: `1-${this.fileContents.get(path)!.lines}`,
          hash,
        })),
        sample_code: firstFile.content.split('\n').slice(0, 10).join('\n'),
        lines_count: firstFile.lines,
        space_savings_potential: firstFile.size * (paths.length - 1),
        refactor_priority: 'medium', // Will be calculated later
        recommendation: `Consider extracting this code into a shared module. Found in ${paths.length} locations.`,
      });
    }

    return duplicateGroups;
  }

  /**
   * Detect similar duplicates (55-95% similarity using fuzzy hashing)
   */
  private detectSimilarDuplicates(): DuplicateGroup[] {
    const duplicateGroups: DuplicateGroup[] = [];
    const processed = new Set<string>();
    let groupId = 1;

    const files = Array.from(this.fileContents.keys());

    for (let i = 0; i < files.length; i++) {
      if (processed.has(files[i])) continue;

      const group: string[] = [files[i]];

      for (let j = i + 1; j < files.length; j++) {
        if (processed.has(files[j])) continue;

        const similarity = this.calculateSimilarity(files[i], files[j]);

        if (
          similarity >= this.config.similarity_thresholds.similar_match_min &&
          similarity < this.config.similarity_thresholds.similar_match_max
        ) {
          group.push(files[j]);
          processed.add(files[j]);
        }
      }

      if (group.length >= 2) {
        processed.add(files[i]);

        const firstFile = this.fileContents.get(group[0])!;
        const avgSimilarity = group.length === 2
          ? this.calculateSimilarity(group[0], group[1])
          : group.reduce((sum, path, idx) => {
              if (idx === 0) return 0;
              return sum + this.calculateSimilarity(group[0], path);
            }, 0) / (group.length - 1);

        duplicateGroups.push({
          id: `similar-${groupId++}`,
          similarity: Math.round(avgSimilarity),
          type: 'similar',
          files: group.map(path => ({
            path,
            lines: `1-${this.fileContents.get(path)!.lines}`,
            hash: this.fileContents.get(path)!.hash,
          })),
          sample_code: firstFile.content.split('\n').slice(0, 10).join('\n'),
          lines_count: firstFile.lines,
          space_savings_potential: Math.round(firstFile.size * (group.length - 1) * (avgSimilarity / 100)),
          refactor_priority: 'medium', // Will be calculated later
          recommendation: `Consider refactoring these similar implementations into a shared pattern. Average similarity: ${Math.round(avgSimilarity)}%`,
        });
      }

      logger.progress(i + 1, files.length);
    }

    return duplicateGroups;
  }

  /**
   * Detect pattern-based duplicates (repeated code structures)
   */
  private detectPatternDuplicates(): PatternGroup[] {
    const patterns = new Map<string, Set<string>>();

    for (const [path, fileContent] of this.fileContents) {
      const codePatterns = this.extractPatterns(fileContent.content);

      for (const pattern of codePatterns) {
        const existing = patterns.get(pattern) || new Set();
        existing.add(path);
        patterns.set(pattern, existing);
      }
    }

    const patternGroups: PatternGroup[] = [];

    for (const [pattern, files] of patterns) {
      if (files.size >= 3) { // Pattern appears in 3+ files
        patternGroups.push({
          pattern,
          occurrences: files.size,
          files: Array.from(files),
          suggested_solution: this.suggestPatternSolution(pattern),
        });
      }
    }

    return patternGroups.sort((a, b) => b.occurrences - a.occurrences);
  }

  /**
   * Analyze file path patterns for misplaced files
   */
  private analyzeFilePathPatterns(): Array<{ pattern: string; files: string[]; similarity: number }> {
    const pathGroups = new Map<string, string[]>();

    for (const path of this.fileContents.keys()) {
      const parts = path.split('/');
      if (parts.length < 2) continue;

      // Group by directory structure
      const pattern = parts.slice(0, -1).join('/');
      const existing = pathGroups.get(pattern) || [];
      existing.push(path);
      pathGroups.set(pattern, existing);
    }

    return Array.from(pathGroups.entries())
      .filter(([_, files]) => files.length >= 2)
      .map(([pattern, files]) => ({
        pattern,
        files,
        similarity: this.calculatePathSimilarity(files),
      }))
      .sort((a, b) => b.files.length - a.files.length);
  }

  /**
   * Calculate similarity between two files (0-100)
   */
  private calculateSimilarity(path1: string, path2: string): number {
    const cacheKey = [path1, path2].sort().join('::');

    if (this.similarityCache.has(cacheKey)) {
      return this.similarityCache.get(cacheKey)!;
    }

    const content1 = this.fileContents.get(path1)!.content;
    const content2 = this.fileContents.get(path2)!.content;

    // Simple line-based similarity
    const lines1 = content1.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    const lines2 = content2.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    const set1 = new Set(lines1);
    const set2 = new Set(lines2);

    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);

    const similarity = (intersection.size / union.size) * 100;
    this.similarityCache.set(cacheKey, similarity);

    return similarity;
  }

  /**
   * Calculate path similarity for files in a group
   */
  private calculatePathSimilarity(files: string[]): number {
    if (files.length < 2) return 100;

    let totalSimilarity = 0;
    let comparisons = 0;

    for (let i = 0; i < files.length - 1; i++) {
      for (let j = i + 1; j < files.length; j++) {
        const parts1 = files[i].split('/');
        const parts2 = files[j].split('/');

        let matches = 0;
        const maxLen = Math.max(parts1.length, parts2.length);

        for (let k = 0; k < Math.min(parts1.length, parts2.length); k++) {
          if (parts1[k] === parts2[k]) matches++;
        }

        totalSimilarity += (matches / maxLen) * 100;
        comparisons++;
      }
    }

    return Math.round(totalSimilarity / comparisons);
  }

  /**
   * Extract code patterns from content
   */
  private extractPatterns(content: string): string[] {
    const patterns: string[] = [];

    // Extract function signatures
    const functionPattern = /(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:\([^)]*\)|async)/g;
    let match;
    while ((match = functionPattern.exec(content)) !== null) {
      patterns.push(`function:${match[1]}`);
    }

    // Extract import patterns
    const importPattern = /import\s+.*?from\s+['"]([^'"]+)['"]/g;
    while ((match = importPattern.exec(content)) !== null) {
      patterns.push(`import:${match[1]}`);
    }

    // Extract class patterns
    const classPattern = /class\s+(\w+)/g;
    while ((match = classPattern.exec(content)) !== null) {
      patterns.push(`class:${match[1]}`);
    }

    return patterns;
  }

  /**
   * Suggest solution for repeated pattern
   */
  private suggestPatternSolution(pattern: string): string {
    if (pattern.startsWith('function:')) {
      return 'Consider creating a shared utility module for this function';
    }
    if (pattern.startsWith('import:')) {
      return 'Consider consolidating these imports into a barrel export';
    }
    if (pattern.startsWith('class:')) {
      return 'Consider using a factory pattern or inheritance';
    }
    return 'Consider refactoring to reduce duplication';
  }

  /**
   * Calculate refactor priorities for duplicate groups
   */
  private calculatePriorities(groups: DuplicateGroup[]): void {
    for (const group of groups) {
      const lines = group.lines_count;
      const occurrences = group.files.length;
      const rules = this.config.refactor_priority_rules;

      if (lines >= rules.critical_lines || occurrences >= rules.critical_occurrences) {
        group.refactor_priority = 'critical';
      } else if (lines >= rules.high_lines || occurrences >= rules.high_occurrences) {
        group.refactor_priority = 'high';
      } else if (lines >= rules.medium_lines) {
        group.refactor_priority = 'medium';
      } else {
        group.refactor_priority = 'low';
      }
    }
  }

  /**
   * Check if file should be ignored
   */
  private shouldIgnoreFile(path: string): boolean {
    return this.config.ignore_patterns.some(pattern => {
      const regex = new RegExp(pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*'));
      return regex.test(path);
    });
  }

  /**
   * Hash content for comparison
   */
  private hashContent(content: string): string {
    return createHash('sha256').update(content).digest('hex');
  }
}
