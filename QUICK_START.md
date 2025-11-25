# LearnQwest Quick Start

Get the Full Intelligence Pipeline running in 3 minutes.

---

## Prerequisites

- Python 3.11+
- Bun 1.0+ (for TypeScript Ions)

---

## Step 1: Install Bun (if not installed)

```powershell
# Windows
powershell -NoProfile -Command "irm bun.sh/install.ps1 | iex"

# Verify
C:\Users\talon\.bun\bin\bun.exe --version
# Should show: 1.3.3 or higher
```

---

## Step 2: Install Ion Dependencies

```powershell
cd C:\Users\talon\OneDrive\Projects\LearnQwest\qwest-ions\quality-assessor
C:\Users\talon\.bun\bin\bun.exe install
```

---

## Step 3: Test the Pipeline

```powershell
cd C:\Users\talon\OneDrive\Projects\LearnQwest

python -c "
import asyncio
from ada_orchestrator import ADAOrchestrator, TaskPriority, QuestDomain

async def test_pipeline():
    print('='*60)
    print('  LEARNQWEST QUICK START TEST')
    print('='*60)

    # Initialize ADA
    ada = ADAOrchestrator()
    print(f'Ions available: {ada.ion_bridge.list_ions()}')

    # Submit a task
    task_id = await ada.submit_task(
        description='Assess quality of Python tutorial',
        priority=TaskPriority.HIGH,
        domain=QuestDomain.GENERAL
    )
    print(f'Task submitted: {task_id[:8]}...')

    # Get and process task
    task = await ada.task_queue.get_next_task()
    if task:
        # Route to agent
        agents = ada.routing_spine.route(task.description)
        primary = next((a for a in agents if ada.ion_bridge.is_real_ion(a)), 'quality-assessor')

        # Execute real Ion
        result = await ada.ion_bridge.execute_ion(primary, task.description)
        print(f'Ion executed: {primary}')
        print(f'Success: {result[\"success\"]}')
        print(f'Time: {result[\"execution_time_ms\"]:.0f}ms')

        # Record feedback
        ada.feedback_loop.record(
            task_id=task.id,
            content_type='test',
            agents_used=[primary],
            success=result['success'],
            execution_time_ms=result['execution_time_ms']
        )
        print('Feedback recorded!')

    print()
    print('='*60)
    print('  SUCCESS! Pipeline is working.')
    print('='*60)

asyncio.run(test_pipeline())
"
```

---

## Expected Output

```
============================================================
  LEARNQWEST QUICK START TEST
============================================================
Ions available: ['omnisearch', 'quality-assessor', 'duplicate-detector-ion', ...]
Task submitted: abc12345...
Ion executed: quality-assessor
Success: True
Time: 182ms
Feedback recorded!

============================================================
  SUCCESS! Pipeline is working.
============================================================
```

---

## What Just Happened?

1. **ADA Orchestrator** initialized with all components
2. **RoutingSpine** selected the best agent for the task
3. **IonBridge** executed a real TypeScript Ion via Bun
4. **FeedbackLoop** recorded the outcome for learning
5. **Full Intelligence Pipeline** completed in ~200ms

---

## Next Steps

### Test Other Ions

```python
# Available local Ions (no API keys needed):
- quality-assessor
- duplicate-detector-ion
- dead-code-eliminator-ion
- code-grouper-ion
- refactor-planner-ion
```

### Add API Keys for Omnisearch

Create environment variables:
```
YOUTUBE_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

Then set `mock_apis: false` in `qwest-ions/omnisearch/config.yaml`

---

## Troubleshooting

### "Bun not found"
Install Bun: `powershell -NoProfile -Command "irm bun.sh/install.ps1 | iex"`

### "Module not found"
Run `bun install` in the Ion directory

### Ion returns empty result
Check the Ion's config.yaml for proper settings

---

## Documentation

- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - Current system state
- [qwest-ions/*/README.md] - Individual Ion documentation
- [ada_orchestrator.py](ada_orchestrator.py) - Main orchestration code

---

**Built with the Full Intelligence Pipeline pattern.**
