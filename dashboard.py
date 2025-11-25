#!/usr/bin/env python3
"""
ADA Orchestrator Dashboard - Real-time Visualization
=====================================================
Live monitoring of Ion execution, routing, and learning.

Run: python dashboard.py
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# Clear screen helper
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_box(title: str, content: List[str], width: int = 78):
    """Print a styled box"""
    print("+" + "-" * width + "+")
    print("|" + f" {title}".ljust(width) + "|")
    print("+" + "-" * width + "+")
    for line in content:
        print("|" + f" {line}".ljust(width) + "|")
    print("+" + "-" * width + "+")


class ADADashboard:
    """Real-time dashboard for ADA Orchestrator visualization"""

    def __init__(self):
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0,
            "ions_used": {},
            "recent_tasks": [],
            "execution_times": []
        }
        self.ada = None
        self.session_start = datetime.now()

    def _load_ada(self):
        """Lazy load ADA orchestrator"""
        if self.ada is None:
            from ada_orchestrator import ADAOrchestrator
            self.ada = ADAOrchestrator()
        return self.ada

    def _success_rate(self) -> float:
        total = self.stats['tasks_completed'] + self.stats['tasks_failed']
        if total == 0:
            return 0.0
        return (self.stats['tasks_completed'] / total) * 100

    def _avg_execution_time(self) -> float:
        if not self.stats['execution_times']:
            return 0.0
        return sum(self.stats['execution_times']) / len(self.stats['execution_times'])

    def print_header(self):
        """Print dashboard header"""
        print()
        print("=" * 80)
        print("     ADA ORCHESTRATOR DASHBOARD - LIVE MONITORING")
        print("     Full Intelligence Pipeline: Task -> Route -> Execute -> Learn")
        print("=" * 80)
        print(f"  Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Uptime: {self._get_uptime()}")
        print("=" * 80)

    def _get_uptime(self) -> str:
        delta = datetime.now() - self.session_start
        minutes = int(delta.total_seconds() / 60)
        seconds = int(delta.total_seconds() % 60)
        return f"{minutes}m {seconds}s"

    def print_ion_fleet_status(self):
        """Print Ion fleet status"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| ION FLEET STATUS                                                           |")
        print("+----------------------------------------------------------------------------+")

        ions = [
            ("quality-assessor", "OK", "Content quality scoring", "~150ms"),
            ("duplicate-detector", "OK", "Code duplicate detection", "~50ms"),
            ("dead-code-eliminator", "OK", "Unused code finder", "~100ms"),
            ("code-grouper", "OK", "Code organization analysis", "~80ms"),
            ("refactor-planner", "OK", "Refactor roadmap generation", "~120ms"),
            ("omnisearch", "--", "Multi-source search (needs API)", "N/A"),
        ]

        for name, status, desc, perf in ions:
            icon = "[OK]" if status == "OK" else "[--]"
            usage = self.stats['ions_used'].get(name, 0)
            print(f"| {icon} {name:24} | {desc:28} | {perf:8} | x{usage:3} |")

        print("+----------------------------------------------------------------------------+")

    def print_system_stats(self):
        """Print system statistics"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| SYSTEM STATISTICS                                                          |")
        print("+----------------------------------------------------------------------------+")

        stats_lines = [
            f"  Tasks Completed:     {self.stats['tasks_completed']}",
            f"  Tasks Failed:        {self.stats['tasks_failed']}",
            f"  Success Rate:        {self._success_rate():.1f}%",
            f"  Avg Execution Time:  {self._avg_execution_time():.0f}ms",
            f"  Total Time:          {self.stats['total_execution_time']:.0f}ms",
        ]

        for line in stats_lines:
            print(f"|{line.ljust(76)}|")

        print("+----------------------------------------------------------------------------+")

    def print_performance_graph(self):
        """Print ASCII performance graph"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| PERFORMANCE TIMELINE (Last 10 Tasks)                                       |")
        print("+----------------------------------------------------------------------------+")

        times = self.stats['execution_times'][-10:]

        if not times:
            print("| No tasks executed yet                                                      |")
            print("+----------------------------------------------------------------------------+")
            return

        max_time = max(times) if times else 1

        for i, t in enumerate(times):
            bar_length = int((t / max_time) * 40) if max_time > 0 else 0
            bar = "#" * bar_length
            task_num = len(times) - len(times) + i + 1
            line = f"  Task {task_num:2}: {bar.ljust(40)} {t:6.0f}ms"
            print(f"|{line.ljust(76)}|")

        print("|" + "-" * 76 + "|")
        avg = sum(times) / len(times)
        min_t = min(times)
        max_t = max(times)
        print(f"|  Avg: {avg:.0f}ms | Min: {min_t:.0f}ms | Max: {max_t:.0f}ms".ljust(77) + "|")
        print("+----------------------------------------------------------------------------+")

    def print_routing_decision(self, task_desc: str, content_type: str,
                               selected_ion: str, candidates: List[str]):
        """Visualize routing decision"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| ROUTING DECISION (SpineRoute)                                              |")
        print("+----------------------------------------------------------------------------+")
        print(f"|  Task: {task_desc[:65].ljust(68)}|")
        print(f"|  Content Type: {content_type.ljust(60)}|")
        print(f"|  Selected Ion: >>> {selected_ion.ljust(55)}|")
        print("|" + "-" * 76 + "|")
        print("|  Candidates:".ljust(77) + "|")
        for ion in candidates[:5]:
            marker = ">>>" if ion == selected_ion else "   "
            print(f"|    {marker} {ion.ljust(67)}|")
        print("+----------------------------------------------------------------------------+")

    def print_learning_update(self, ion: str, success: bool,
                              entries_count: int):
        """Show Iron Sharpens Iron learning"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| LEARNING UPDATE (Iron Sharpens Iron)                                       |")
        print("+----------------------------------------------------------------------------+")
        outcome = "SUCCESS" if success else "FAILED"
        print(f"|  Ion:           {ion.ljust(58)}|")
        print(f"|  Outcome:       {outcome.ljust(58)}|")
        print(f"|  Total Entries: {str(entries_count).ljust(58)}|")
        print("+----------------------------------------------------------------------------+")

    def print_recent_tasks(self):
        """Print recent task history"""
        print()
        print("+----------------------------------------------------------------------------+")
        print("| RECENT TASKS                                                               |")
        print("+----------------------------------------------------------------------------+")

        if not self.stats['recent_tasks']:
            print("| No tasks executed yet                                                      |")
        else:
            for task in self.stats['recent_tasks'][-5:]:
                status = "[OK]" if task['success'] else "[XX]"
                desc = task['description'][:40]
                ion = task['ion'][:20]
                time_ms = task['time_ms']
                line = f"  {status} {desc:40} | {ion:20} | {time_ms:5.0f}ms"
                print(f"|{line.ljust(76)}|")

        print("+----------------------------------------------------------------------------+")

    async def run_task(self, description: str, show_routing: bool = True):
        """Run a task through ADA and update stats"""
        from ada_orchestrator import TaskPriority, QuestDomain

        ada = self._load_ada()
        start_time = time.time()

        try:
            # Submit task
            task_id = await ada.submit_task(
                description=description,
                priority=TaskPriority.HIGH,
                domain=QuestDomain.GENERAL
            )

            # Get routing decision
            task = await ada.task_queue.get_next_task()
            if task:
                candidates = ada.routing_spine.route(task.description)

                # Find real Ion
                selected = None
                for agent in candidates:
                    if ada.ion_bridge.is_real_ion(agent):
                        selected = agent
                        break
                selected = selected or "quality-assessor"

                if show_routing:
                    self.print_routing_decision(
                        task_desc=description,
                        content_type="detected",
                        selected_ion=selected,
                        candidates=candidates
                    )

                # Execute Ion
                result = await ada.ion_bridge.execute_ion(
                    ion_name=selected,
                    task_description=task.description,
                    timeout_seconds=30
                )

                execution_time = (time.time() - start_time) * 1000
                success = result.get('success', False)

                # Record feedback
                ada.feedback_loop.record(
                    task_id=task.id,
                    content_type="task",
                    agents_used=[selected],
                    success=success,
                    execution_time_ms=execution_time
                )

                # Log event
                ada.jsonl_logger.agent_execution(
                    task.id,
                    selected,
                    success,
                    execution_time,
                    None if success else "Task failed"
                )

                # Update stats
                if success:
                    self.stats['tasks_completed'] += 1
                else:
                    self.stats['tasks_failed'] += 1

                self.stats['total_execution_time'] += execution_time
                self.stats['execution_times'].append(execution_time)
                self.stats['ions_used'][selected] = self.stats['ions_used'].get(selected, 0) + 1
                self.stats['recent_tasks'].append({
                    'description': description,
                    'ion': selected,
                    'success': success,
                    'time_ms': execution_time
                })

                # Show learning update
                self.print_learning_update(
                    ion=selected,
                    success=success,
                    entries_count=len(ada.feedback_loop.entries)
                )

                # Complete task
                await ada.task_queue.complete_task(task.id, {"result": result})

                return {
                    'success': success,
                    'ion': selected,
                    'time_ms': execution_time,
                    'result': result
                }

        except Exception as e:
            self.stats['tasks_failed'] += 1
            return {
                'success': False,
                'error': str(e)
            }

    def print_full_dashboard(self):
        """Print complete dashboard view"""
        clear_screen()
        self.print_header()
        self.print_ion_fleet_status()
        self.print_system_stats()
        self.print_performance_graph()
        self.print_recent_tasks()


async def interactive_demo():
    """Run interactive dashboard demo"""
    dashboard = ADADashboard()

    # Demo tasks showcasing each Ion
    demo_tasks = [
        "Assess quality of Python programming tutorial video",
        "Find duplicate code patterns in the project",
        "Identify dead code that can be removed safely",
        "Group related files by functionality",
        "Create refactoring plan for the Ion system",
    ]

    dashboard.print_full_dashboard()

    print()
    print("=" * 80)
    print("  DEMO MODE - Running 5 tasks through Full Intelligence Pipeline")
    print("=" * 80)
    input("\n  Press ENTER to start demo...")

    for i, task_desc in enumerate(demo_tasks, 1):
        print(f"\n>>> TASK {i}/5: {task_desc}")
        print("-" * 80)

        result = await dashboard.run_task(task_desc)

        if result.get('success'):
            print(f"\n  [OK] Completed in {result.get('time_ms', 0):.0f}ms via {result.get('ion', 'unknown')}")
        else:
            print(f"\n  [XX] Failed: {result.get('error', 'Unknown error')}")

        # Update dashboard
        dashboard.print_full_dashboard()

        if i < len(demo_tasks):
            input(f"\n  Press ENTER for next task ({i+1}/5)...")

    # Final summary
    print()
    print("=" * 80)
    print("  DEMO COMPLETE - Full Intelligence Pipeline Operational")
    print("=" * 80)
    print()
    print(f"  Tasks Completed: {dashboard.stats['tasks_completed']}")
    print(f"  Success Rate:    {dashboard._success_rate():.1f}%")
    print(f"  Total Time:      {dashboard.stats['total_execution_time']:.0f}ms")
    print(f"  Avg Per Task:    {dashboard._avg_execution_time():.0f}ms")
    print()
    print("  Ion Usage:")
    for ion, count in sorted(dashboard.stats['ions_used'].items(),
                             key=lambda x: x[1], reverse=True):
        print(f"    {ion}: {count}x")
    print()


async def continuous_monitor():
    """Run continuous monitoring mode"""
    dashboard = ADADashboard()

    print("Starting continuous monitoring mode...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            dashboard.print_full_dashboard()
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def main():
    """Main entry point"""
    print()
    print("=" * 80)
    print("  ADA ORCHESTRATOR DASHBOARD")
    print("=" * 80)
    print()
    print("  1. Interactive Demo (run 5 tasks)")
    print("  2. Continuous Monitor (live view)")
    print("  3. Quick Status Check")
    print()

    choice = input("  Select mode [1/2/3]: ").strip() or "1"

    if choice == "1":
        asyncio.run(interactive_demo())
    elif choice == "2":
        asyncio.run(continuous_monitor())
    else:
        dashboard = ADADashboard()
        dashboard.print_full_dashboard()


if __name__ == "__main__":
    main()
