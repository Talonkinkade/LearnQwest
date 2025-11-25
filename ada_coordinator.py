#!/usr/bin/env python3
"""
ADA Coordinator - The Orchestration Engine
==========================================
This is what replaces Link as the orchestrator.

Takes high-level tasks and coordinates:
1. Task decomposition (ALPHA's work)
2. Ion execution (existing ADA infrastructure)
3. Output synthesis (BRAVO's work)

Usage:
    from ada_coordinator import ADACoordinator

    coordinator = ADACoordinator()
    report = await coordinator.execute("Analyze the LearnQwest codebase")
    print(coordinator.format_report(report))

One command, one answer, zero manual coordination.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json
import time

# Import our components
from ada_orchestrator import ADAOrchestrator, TaskPriority, QuestDomain
from ada_task_decomposer import TaskDecomposer, TaskPlan, SubTask, TaskPattern
from ada_output_synthesizer import OutputSynthesizer, IonOutput, SynthesizedReport


@dataclass
class ExecutionTrace:
    """Tracks detailed execution info for observability"""

    wave: int
    ion_name: str
    status: str  # "STARTED" | "SUCCESS" | "FAILED"
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class ExecutionMetrics:
    """Track execution performance"""

    start_time: datetime
    end_time: Optional[datetime] = None
    total_subtasks: int = 0
    successful_subtasks: int = 0
    failed_subtasks: int = 0
    total_execution_ms: float = 0
    waves_executed: int = 0

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    @property
    def success_rate(self) -> float:
        if self.total_subtasks == 0:
            return 0
        return self.successful_subtasks / self.total_subtasks


class ExecutionStrategy:
    """Determines how to execute subtasks (parallel vs sequential)"""

    @staticmethod
    def create_execution_plan(subtasks: List[SubTask]) -> List[List[SubTask]]:
        """
        Group subtasks into execution waves.

        Tasks in the same wave can run in parallel.
        Waves execute sequentially (wave 2 waits for wave 1).

        Returns:
            List of task waves (each wave executes in parallel)
        """
        if not subtasks:
            return []

        # Build set of completed task names as we go
        completed = set()
        waves = []
        remaining = subtasks.copy()

        while remaining:
            # Find tasks ready to execute (no dependencies or dependencies satisfied)
            ready = []
            for task in remaining:
                if not task.depends_on:
                    ready.append(task)
                elif all(dep in completed for dep in task.depends_on):
                    ready.append(task)

            if not ready:
                # Circular dependency or unresolvable - execute remaining anyway
                print(
                    f"[WARN] Could not resolve dependencies, executing {len(remaining)} remaining tasks"
                )
                ready = remaining.copy()

            waves.append(ready)

            # Mark these as completed for next iteration
            for task in ready:
                completed.add(task.ion_name)
                remaining.remove(task)

        return waves

    @staticmethod
    def optimize_wave(wave: List[SubTask]) -> List[SubTask]:
        """
        Optimize a wave for execution.
        Sort by priority (lower number = higher priority).
        """
        return sorted(wave, key=lambda t: t.priority)


class ADACoordinator:
    """
    Main coordinator - This is the brain that replaces Link's manual orchestration.

    Flow:
    1. Receive high-level task from Link
    2. Decompose into Ion-executable subtasks (TaskDecomposer)
    3. Execute Ions (parallel where possible via existing ADA)
    4. Synthesize outputs into one report (OutputSynthesizer)
    5. Return coherent answer to Link

    Example:
        coordinator = ADACoordinator()
        report = await coordinator.execute("Analyze the codebase", verbose=True)
        print(coordinator.format_report(report))
    """

    # Map decomposer Ion names to actual Ion directory names
    ION_NAME_MAP = {
        "duplicate-detector": "duplicate-detector-ion",
        "dead-code-eliminator": "dead-code-eliminator-ion",
        "code-grouper": "code-grouper-ion",
        "refactor-planner": "refactor-planner-ion",
        # ALPHA's new Ions (Nov 25, 2025)
        "content-fetcher": "content-fetcher-ion",
        "context-builder": "context-builder-ion",
        "quiz-generator": "quiz-generator-ion",
    }

    def __init__(self):
        self.ada = ADAOrchestrator()
        self.decomposer = TaskDecomposer()
        self.synthesizer = OutputSynthesizer()
        self.execution_history: List[Dict[str, Any]] = []
        self._verbose = False

    def _resolve_ion_name(self, ion_name: str) -> str:
        """Resolve Ion name from decomposer to actual Ion directory name"""
        return self.ION_NAME_MAP.get(ion_name, ion_name)

    async def execute(
        self,
        task: str,
        verbose: bool = False,
        timeout_seconds: int = 300,
        trace: bool = False,
    ) -> SynthesizedReport:
        """
        Main execution method - THE ONE METHOD Link calls.

        Args:
            task: High-level task description (e.g., "Analyze the codebase")
            verbose: Print execution details to console
            timeout_seconds: Maximum time for entire execution
            trace: Enable execution trace collection

        Returns:
            SynthesizedReport combining all Ion outputs into one coherent report
        """
        self._verbose = verbose
        metrics = ExecutionMetrics(start_time=datetime.now())

        if verbose:
            self._print_header(task)

        try:
            # Step 1: Decompose task
            if verbose:
                self._print_step(1, "Task Decomposition")

            task_plan = self.decomposer.decompose(task)
            metrics.total_subtasks = len(task_plan.subtasks)

            if verbose:
                self._print_decomposition(task_plan)

            # Step 2: Create execution plan
            if verbose:
                self._print_step(2, "Creating Execution Plan")

            execution_waves = ExecutionStrategy.create_execution_plan(
                task_plan.subtasks
            )
            metrics.waves_executed = len(execution_waves)

            if verbose:
                self._print_execution_plan(execution_waves)

            # Step 3: Execute Ions
            if verbose:
                self._print_step(3, "Executing Ions")

            all_outputs = []
            # Track results from previous waves for orchestrator Ions
            previous_wave_results = {}
            # Initialize trace collector
            execution_trace = [] if trace else None

            for wave_num, wave in enumerate(execution_waves, 1):
                if verbose:
                    print(f"\n  Wave {wave_num}/{len(execution_waves)}:")

                # Execute wave with timeout, passing previous results
                try:
                    wave_outputs = await asyncio.wait_for(
                        self._execute_wave(
                            wave, wave_num, previous_wave_results, execution_trace
                        ),
                        timeout=timeout_seconds / len(execution_waves),
                    )
                    all_outputs.extend(wave_outputs)

                    # Store results from this wave for next wave
                    for output in wave_outputs:
                        if output.success:
                            # Store by base Ion name (without -ion suffix)
                            base_name = output.ion_name.replace("-ion", "")
                            previous_wave_results[base_name] = output.result

                    # Update metrics
                    for output in wave_outputs:
                        metrics.total_execution_ms += output.execution_time_ms
                        if output.success:
                            metrics.successful_subtasks += 1
                        else:
                            metrics.failed_subtasks += 1

                except asyncio.TimeoutError:
                    if verbose:
                        print(f"  [TIMEOUT] Wave {wave_num} timed out")
                    # Create failed outputs for remaining tasks in wave
                    for subtask in wave:
                        all_outputs.append(
                            IonOutput(
                                ion_name=subtask.ion_name,
                                description=subtask.description,
                                success=False,
                                result={"error": "Timeout"},
                                execution_time_ms=0,
                                timestamp=datetime.now(),
                                error="Execution timeout",
                            )
                        )
                        metrics.failed_subtasks += 1

            if verbose:
                self._print_execution_summary(metrics)

            # Step 4: Synthesize results
            if verbose:
                self._print_step(4, "Synthesizing Results")

            report = self.synthesizer.synthesize(
                task_pattern=task_plan.pattern.value, ion_outputs=all_outputs
            )

            if verbose:
                print(f"  Report generated: {report.title}")
                print(f"  Sections: {len(report.sections)}")
                print(f"  Recommendations: {len(report.recommendations)}")

            # Step 5: Record history
            metrics.end_time = datetime.now()
            self._record_history(task, task_plan, metrics, all_outputs)

            # Display and store trace if requested
            if trace and execution_trace:
                self._display_execution_trace(execution_trace)
                report.execution_trace = execution_trace

            if verbose:
                self._print_footer(metrics)

            return report

        except Exception as e:
            metrics.end_time = datetime.now()
            if verbose:
                print(f"\n  [ERROR] Execution failed: {e}")

            # Return error report
            return SynthesizedReport(
                title="Execution Error",
                summary=f"Task execution failed: {str(e)}",
                sections=[
                    {
                        "title": "Error Details",
                        "icon": "[ERR]",
                        "content": str(e),
                        "priority": "high",
                    }
                ],
                metadata={
                    "error": str(e),
                    "task": task,
                    "duration_seconds": metrics.duration_seconds,
                },
                raw_outputs=[],
                recommendations=["Review the error and retry"],
            )

    async def _execute_wave(
        self,
        wave: List[SubTask],
        wave_num: int,
        previous_results: Optional[Dict[str, Any]] = None,
        trace_list: Optional[List[ExecutionTrace]] = None,
    ) -> List[IonOutput]:
        """Execute a wave of subtasks in parallel

        Args:
            wave: List of subtasks to execute
            wave_num: Current wave number (for trace)
            previous_results: Results from previous waves (for orchestrator Ions)
            trace_list: Execution trace collector
        """
        # Optimize wave order
        wave = ExecutionStrategy.optimize_wave(wave)

        # Create trace entries for each subtask (STARTED)
        if trace_list is not None:
            for subtask in wave:
                trace_entry = ExecutionTrace(
                    wave=wave_num,
                    ion_name=subtask.ion_name,
                    status="STARTED",
                    start_time=time.time(),
                )
                trace_list.append(trace_entry)

        # Create coroutines for parallel execution, passing previous results
        tasks = [
            self._execute_subtask(subtask, previous_results, wave_num, trace_list)
            for subtask in wave
        ]

        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert results to IonOutput objects
        outputs = []
        for subtask, result in zip(wave, results):
            if isinstance(result, Exception):
                # Update trace entry for exception
                if trace_list is not None:
                    for trace_entry in reversed(trace_list):
                        if (
                            trace_entry.ion_name == subtask.ion_name
                            and trace_entry.wave == wave_num
                            and trace_entry.end_time is None
                        ):
                            trace_entry.end_time = time.time()
                            trace_entry.duration_ms = int(
                                (trace_entry.end_time - trace_entry.start_time) * 1000
                            )
                            trace_entry.status = "FAILED"
                            trace_entry.error_message = str(result)
                            break

                outputs.append(
                    IonOutput(
                        ion_name=subtask.ion_name,
                        description=subtask.description,
                        success=False,
                        result={"error": str(result)},
                        execution_time_ms=0,
                        timestamp=datetime.now(),
                        error=str(result),
                    )
                )
            else:
                outputs.append(result)

        return outputs

    async def _execute_subtask(
        self,
        subtask: SubTask,
        previous_results: Optional[Dict[str, Any]] = None,
        wave_num: int = 1,
        trace_list: Optional[List[ExecutionTrace]] = None,
    ) -> IonOutput:
        """Execute a single subtask via ADA infrastructure

        Args:
            subtask: The subtask to execute
            previous_results: Results from previous waves (for orchestrator Ions)
            wave_num: Current wave number (for trace)
            trace_list: Execution trace collector
        """
        start_time = datetime.now()

        # Resolve the Ion name (handle decomposer vs actual Ion naming)
        resolved_ion = self._resolve_ion_name(subtask.ion_name)

        if self._verbose:
            print(f"    -> {subtask.ion_name}... ", end="", flush=True)

        try:
            # Check if this is a real Ion we can execute
            if self.ada.ion_bridge.is_real_ion(resolved_ion):
                # Execute via IonBridge with resolved name, passing previous results
                result = await self.ada.ion_bridge.execute_ion(
                    ion_name=resolved_ion,
                    task_description=subtask.description,
                    timeout_seconds=30,
                    previous_results=previous_results,
                )

                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                success = result.get("success", False)

                # Update trace entry (SUCCESS/FAILED)
                if trace_list is not None:
                    for trace_entry in reversed(trace_list):
                        if (
                            trace_entry.ion_name == subtask.ion_name
                            and trace_entry.wave == wave_num
                            and trace_entry.end_time is None
                        ):
                            trace_entry.end_time = time.time()
                            trace_entry.duration_ms = int(
                                (trace_entry.end_time - trace_entry.start_time) * 1000
                            )
                            trace_entry.status = "SUCCESS" if success else "FAILED"
                            # Extract token usage if available
                            if (
                                "metadata" in result
                                and "tokens_used" in result["metadata"]
                            ):
                                trace_entry.tokens_used = result["metadata"][
                                    "tokens_used"
                                ]
                                trace_entry.cost_usd = self._calculate_cost(
                                    trace_entry.tokens_used
                                )
                            if not success and "error" in result:
                                trace_entry.error_message = result["error"]
                            break

                if self._verbose:
                    status = "[OK]" if success else "[XX]"
                    print(f"{status} ({execution_time:.0f}ms)")

                # Record feedback for learning
                self.ada.feedback_loop.record(
                    task_id=f"coord-{subtask.ion_name}-{start_time.timestamp()}",
                    content_type=subtask.ion_name,
                    agents_used=[subtask.ion_name],
                    success=success,
                    execution_time_ms=execution_time,
                )

                return IonOutput(
                    ion_name=subtask.ion_name,
                    description=subtask.description,
                    success=success,
                    result=result.get("result", result),
                    execution_time_ms=int(execution_time),
                    timestamp=datetime.now(),
                )
            else:
                # Simulate for Ions we don't have yet
                execution_time = 50  # Simulated
                if self._verbose:
                    print(f"[SIM] ({execution_time}ms)")

                return IonOutput(
                    ion_name=subtask.ion_name,
                    description=subtask.description,
                    success=True,
                    result={
                        "simulated": True,
                        "message": f"Simulated {subtask.ion_name} execution",
                    },
                    execution_time_ms=execution_time,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            if self._verbose:
                print(f"[ERR] {str(e)[:30]}")

            return IonOutput(
                ion_name=subtask.ion_name,
                description=subtask.description,
                success=False,
                result={"error": str(e)},
                execution_time_ms=int(execution_time),
                timestamp=datetime.now(),
                error=str(e),
            )

    def _record_history(
        self,
        task: str,
        plan: TaskPlan,
        metrics: ExecutionMetrics,
        outputs: List[IonOutput],
    ):
        """Record execution in history for analysis"""
        self.execution_history.append(
            {
                "task": task,
                "pattern": plan.pattern.value,
                "timestamp": metrics.start_time.isoformat(),
                "duration_seconds": metrics.duration_seconds,
                "total_subtasks": metrics.total_subtasks,
                "successful_subtasks": metrics.successful_subtasks,
                "failed_subtasks": metrics.failed_subtasks,
                "success_rate": metrics.success_rate,
                "waves_executed": metrics.waves_executed,
                "total_execution_ms": metrics.total_execution_ms,
                "ions_used": [o.ion_name for o in outputs],
            }
        )

    # =========================================================================
    # Output Formatting
    # =========================================================================

    def format_report(self, report: SynthesizedReport, format: str = "text") -> str:
        """Format report for display"""
        if format == "text":
            return self.synthesizer.format_as_text(report)
        elif format == "markdown":
            return self.synthesizer.format_as_markdown(report)
        elif format == "json":
            return self.synthesizer.format_as_json(report)
        elif format == "html":
            return self.synthesizer.format_as_html(report)
        else:
            return self.synthesizer.format_as_text(report)

    def save_report(
        self, report: SynthesizedReport, path: Path, format: str = "text"
    ) -> Path:
        """Save report to file"""
        return self.synthesizer.save_report(report, path, format)

    def _calculate_cost(self, tokens: int, model: str = "claude-sonnet-4") -> float:
        """Calculate cost based on token usage

        Claude Sonnet 4 pricing (approximate):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        - Using average: $9 per million tokens
        """
        cost_per_million = 9.0
        return (tokens / 1_000_000) * cost_per_million

    # =========================================================================
    # History & Status
    # =========================================================================

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]

    def print_history(self):
        """Print execution history"""
        print("\n" + "=" * 80)
        print("  ADA COORDINATOR - EXECUTION HISTORY")
        print("=" * 80)

        if not self.execution_history:
            print("\n  No tasks executed yet.\n")
            return

        for i, entry in enumerate(self.execution_history[-10:], 1):
            print(f"\n  {i}. {entry['task'][:50]}")
            print(f"     Pattern: {entry['pattern']}")
            print(f"     Time: {entry['duration_seconds']:.2f}s")
            print(
                f"     Success: {entry['success_rate']:.0%} ({entry['successful_subtasks']}/{entry['total_subtasks']})"
            )
            print(f"     Ions: {', '.join(entry['ions_used'][:5])}")

        print()

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status"""
        return {
            "ada_status": "online",
            "decomposer_patterns": len(self.decomposer.patterns),
            "synthesizer_patterns": len(self.synthesizer.synthesizers),
            "available_ions": self.ada.ion_bridge.list_ions(),
            "real_ions": [
                ion
                for ion in self.ada.ion_bridge.list_ions()
                if self.ada.ion_bridge.is_real_ion(ion)
            ],
            "executions_total": len(self.execution_history),
            "last_execution": (
                self.execution_history[-1] if self.execution_history else None
            ),
        }

    # =========================================================================
    # Verbose Output Helpers
    # =========================================================================

    def _print_header(self, task: str):
        """Print execution header"""
        print()
        print("=" * 80)
        print("  ADA COORDINATOR - Multi-Ion Orchestration")
        print("=" * 80)
        print(f"\n  Task: {task}")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _print_step(self, num: int, name: str):
        """Print step header"""
        icons = {1: "[1]", 2: "[2]", 3: "[3]", 4: "[4]", 5: "[5]"}
        print(f"\n{icons.get(num, '[*]')} STEP {num}: {name}")
        print("-" * 80)

    def _print_decomposition(self, plan: TaskPlan):
        """Print decomposition results"""
        print(f"  Pattern: {plan.pattern.value}")
        print(f"  Subtasks: {len(plan.subtasks)}")
        print(f"  Est. time: {plan.estimated_time_seconds}s")
        print()
        for i, subtask in enumerate(plan.subtasks, 1):
            deps = (
                f" (depends: {', '.join(subtask.depends_on)})"
                if subtask.depends_on
                else ""
            )
            parallel = "[P]" if subtask.can_parallelize else "[S]"
            print(
                f"  {i}. {parallel} {subtask.ion_name} - {subtask.description[:40]}{deps}"
            )

    def _print_execution_plan(self, waves: List[List[SubTask]]):
        """Print execution plan"""
        print(f"  Execution waves: {len(waves)}")
        for i, wave in enumerate(waves, 1):
            ion_names = [t.ion_name for t in wave]
            mode = "parallel" if len(wave) > 1 else "single"
            print(f"    Wave {i}: [{mode}] {', '.join(ion_names)}")

    def _print_execution_summary(self, metrics: ExecutionMetrics):
        """Print execution summary"""
        print()
        print(
            f"  Completed: {metrics.successful_subtasks}/{metrics.total_subtasks} successful"
        )
        print(f"  Total Ion time: {metrics.total_execution_ms:.0f}ms")

    def _print_footer(self, metrics: ExecutionMetrics):
        """Print execution footer"""
        print()
        print("=" * 80)
        print("  EXECUTION COMPLETE")
        print("=" * 80)
        print(f"  Duration: {metrics.duration_seconds:.2f}s")
        print(f"  Success rate: {metrics.success_rate:.0%}")
        print()

    def _display_execution_trace(self, trace: List[ExecutionTrace]) -> None:
        """Display execution trace in Dan's observability style"""

        print("\n" + "=" * 80)
        print("  EXECUTION TRACE")
        print("=" * 80 + "\n")

        # Group by wave
        waves: Dict[int, List[ExecutionTrace]] = {}
        for entry in trace:
            if entry.wave not in waves:
                waves[entry.wave] = []
            waves[entry.wave].append(entry)

        # Display each wave
        for wave_num in sorted(waves.keys()):
            wave_entries = waves[wave_num]

            # Determine if parallel or sequential
            wave_type = "Parallel" if len(wave_entries) > 1 else "Sequential"

            print(f"Wave {wave_num} ({wave_type}):")

            for entry in wave_entries:
                # Status icon (ASCII-safe for Windows compatibility)
                if entry.status == "SUCCESS":
                    icon = "OK"
                elif entry.status == "FAILED":
                    icon = "XX"
                else:
                    icon = "->"

                # Format output line
                ion_display = f"{entry.ion_name:<30}"
                time_display = f"{entry.duration_ms:>6}ms" if entry.duration_ms else "    --ms"

                if entry.tokens_used:
                    token_display = f"{entry.tokens_used:>6} tokens"
                    cost_display = f"${entry.cost_usd:.4f}" if entry.cost_usd else "$-.----"
                else:
                    token_display = "   --- tokens"
                    cost_display = "$-.----"

                print(f"  [{icon}] {ion_display} {time_display}  {token_display}  {cost_display}")

                # Show error if failed
                if entry.status == "FAILED" and entry.error_message:
                    print(f"      Error: {entry.error_message}")

            print()  # Blank line between waves

        # Calculate totals
        total_time_ms = sum(e.duration_ms for e in trace if e.duration_ms)
        total_tokens = sum(e.tokens_used for e in trace if e.tokens_used)
        total_cost = sum(e.cost_usd for e in trace if e.cost_usd)

        success_count = sum(1 for e in trace if e.status == "SUCCESS")
        total_count = len(trace)

        print("-" * 80)
        print(
            f"Total: {total_time_ms/1000:.1f}s | "
            f"{total_tokens} tokens | "
            f"${total_cost:.4f} | "
            f"{success_count}/{total_count} successful"
        )
        print("=" * 80 + "\n")


# =============================================================================
# Convenience Functions
# =============================================================================


async def quick_execute(task: str, verbose: bool = True) -> SynthesizedReport:
    """Quick execution helper"""
    coordinator = ADACoordinator()
    return await coordinator.execute(task, verbose=verbose)


# =============================================================================
# CLI Demo
# =============================================================================


async def demo():
    """Demonstrate the coordinator"""
    print()
    print("=" * 80)
    print("  ADA COORDINATOR DEMO")
    print("  One command -> Multiple Ions -> One coherent report")
    print("=" * 80)

    coordinator = ADACoordinator()

    # Show status
    status = coordinator.get_status()
    print(f"\n  Available Ions: {len(status['available_ions'])}")
    print(f"  Real Ions: {len(status['real_ions'])}")
    print(f"  Decomposer patterns: {status['decomposer_patterns']}")
    print(f"  Synthesizer patterns: {status['synthesizer_patterns']}")

    # Demo tasks
    demo_tasks = [
        "Analyze the LearnQwest codebase for duplicates and dead code",
        "Research agent orchestration patterns",
    ]

    for task in demo_tasks:
        print()
        print("=" * 80)
        input(f"  Press ENTER to execute: '{task[:50]}...'")

        report = await coordinator.execute(task, verbose=True)

        print()
        print("=" * 80)
        print("  FINAL REPORT")
        print("=" * 80)
        print(coordinator.format_report(report, "text"))

    # Show history
    coordinator.print_history()

    print()
    print("=" * 80)
    print("  DEMO COMPLETE")
    print("=" * 80)
    print("  The coordinator is ready. Link can now use:")
    print()
    print('    report = await coordinator.execute("your task here")')
    print("    print(coordinator.format_report(report))")
    print()


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo())
    elif len(sys.argv) > 1:
        # Execute task from command line
        task = " ".join(sys.argv[1:])
        print(f"Executing: {task}")

        async def run():
            coordinator = ADACoordinator()
            report = await coordinator.execute(task, verbose=True)
            print("\n" + coordinator.format_report(report))

        asyncio.run(run())
    else:
        print("ADA Coordinator - Multi-Ion Orchestration")
        print()
        print("Usage:")
        print("  python ada_coordinator.py demo              Run interactive demo")
        print("  python ada_coordinator.py <task>            Execute a task")
        print()
        print("Example:")
        print('  python ada_coordinator.py "Analyze the codebase"')
        print()
        print("Or use in Python:")
        print("  from ada_coordinator import ADACoordinator")
        print("  coordinator = ADACoordinator()")
        print('  report = await coordinator.execute("your task")')


if __name__ == "__main__":
    main()
