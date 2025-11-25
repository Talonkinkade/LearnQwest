import { readFileSync, existsSync } from 'fs';
import { join, dirname, basename } from 'path';
import type { ScanResult, Config, FileGroup, MisplacedFile } from './types';
import { logger } from './logger';

export class CodeGrouper {
  private importGraph: Map<string, Set<string>> = new Map();
  private fileContents: Map<string, string> = new Map();

  constructor(private config: Config, private projectRoot: string) {}

  async analyze(scanResult: ScanResult) {
    logger.section('Code Grouping Analysis');

    // Load files and build import graph
    await this.loadFiles(scanResult);
    await this.buildImportGraph();

    // Analyze grouping strategies
    const functionalGroups = this.analyzeFunctionalGrouping();
    const layeredGroups = this.analyzeLayeredGrouping();
    const misplacedFiles = this.findMisplacedFiles();

    const allGroups = [...functionalGroups, ...layeredGroups];
    const proposedStructure = this.generateProposedStructure(allGroups);

    return {
      fileGroups: allGroups,
      misplacedFiles,
      proposedStructure,
    };
  }

  private async loadFiles(scanResult: ScanResult) {
    logger.info('Loading files...');
    const files = scanResult.findings?.files || [];

    for (const file of files) {
      if (this.shouldIgnore(file.path)) continue;

      const fullPath = join(this.projectRoot, file.path);
      if (existsSync(fullPath)) {
        try {
          const content = readFileSync(fullPath, 'utf-8');
          this.fileContents.set(file.path, content);
        } catch (error) {
          logger.warning(`Failed to read ${file.path}`);
        }
      }
    }

    logger.success(`Loaded ${this.fileContents.size} files`);
  }

  private async buildImportGraph() {
    logger.info('Building import graph...');

    for (const [filePath, content] of this.fileContents) {
      const imports = this.extractImports(content);
      this.importGraph.set(filePath, new Set(imports));
    }

    logger.success('Import graph built');
  }

  private extractImports(content: string): string[] {
    const imports: string[] = [];
    const importRegex = /import\s+.*?from\s+['"]([^'"]+)['"]/g;
    let match;

    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
    }

    return imports;
  }

  private analyzeFunctionalGrouping(): FileGroup[] {
    logger.subsection('Analyzing Functional Grouping');
    const groups: FileGroup[] = [];
    const processed = new Set<string>();

    // Group files that import each other heavily
    for (const [file, imports] of this.importGraph) {
      if (processed.has(file)) continue;

      const relatedFiles = this.findRelatedFiles(file, imports);
      if (relatedFiles.size >= this.config.analysis.min_group_size) {
        const groupFiles = Array.from(relatedFiles);
        groups.push({
          id: `func-${groups.length + 1}`,
          name: this.inferGroupName(groupFiles),
          strategy: 'functional',
          files: groupFiles,
          suggested_location: this.suggestLocation(groupFiles),
          confidence: 0.8,
          reason: 'Files frequently import from each other',
        });

        groupFiles.forEach(f => processed.add(f));
      }
    }

    logger.success(`Found ${groups.length} functional groups`);
    return groups;
  }

  private analyzeLayeredGrouping(): FileGroup[] {
    logger.subsection('Analyzing Layered Grouping');
    const groups: FileGroup[] = [];

    // Simple layer detection based on naming patterns
    const layers = {
      ui: [] as string[],
      services: [] as string[],
      models: [] as string[],
      utils: [] as string[],
    };

    for (const file of this.fileContents.keys()) {
      if (file.includes('component') || file.includes('view') || file.includes('ui')) {
        layers.ui.push(file);
      } else if (file.includes('service') || file.includes('api')) {
        layers.services.push(file);
      } else if (file.includes('model') || file.includes('schema')) {
        layers.models.push(file);
      } else if (file.includes('util') || file.includes('helper')) {
        layers.utils.push(file);
      }
    }

    for (const [layerName, files] of Object.entries(layers)) {
      if (files.length >= this.config.analysis.min_group_size) {
        groups.push({
          id: `layer-${layerName}`,
          name: layerName.charAt(0).toUpperCase() + layerName.slice(1),
          strategy: 'layered',
          files,
          suggested_location: `src/${layerName}`,
          confidence: 0.7,
          reason: `Files follow ${layerName} layer pattern`,
        });
      }
    }

    logger.success(`Found ${groups.length} layer groups`);
    return groups;
  }

  private findRelatedFiles(file: string, imports: Set<string>): Set<string> {
    const related = new Set<string>([file]);

    // Find files that this file imports from
    for (const imp of imports) {
      if (imp.startsWith('.')) {
        const resolved = this.resolveRelativeImport(imp, file);
        if (resolved && this.fileContents.has(resolved)) {
          related.add(resolved);
        }
      }
    }

    return related;
  }

  private resolveRelativeImport(importPath: string, fromFile: string): string | null {
    const dir = dirname(fromFile);
    const resolved = join(dir, importPath);

    // Try common extensions
    const extensions = ['.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.js'];
    for (const ext of extensions) {
      const withExt = resolved + ext;
      if (this.fileContents.has(withExt)) return withExt;
    }

    return null;
  }

  private findMisplacedFiles(): MisplacedFile[] {
    logger.subsection('Finding Misplaced Files');
    const misplaced: MisplacedFile[] = [];

    for (const [file, imports] of this.importGraph) {
      const currentDir = dirname(file);
      const mostCommonImportDir = this.getMostCommonImportDirectory(imports, file);

      if (mostCommonImportDir && mostCommonImportDir !== currentDir) {
        const confidence = 0.7;
        if (confidence >= this.config.analysis.confidence_threshold) {
          misplaced.push({
            file,
            current_location: currentDir,
            suggested_location: mostCommonImportDir,
            confidence,
            reason: 'File imports mostly from different directory',
          });
        }
      }
    }

    logger.success(`Found ${misplaced.length} misplaced files`);
    return misplaced;
  }

  private getMostCommonImportDirectory(imports: Set<string>, fromFile: string): string | null {
    const dirs: Record<string, number> = {};

    for (const imp of imports) {
      if (imp.startsWith('.')) {
        const resolved = this.resolveRelativeImport(imp, fromFile);
        if (resolved) {
          const dir = dirname(resolved);
          dirs[dir] = (dirs[dir] || 0) + 1;
        }
      }
    }

    if (Object.keys(dirs).length === 0) return null;

    return Object.entries(dirs).sort((a, b) => b[1] - a[1])[0][0];
  }

  private inferGroupName(files: string[]): string {
    // Extract common path segments
    const firstFile = files[0];
    const parts = firstFile.split('/');
    return parts[parts.length - 2] || 'unnamed-group';
  }

  private suggestLocation(files: string[]): string {
    const firstFile = files[0];
    const dir = dirname(firstFile);
    return `src/${basename(dir)}`;
  }

  private generateProposedStructure(groups: FileGroup[]): Record<string, string[]> {
    const structure: Record<string, string[]> = {};

    for (const group of groups) {
      structure[group.suggested_location] = group.files;
    }

    return structure;
  }

  private shouldIgnore(path: string): boolean {
    return this.config.ignore_patterns.some(pattern => {
      const regex = new RegExp(pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*'));
      return regex.test(path);
    });
  }
}
