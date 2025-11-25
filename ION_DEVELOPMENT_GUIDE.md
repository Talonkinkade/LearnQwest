# 🔧 Ion Development Guide

**How to Build Your Own BMAD Ions**

---

## 📖 What is an Ion?

An **Ion** is a specialized TypeScript/Bun agent that performs a specific task. Ions are:
- **Atomic** - Single-purpose, focused
- **Fast** - Execute in milliseconds
- **Local** - No external APIs (when possible)
- **Composable** - Work together via ADA orchestration

---

## 🏗️ Ion Architecture

```
qwest-ions/
└── your-ion-name/
    ├── src/
    │   ├── index.ts          # Main entry point
    │   ├── types.ts          # Type definitions
    │   └── [your-logic].ts   # Implementation
    ├── tests/
    │   └── index.test.ts     # Tests
    ├── package.json          # Dependencies
    ├── tsconfig.json         # TypeScript config
    └── README.md             # Documentation
```

---

## 🚀 Quick Start: Build Your First Ion

### Step 1: Create Ion Directory

```bash
cd qwest-ions
mkdir my-new-ion
cd my-new-ion
```

### Step 2: Initialize Bun Project

```bash
bun init -y
```

### Step 3: Create `src/index.ts`

```typescript
#!/usr/bin/env bun

import { parseArgs } from "util";

// Define your Ion's input/output types
interface MyIonInput {
  query: string;
  options?: Record<string, any>;
}

interface MyIonOutput {
  success: boolean;
  result: any;
  execution_time_ms: number;
}

// Main Ion logic
async function executeIon(input: MyIonInput): Promise<MyIonOutput> {
  const startTime = performance.now();
  
  try {
    // YOUR LOGIC HERE
    const result = await processInput(input.query);
    
    const executionTime = performance.now() - startTime;
    
    return {
      success: true,
      result,
      execution_time_ms: executionTime
    };
  } catch (error) {
    return {
      success: false,
      result: null,
      execution_time_ms: performance.now() - startTime
    };
  }
}

async function processInput(query: string): Promise<any> {
  // Implement your Ion's core functionality here
  return { message: `Processed: ${query}` };
}

// CLI Interface
async function main() {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      query: { type: "string" },
      help: { type: "boolean" }
    }
  });

  if (values.help) {
    console.log(`
My New Ion - Description of what it does

Usage:
  bun run src/index.ts --query "your input"

Options:
  --query    Input query to process
  --help     Show this help message
    `);
    process.exit(0);
  }

  if (!values.query) {
    console.error("Error: --query is required");
    process.exit(1);
  }

  const result = await executeIon({ query: values.query });
  console.log(JSON.stringify(result, null, 2));
}

main();
```

### Step 4: Add Dependencies

```bash
bun add zod  # For validation
bun add --dev @types/bun  # TypeScript types
```

### Step 5: Test Your Ion

```bash
bun run src/index.ts --query "test input"
```

---

## 🔌 Integrate with ADA

### Step 1: Register Your Ion

Edit `ada_orchestrator.py` and add to `ION_REGISTRY`:

```python
ION_REGISTRY = {
    # ... existing ions ...
    "my-new-ion": "my-new-ion",  # Add your ion here
}
```

### Step 2: Add Execution Logic

In `IonBridge.execute_ion()`, add your Ion's command:

```python
elif ion_name == "my-new-ion":
    cmd = [bun_cmd, "run", "src/index.ts", "--query", task_description]
```

### Step 3: Test Integration

```python
# test_my_ion.py
import asyncio
from ada_orchestrator import ADAOrchestrator, TaskPriority, QuestDomain

async def test():
    ada = ADAOrchestrator()
    task_id = await ada.submit_task(
        description="Test my new ion",
        priority=TaskPriority.HIGH,
        domain=QuestDomain.GENERAL
    )
    await ada.start()
    await asyncio.sleep(2)
    result = ada.task_queue.completed_tasks.get(task_id)
    print(result.results if result else "Task not completed")
    await ada.stop()

asyncio.run(test())
```

---

## ✅ Ion Checklist

Before considering your Ion complete:

- [ ] **Functionality** - Does it do what it's supposed to?
- [ ] **Performance** - Executes in < 1 second for typical inputs?
- [ ] **Error Handling** - Gracefully handles invalid inputs?
- [ ] **CLI Interface** - Works from command line with `--help`?
- [ ] **JSON Output** - Returns structured JSON?
- [ ] **Tests** - Has at least basic test coverage?
- [ ] **Documentation** - README explains what it does?
- [ ] **ADA Integration** - Registered and tested with ADA?

---

## 🎯 Ion Design Principles

### 1. Single Responsibility
Each Ion should do ONE thing well. Don't create "do everything" Ions.

**Good:** `duplicate-detector` - finds duplicate code  
**Bad:** `code-analyzer` - does 10 different things

### 2. Fast Execution
Target < 500ms for most operations. If it takes longer, consider:
- Breaking into smaller Ions
- Caching results
- Optimizing algorithms

### 3. Local-First
Prefer local processing over API calls when possible:
- ✅ Analyze local files
- ✅ Process in-memory data
- ⚠️ Call external APIs only when necessary

### 4. Structured Output
Always return JSON with consistent structure:

```typescript
{
  "success": boolean,
  "result": any,
  "execution_time_ms": number,
  "error"?: string
}
```

### 5. Graceful Degradation
Handle errors without crashing:
- Invalid input → Return error message
- Missing file → Return helpful error
- Timeout → Return partial results

---

## 📚 Example Ions to Study

### Simple Ion: quality-assessor
- **Purpose:** Score content quality
- **Input:** JSON file with content items
- **Output:** Quality scores (0-100)
- **Location:** `qwest-ions/quality-assessor/`

### Complex Ion: omnisearch
- **Purpose:** Search multiple sources
- **Input:** Search query
- **Output:** Aggregated results
- **Location:** `qwest-ions/omnisearch/`

---

## 🐛 Debugging Tips

### Test Ion Standalone First
```bash
cd qwest-ions/your-ion
bun run src/index.ts --query "test"
```

### Check ADA Logs
```bash
cat ada_logs/ada_*.jsonl | grep "your-ion"
```

### Enable Verbose Logging
```python
# In ada_orchestrator.py
logging.basicConfig(level=logging.DEBUG)
```

### Test with Simple Input
Start with the simplest possible input, then add complexity.

---

## 🚀 Advanced Topics

### Async Operations
```typescript
async function processAsync(input: string): Promise<Result> {
  const results = await Promise.all([
    operation1(input),
    operation2(input),
    operation3(input)
  ]);
  return combineResults(results);
}
```

### Streaming Output
```typescript
// For long-running operations
for await (const chunk of processStream(input)) {
  console.log(JSON.stringify({ type: "progress", data: chunk }));
}
```

### Caching
```typescript
const cache = new Map<string, Result>();

function getCached(key: string): Result | null {
  return cache.get(key) || null;
}
```

---

## 📞 Need Help?

- **Check existing Ions** in `qwest-ions/` for examples
- **Read ADA logs** in `ada_logs/` for debugging
- **Test standalone** before integrating with ADA
- **Start simple** and add complexity gradually

---

## 🎉 You're Ready!

You now know how to:
- ✅ Create a new Ion from scratch
- ✅ Integrate it with ADA
- ✅ Test it end-to-end
- ✅ Follow Ion design principles

**Go build something amazing!** 🚀

---

*Ion Development Guide - Part of LearnQwest Full Intelligence Pipeline™*
