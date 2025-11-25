#!/usr/bin/env python3
"""
LearnQwest Full Intelligence Pipeline Demo
==========================================
Shows all working components in action.

Run: python demo_pipeline.py
"""

import asyncio
import json
from datetime import datetime
from ada_orchestrator import (
    ADAOrchestrator,
    TaskPriority,
    QuestDomain
)


def banner(text: str):
    """Print a formatted banner"""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def section(text: str):
    """Print a section header"""
    print()
    print(f">>> {text}")
    print("-" * 40)


async def demo_full_pipeline():
    """Demonstrate the Full Intelligence Pipeline"""

    banner("LEARNQWEST FULL INTELLIGENCE PIPELINE DEMO")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize ADA
    section("1. INITIALIZING ADA ORCHESTRATOR")
    ada = ADAOrchestrator()

    print(f"  Components loaded:")
    print(f"    - RoutingSpine: Active")
    print(f"    - IonBridge: {len(ada.ion_bridge.list_ions())} Ions available")
    print(f"    - FeedbackLoop: {len(ada.feedback_loop.entries)} historical entries")
    print(f"    - JSONLLogger: Writing to {ada.jsonl_logger.log_file}")
    print(f"    - TaskQueue: Max {ada.task_queue.max_concurrent} concurrent")

    # Show available Ions
    section("2. AVAILABLE IONS")
    for ion in ada.ion_bridge.list_ions():
        print(f"    [{ion}]")

    # Submit a test task
    section("3. SUBMITTING TASK")
    task_description = "Analyze Python code quality and suggest improvements"

    task_id = await ada.submit_task(
        description=task_description,
        priority=TaskPriority.HIGH,
        domain=QuestDomain.GENERAL
    )
    print(f"  Task ID: {task_id[:8]}...")
    print(f"  Description: {task_description}")
    print(f"  Priority: HIGH")

    # Get and process task
    section("4. ROUTING TASK (SpineRoute)")
    task = await ada.task_queue.get_next_task()

    if task:
        agents = ada.routing_spine.route(task.description)
        print(f"  Candidates: {agents}")

        # Find real Ion
        selected = None
        for agent in agents:
            if ada.ion_bridge.is_real_ion(agent):
                selected = agent
                break
        selected = selected or "quality-assessor"

        print(f"  Selected: {selected}")

        # Execute Ion
        section("5. EXECUTING ION (IonExecute)")
        print(f"  Running: {selected}")
        print(f"  Method: Bun subprocess")

        result = await ada.ion_bridge.execute_ion(
            ion_name=selected,
            task_description=task.description,
            timeout_seconds=30
        )

        print(f"  Success: {result['success']}")
        print(f"  Time: {result['execution_time_ms']:.0f}ms")

        # Record feedback
        section("6. RECORDING FEEDBACK (IronLoop)")
        ada.feedback_loop.record(
            task_id=task.id,
            content_type="code_analysis",
            agents_used=[selected],
            success=result['success'],
            execution_time_ms=result['execution_time_ms']
        )
        print(f"  Recorded for task: {task.id[:8]}...")
        print(f"  Total feedback entries: {len(ada.feedback_loop.entries)}")

        # Log event
        section("7. LOGGING EVENT (StreamLog)")
        ada.jsonl_logger.agent_execution(
            task.id,
            selected,
            result['success'],
            result['execution_time_ms'],
            None
        )
        print(f"  Event logged to: {ada.jsonl_logger.log_file}")

        # Complete task
        section("8. COMPLETING TASK")
        await ada.task_queue.complete_task(task.id, {"result": result})
        print(f"  Task marked complete")
        print(f"  Queue status: {len(ada.task_queue.queue)} pending, {len(ada.task_queue.completed_tasks)} completed")

    # Final summary
    banner("DEMO COMPLETE - FULL PIPELINE OPERATIONAL")
    print()
    print("  Components Demonstrated:")
    print("    [x] ADA Orchestrator - Main coordinator")
    print("    [x] RoutingSpine - Smart agent selection")
    print("    [x] IonBridge - Python->Bun execution")
    print("    [x] FeedbackLoop - Learning from outcomes")
    print("    [x] JSONLLogger - Complete audit trail")
    print("    [x] TaskQueue - Priority management")
    print()
    print("  Pipeline Flow:")
    print("    Task -> Route -> Execute -> Feedback -> Log -> Complete")
    print()
    print("  This is the Full Intelligence Pipeline.")
    print()


async def demo_multiple_tasks():
    """Demo processing multiple tasks"""

    banner("MULTI-TASK DEMO")

    ada = ADAOrchestrator()

    tasks = [
        "Assess quality of documentation",
        "Find duplicate code patterns",
        "Analyze code organization",
    ]

    section("SUBMITTING 3 TASKS")
    task_ids = []
    for desc in tasks:
        tid = await ada.submit_task(
            description=desc,
            priority=TaskPriority.NORMAL,
            domain=QuestDomain.GENERAL
        )
        task_ids.append(tid)
        print(f"  [{tid[:8]}] {desc[:40]}...")

    section("PROCESSING TASKS")
    for _ in range(len(tasks)):
        task = await ada.task_queue.get_next_task()
        if task:
            agents = ada.routing_spine.route(task.description)
            selected = next(
                (a for a in agents if ada.ion_bridge.is_real_ion(a)),
                "quality-assessor"
            )

            result = await ada.ion_bridge.execute_ion(selected, task.description)

            print(f"  [{task.id[:8]}] {selected}: {'OK' if result['success'] else 'FAIL'} ({result['execution_time_ms']:.0f}ms)")

            await ada.task_queue.complete_task(task.id, {"result": result})

    print()
    print(f"  Completed: {len(ada.task_queue.completed_tasks)}/{len(tasks)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LearnQwest Demo - Choose Mode")
    print("="*60)
    print("  1. Full Pipeline Demo (detailed)")
    print("  2. Multi-Task Demo (speed)")
    print("  3. Both")
    print()

    choice = input("  Enter choice (1/2/3) [default=1]: ").strip() or "1"

    if choice == "1":
        asyncio.run(demo_full_pipeline())
    elif choice == "2":
        asyncio.run(demo_multiple_tasks())
    else:
        asyncio.run(demo_full_pipeline())
        asyncio.run(demo_multiple_tasks())
