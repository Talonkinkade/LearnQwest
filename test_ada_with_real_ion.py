#!/usr/bin/env python3
"""
Test ADA with Real Quality-Assessor Ion
"""
import asyncio
import json
from ada_orchestrator import ADAOrchestrator, TaskPriority, QuestDomain


async def test_real_ion():
    print("=" * 60)
    print("  TESTING ADA WITH REAL QUALITY-ASSESSOR ION")
    print("=" * 60)
    print()

    # Initialize ADA
    ada = ADAOrchestrator()
    print(f"✅ ADA initialized")
    print(f"✅ IonBridge found {len(ada.ion_bridge.available_ions)} Ions:")
    for ion in ada.ion_bridge.available_ions:
        print(f"   - {ion}")
    print()

    # Submit a task that will route to quality-assessor
    print("📤 Submitting task...")
    task_id = await ada.submit_task(
        description="Assess the quality of Python tutorial content for beginners",
        priority=TaskPriority.HIGH,
        domain=QuestDomain.GENERAL,
    )
    print(f"✅ Task submitted: {task_id}")
    print()

    # Start ADA's task processor
    await ada.start()

    # Wait for task to complete
    print("⚙️  Processing task through Full Intelligence Pipeline™...")
    print("   Question → Classify → Steps → Execute → Log → Learn")
    print()

    # Wait for task to be processed
    await asyncio.sleep(2)

    # Get task result
    task = ada.task_queue.completed_tasks.get(task_id)
    if not task:
        print("⚠️  Task still processing or not found")
        await ada.stop()
        return None

    result = task.results
    await ada.stop()

    print()
    print("=" * 60)
    print("  RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    print()

    # Check if real Ion was used
    if result.get("outputs"):
        for output in result["outputs"]:
            if output.get("agent_name") == "quality-assessor":
                if output.get("status") == "success":
                    print("🎉 SUCCESS! Real Quality-Assessor Ion executed!")
                    print(f"⏱️  Execution time: {output.get('execution_time', 0):.3f}s")
                else:
                    print(f"⚠️  Ion execution failed: {output.get('error')}")

    return result


if __name__ == "__main__":
    asyncio.run(test_real_ion())
