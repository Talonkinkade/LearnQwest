# Quality Assessment Qwest-ion - Installation Guide

## Prerequisites

### 1. Install Bun Runtime

**Windows:**
```powershell
# Using PowerShell
irm bun.sh/install.ps1 | iex
```

**Verify installation:**
```bash
bun --version
# Should show: 1.0.0 or higher
```

### 2. Install Dependencies

```bash
cd c:\Users\talon\OneDrive\Projects\LearnQwest\qwest-ions\quality-assessor
bun install
```

This will install:
- `zod@^3.22.4` - Schema validation
- `yaml@^2.3.4` - Config file parsing

## Verification

### Run Tests

```bash
# All tests (should pass 100%)
bun test

# Specific test suites
bun test tests/scorers.test.ts
bun test tests/integration.test.ts

# Watch mode (auto-run on file changes)
bun test --watch
```

### Type Check

```bash
bun run typecheck
```

### Quick Test Run

```bash
# Test with the YouTube playlist data
bun run src/index.ts --input ../../output/omnisearch_results.json --output ../../output/quality_filtered.json --mode testing --verbose
```

## Common Issues

### Issue: `bun: command not found`

**Solution:** Bun is not installed or not in PATH
```powershell
# Reinstall Bun
irm bun.sh/install.ps1 | iex

# Add to PATH if needed
$env:PATH += ";$env:USERPROFILE\.bun\bin"
```

### Issue: Module resolution errors

**Solution:** Ensure TypeScript config is correct
```bash
bun run typecheck
```

### Issue: Test failures

**Solution:** Check Bun version
```bash
bun --version
# Must be 1.0.0+
```

## Next Steps

Once installed and verified:

1. **Run with real data:**
   ```bash
   bun run src/index.ts -i ../../output/omnisearch_results.json -o ../../output/quality_filtered.json -m production -v
   ```

2. **Integrate with workflow executor:**
   ```bash
   cd ../..
   python workflow_executor.py run complete-pipeline
   ```

3. **Start building Agent #2 (Difficulty Scorer)**

## File Structure Verification

Ensure you have:
```
qwest-ions/quality-assessor/
├── src/
│   ├── index.ts              ✅ CLI entry
│   ├── orchestrator.ts       ✅ Main logic
│   ├── types.ts              ✅ Schemas
│   ├── config.ts             ✅ Config loader
│   ├── logger.ts             ✅ Logging
│   └── scorers/
│       ├── credibility.ts    ✅ Scorer 1/5
│       ├── accuracy.ts       ✅ Scorer 2/5
│       ├── production.ts     ✅ Scorer 3/5
│       ├── educational.ts    ✅ Scorer 4/5
│       └── engagement.ts     ✅ Scorer 5/5
├── tests/
│   ├── scorers.test.ts       ✅ Unit tests
│   └── integration.test.ts   ✅ Integration tests
├── config/
│   └── thresholds.yaml       ✅ Configuration
├── package.json              ✅ Dependencies
├── tsconfig.json             ✅ TypeScript config
├── agent.md                  ✅ BMAD definition
├── README.md                 ✅ Usage docs
└── INSTALLATION.md           ✅ This file
```

## Support

If you encounter issues:

1. Check [Bun documentation](https://bun.sh/docs)
2. Verify Node.js is not interfering (Bun should work standalone)
3. Review error logs with `--verbose` flag
4. Check test output for specific failures

---

**Status:** Agent #1 (Quality Assessment) - BUILD COMPLETE ✅
**Next:** Install Bun → Run tests → Integrate with pipeline → Build Agent #2
