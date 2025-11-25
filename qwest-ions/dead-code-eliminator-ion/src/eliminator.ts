import { readFileSync, existsSync } from 'fs';
import { join, relative } from 'path';
import { parse } from '@typescript-eslint/typescript-estree';
import type {
  ScanResult,
  Config,
  CodeEntity,
  FileReference,
  Dependency,
  UnusedCodeItem,
} from './types';
import { logger } from './logger';

export class DeadCodeEliminator {
  private fileContents: Map<string, string> = new Map();
  private codeEntities: Map<string, CodeEntity> = new Map();
  private fileReferences: Map<string, FileReference> = new Map();
  private dependencies: Map<string, Dependency> = new Map();
  private importGraph: Map<string, Set<string>> = new Map(); // file -> files it imports

  constructor(private config: Config, private projectRoot: string) {}

  /**
   * Analyze scan results for dead code
   */
  async analyze(scanResult: ScanResult): Promise<{
    unusedCode: UnusedCodeItem[];
    unusedFiles: Array<{ path: string; size: number; reason: string; safe_to_delete: boolean }>;
    unusedDependencies: Dependency[];
    diskSpaceReclaimable: number;
  }> {
    logger.section('Dead Code Analysis');

    // Step 1: Load all files
    await this.loadFiles(scanResult);

    // Step 2: Build import/export graph
    logger.subsection('Building Import/Export Graph');
    await this.buildImportGraph();

    // Step 3: Analyze code entities
    if (this.config.analysis.check_functions || this.config.analysis.check_classes) {
      logger.subsection('Analyzing Code Entities');
      await this.analyzeCodeEntities();
    }

    // Step 4: Find unused files
    logger.subsection('Finding Unused Files');
    const unusedFiles = this.findUnusedFiles();

    // Step 5: Find unused dependencies
    let unusedDependencies: Dependency[] = [];
    if (this.config.analysis.check_dependencies) {
      logger.subsection('Analyzing Dependencies');
      unusedDependencies = await this.findUnusedDependencies(scanResult);
    }

    // Step 6: Find unused code entities
    logger.subsection('Finding Unused Code Entities');
    const unusedEntities = this.findUnusedEntities();

    // Step 7: Calculate space savings
    const diskSpaceReclaimable = this.calculateSpaceSavings(unusedFiles, unusedEntities);

    logger.success(`Analysis complete!`);
    logger.info(`Unused files: ${unusedFiles.length}`);
    logger.info(`Unused entities: ${unusedEntities.length}`);
    logger.info(`Unused dependencies: ${unusedDependencies.length}`);
    logger.info(`Space reclaimable: ${this.formatBytes(diskSpaceReclaimable)}`);

    return {
      unusedCode: unusedEntities,
      unusedFiles,
      unusedDependencies,
      diskSpaceReclaimable,
    };
  }

  /**
   * Load file contents
   */
  private async loadFiles(scanResult: ScanResult): Promise<void> {
    logger.info('Loading file contents...');

    const files = scanResult.findings?.files || [];
    let loaded = 0;

    for (const file of files) {
      if (this.shouldIgnoreFile(file.path)) continue;

      const ext = file.path.substring(file.path.lastIndexOf('.'));
      if (!this.config.file_extensions.includes(ext)) continue;

      const fullPath = join(scanResult.project_root, file.path);

      try {
        if (existsSync(fullPath)) {
          const content = readFileSync(fullPath, 'utf-8');
          this.fileContents.set(file.path, content);

          // Initialize file reference
          this.fileReferences.set(file.path, {
            path: file.path,
            imports: [],
            exports: [],
            referenced_by: [],
            is_entry_point: this.isEntryPoint(file.path),
            is_orphaned: false,
          });

          loaded++;
          logger.progress(loaded, files.length, file.path);
        }
      } catch (error) {
        logger.warning(`Failed to read ${file.path}`);
      }
    }

    logger.success(`Loaded ${loaded} files`);
  }

  /**
   * Build import/export graph
   */
  private async buildImportGraph(): Promise<void> {
    let processed = 0;
    const total = this.fileContents.size;

    for (const [filePath, content] of this.fileContents) {
      try {
        const ast = parse(content, {
          jsx: filePath.endsWith('.tsx') || filePath.endsWith('.jsx'),
          comment: false,
          loc: true,
        });

        const imports: string[] = [];
        const exports: string[] = [];

        // Walk AST to find imports and exports
        this.walkAST(ast, filePath, imports, exports);

        const fileRef = this.fileReferences.get(filePath)!;
        fileRef.imports = imports;
        fileRef.exports = exports;

        // Build reverse graph (who imports this file)
        for (const importPath of imports) {
          const resolvedPath = this.resolveImport(importPath, filePath);
          if (resolvedPath && this.fileReferences.has(resolvedPath)) {
            const importedFile = this.fileReferences.get(resolvedPath)!;
            importedFile.referenced_by.push(filePath);
          }
        }

        this.importGraph.set(filePath, new Set(imports));

        processed++;
        logger.progress(processed, total);
      } catch (error) {
        logger.debug(`Failed to parse ${filePath}: ${error}`);
      }
    }

    logger.success(`Built import graph for ${processed} files`);
  }

  /**
   * Walk AST to extract imports and exports
   */
  private walkAST(node: any, filePath: string, imports: string[], exports: string[]): void {
    if (!node) return;

    // Import declarations
    if (node.type === 'ImportDeclaration') {
      imports.push(node.source.value);
    }

    // Export declarations
    if (node.type === 'ExportNamedDeclaration' || node.type === 'ExportDefaultDeclaration') {
      if (node.declaration) {
        if (node.declaration.id) {
          exports.push(node.declaration.id.name);
        }
      }
    }

    // Recursively walk children
    for (const key in node) {
      if (key === 'parent' || key === 'loc' || key === 'range') continue;
      const child = node[key];
      if (Array.isArray(child)) {
        child.forEach(c => this.walkAST(c, filePath, imports, exports));
      } else if (typeof child === 'object') {
        this.walkAST(child, filePath, imports, exports);
      }
    }
  }

  /**
   * Analyze code entities (functions, classes, etc.)
   */
  private async analyzeCodeEntities(): Promise<void> {
    let entityCount = 0;

    for (const [filePath, content] of this.fileContents) {
      try {
        const ast = parse(content, {
          jsx: filePath.endsWith('.tsx') || filePath.endsWith('.jsx'),
          comment: false,
          loc: true,
        });

        this.extractEntities(ast, filePath);
      } catch (error) {
        logger.debug(`Failed to analyze entities in ${filePath}`);
      }
    }

    // Mark entities as used/unused based on references
    this.markEntityUsages();

    logger.success(`Analyzed ${this.codeEntities.size} code entities`);
  }

  /**
   * Extract code entities from AST
   */
  private extractEntities(node: any, filePath: string): void {
    if (!node) return;

    const createEntity = (name: string, type: any, line: number, exported: boolean) => {
      const key = `${filePath}::${name}`;
      this.codeEntities.set(key, {
        name,
        type,
        file: filePath,
        line,
        exported,
        used: false,
        usages: [],
      });
    };

    // Function declarations
    if (node.type === 'FunctionDeclaration' && node.id) {
      createEntity(node.id.name, 'function', node.loc?.start.line || 0, false);
    }

    // Class declarations
    if (node.type === 'ClassDeclaration' && node.id) {
      createEntity(node.id.name, 'class', node.loc?.start.line || 0, false);
    }

    // Variable declarations
    if (node.type === 'VariableDeclaration') {
      for (const decl of node.declarations || []) {
        if (decl.id && decl.id.name) {
          createEntity(decl.id.name, 'variable', node.loc?.start.line || 0, false);
        }
      }
    }

    // Recursively walk
    for (const key in node) {
      if (key === 'parent' || key === 'loc' || key === 'range') continue;
      const child = node[key];
      if (Array.isArray(child)) {
        child.forEach(c => this.extractEntities(c, filePath));
      } else if (typeof child === 'object') {
        this.extractEntities(child, filePath);
      }
    }
  }

  /**
   * Mark entity usages
   */
  private markEntityUsages(): void {
    // Simple heuristic: if entity name appears in other files, mark as used
    for (const [key, entity] of this.codeEntities) {
      for (const [filePath, content] of this.fileContents) {
        if (filePath === entity.file) continue;

        if (content.includes(entity.name)) {
          entity.used = true;
          entity.usages.push({ file: filePath, line: 0 });
        }
      }

      // Entry point files are always considered used
      if (this.isEntryPoint(entity.file)) {
        entity.used = true;
      }
    }
  }

  /**
   * Find unused files
   */
  private findUnusedFiles(): Array<{ path: string; size: number; reason: string; safe_to_delete: boolean }> {
    const unusedFiles: Array<{ path: string; size: number; reason: string; safe_to_delete: boolean }> = [];

    for (const [filePath, fileRef] of this.fileReferences) {
      // Skip entry points
      if (fileRef.is_entry_point) continue;

      // Check if file is referenced by any other file
      if (fileRef.referenced_by.length === 0) {
        // Not imported anywhere
        const fileSize = this.fileContents.get(filePath)?.length || 0;

        unusedFiles.push({
          path: filePath,
          size: fileSize,
          reason: 'No imports found - file is not referenced anywhere',
          safe_to_delete: true,
        });
      }
    }

    return unusedFiles.sort((a, b) => b.size - a.size);
  }

  /**
   * Find unused dependencies
   */
  private async findUnusedDependencies(scanResult: ScanResult): Promise<Dependency[]> {
    const packageJsonPath = join(scanResult.project_root, 'package.json');

    if (!existsSync(packageJsonPath)) {
      logger.warning('No package.json found - skipping dependency analysis');
      return [];
    }

    try {
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));
      const deps = packageJson.dependencies || {};
      const devDeps = this.config.dependencies.check_devDependencies
        ? (packageJson.devDependencies || {})
        : {};

      const allDeps = { ...deps, ...devDeps };
      const unusedDeps: Dependency[] = [];

      // Check each dependency
      for (const [name, version] of Object.entries(allDeps)) {
        // Skip @types packages if configured
        if (this.config.dependencies.ignore_types_packages && name.startsWith('@types/')) {
          continue;
        }

        // Check if dependency is imported anywhere
        const imported = this.isDependencyUsed(name);

        if (!imported) {
          unusedDeps.push({
            name,
            version: version as string,
            type: deps[name] ? 'dependency' : 'devDependency',
            used: false,
            imported_in: [],
          });
        }
      }

      return unusedDeps;
    } catch (error) {
      logger.warning(`Failed to analyze dependencies: ${error}`);
      return [];
    }
  }

  /**
   * Check if dependency is used
   */
  private isDependencyUsed(depName: string): boolean {
    for (const [_, fileRef] of this.fileReferences) {
      // Check if any import starts with the dependency name
      if (fileRef.imports.some(imp => imp === depName || imp.startsWith(depName + '/'))) {
        return true;
      }
    }
    return false;
  }

  /**
   * Find unused code entities
   */
  private findUnusedEntities(): UnusedCodeItem[] {
    const unused: UnusedCodeItem[] = [];
    let id = 1;

    for (const [key, entity] of this.codeEntities) {
      if (!entity.used && !this.isEntryPoint(entity.file)) {
        const fileSize = this.fileContents.get(entity.file)?.length || 0;
        const priority = this.calculatePriority(fileSize);

        unused.push({
          id: `entity-${id++}`,
          type: entity.type,
          name: entity.name,
          file: entity.file,
          line: entity.line,
          size_bytes: Math.round(fileSize / 10), // Rough estimate
          priority,
          reason: `${entity.type} '${entity.name}' is not used anywhere`,
          safe_to_delete: true,
          recommendation: `Remove unused ${entity.type} '${entity.name}' from ${entity.file}`,
        });
      }
    }

    return unused.sort((a, b) => b.size_bytes - a.size_bytes);
  }

  /**
   * Calculate space savings
   */
  private calculateSpaceSavings(
    unusedFiles: Array<{ size: number }>,
    unusedEntities: UnusedCodeItem[]
  ): number {
    const filesSavings = unusedFiles.reduce((sum, f) => sum + f.size, 0);
    const entitiesSavings = unusedEntities.reduce((sum, e) => sum + e.size_bytes, 0);
    return filesSavings + entitiesSavings;
  }

  /**
   * Calculate priority based on size
   */
  private calculatePriority(sizeBytes: number): 'critical' | 'high' | 'medium' | 'low' {
    const sizeKB = sizeBytes / 1024;

    if (sizeKB >= this.config.size_thresholds.critical_kb) return 'critical';
    if (sizeKB >= this.config.size_thresholds.high_kb) return 'high';
    if (sizeKB >= this.config.size_thresholds.medium_kb) return 'medium';
    return 'low';
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
   * Check if file is an entry point
   */
  private isEntryPoint(path: string): boolean {
    const basename = path.split('/').pop() || '';
    return this.config.entry_points.some(pattern => {
      const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
      return regex.test(basename);
    });
  }

  /**
   * Resolve import path to actual file
   */
  private resolveImport(importPath: string, fromFile: string): string | null {
    // Simple resolution - in production, would use full module resolution
    if (importPath.startsWith('.')) {
      // Relative import
      const dir = fromFile.substring(0, fromFile.lastIndexOf('/'));
      let resolved = join(dir, importPath);

      // Try with common extensions
      for (const ext of this.config.file_extensions) {
        const withExt = resolved + ext;
        if (this.fileReferences.has(withExt)) return withExt;
      }

      // Try index files
      for (const ext of this.config.file_extensions) {
        const indexFile = join(resolved, 'index' + ext);
        if (this.fileReferences.has(indexFile)) return indexFile;
      }
    }

    return null;
  }

  /**
   * Format bytes to human-readable
   */
  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  }
}
