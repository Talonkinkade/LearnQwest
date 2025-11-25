# Agent Definition: Code Grouper Ion

**Name**: Code Grouper Ion
**Version**: 1.0.0
**Method**: BMAD
**Role**: Code Organization Analysis

## Purpose

Analyzes import patterns to suggest better file organization through functional grouping, layered architecture detection, and misplaced file identification.

## Capabilities

- Import graph analysis
- Functional grouping detection
- Layered architecture recognition
- Misplaced file identification
- Git-aware migration scripts
- Rollback generation

## Input/Output

**Input**: `scan-results.json`
**Output**: `grouping-plan.json` + migration scripts

## Strategies

1. **Functional**: Group files that import each other
2. **Layered**: Group by architectural layer (ui/services/models)
3. **Domain**: Group by business domain

## Status

**Production Ready** ✅

---

**Part of**: LearnQwest Code Cleanup Suite (Ion 4 of 5)
**Last updated**: 2025-11-19
