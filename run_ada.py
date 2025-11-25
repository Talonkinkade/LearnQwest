#!/usr/bin/env python3
"""
ADA CLI - Simple command-line interface for Multi-Ion Orchestration

DELTA's Mission - Just make it work!

Usage:
    # Natural language (backward compatible)
    python run_ada.py "Analyze the codebase"
    python run_ada.py "Create a quiz about fractions"

    # Named workflows (new!)
    python run_ada.py create-quiz --topic "photosynthesis" --grade-level 6
    python run_ada.py audit-codebase
    python run_ada.py --help
    python run_ada.py --status
"""
import sys
import asyncio
from ada_coordinator import ADACoordinator
from workflow_library import (
    build_task_from_workflow,
    list_workflows,
    get_workflow_help,
    WorkflowError,
)


def print_help(workflow_name=None):
    """Print help message"""
    # Workflow-specific help
    if workflow_name:
        try:
            help_text = get_workflow_help(workflow_name)
            print()
            print(help_text)
            print()
            return
        except WorkflowError as e:
            print(f"\nError: {e}\n")
            return

    # General help
    print()
    print("=" * 70)
    print("  ADA CLI - Multi-Ion Orchestration")
    print("=" * 70)
    print()
    print("Usage:")
    print("  # Natural language (backward compatible)")
    print("  python run_ada.py <task>")
    print()
    print("  # Named workflows (new!)")
    print("  python run_ada.py <workflow> [options]")
    print("  python run_ada.py <workflow> --help")
    print()
    print("  # System commands")
    print("  python run_ada.py --help           Show this help")
    print("  python run_ada.py --status         Show system status")
    print("  python run_ada.py --workflows      List all workflows")
    print()
    print("  # Flags (can be combined)")
    print("  --quiet, -q                        Execute without verbose output")
    print("  --trace, -t                        Show execution trace")
    print()
    print("Examples (Natural Language):")
    print('  python run_ada.py "Analyze the codebase"')
    print('  python run_ada.py "Create a quiz about photosynthesis"')
    print('  python run_ada.py "Audit the codebase" --trace')
    print()
    print("Examples (Named Workflows):")
    print('  python run_ada.py create-quiz --topic "photosynthesis" --grade-level 6')
    print("  python run_ada.py audit-codebase")
    print('  python run_ada.py find-duplicates --path "./src"')
    print("  python run_ada.py create-quiz --help")
    print()
    print("Available Workflows:")
    workflows = list_workflows()
    for wf in workflows:
        print(f"  - {wf}")
    print()
    print("  Use 'python run_ada.py <workflow> --help' for workflow details")
    print()
    print("=" * 70)


def print_status():
    """Print system status"""
    coordinator = ADACoordinator()

    print()
    print("=" * 60)
    print("  ADA System Status")
    print("=" * 60)
    print()
    print("  Decomposer:  Ready")
    print("  Synthesizer: Ready")
    print("  Orchestrator: Ready")
    print()
    print("  Available Ions:")
    for ion in coordinator.ada.ion_bridge.list_ions():
        print(f"    - {ion}")
    print()

    # Calculate success rate from feedback entries
    entries = coordinator.ada.feedback_loop.entries
    if entries:
        success_count = sum(1 for e in entries if e.success)
        success_rate = (success_count / len(entries)) * 100
        print(f"  Feedback entries: {len(entries)}")
        print(f"  Success rate: {success_rate:.1f}%")
    else:
        print("  Feedback entries: 0")
        print("  Success rate: N/A")
    print()
    print("=" * 60)


async def execute_task(task: str, verbose: bool = True, trace: bool = False):
    """Execute a task and print the report"""
    coordinator = ADACoordinator()

    if verbose:
        print()

    report = await coordinator.execute(task, verbose=verbose, trace=trace)

    # Print formatted report (unless trace-only mode)
    if not trace or verbose:
        formatted = coordinator.format_report(report, format="text")
        print(formatted)

    return report


def main():
    """Main entry point"""
    # No arguments - show help
    if len(sys.argv) < 2:
        print_help()
        return

    # Parse arguments
    args = sys.argv[1:]
    verbose = True
    trace = False
    workflow_params = {}
    task_parts = []

    # Check for workflow command first
    workflows = list_workflows()
    is_workflow = args[0] in workflows
    workflow_name = args[0] if is_workflow else None

    # Parse all arguments
    i = 0
    while i < len(args):
        arg = args[i]

        # Global flags
        if arg in ("--help", "-h"):
            if workflow_name:
                print_help(workflow_name)
            else:
                print_help()
            return
        elif arg == "--workflows":
            print("\nAvailable workflows:")
            for wf in workflows:
                print(f"  - {wf}")
            print("\nUse 'python run_ada.py <workflow> --help' for details\n")
            return
        elif arg in ("--status", "-s"):
            print_status()
            return
        elif arg in ("--quiet", "-q"):
            verbose = False
        elif arg in ("--trace", "-t"):
            trace = True
        # Workflow parameters (--param-name value)
        elif arg.startswith("--") and is_workflow:
            param_name = arg[2:].replace("-", "_")
            # Check if next arg is a value
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                workflow_params[param_name] = args[i + 1]
                i += 1  # Skip the value
            else:
                workflow_params[param_name] = True
        # Natural language task parts
        elif not is_workflow:
            task_parts.append(arg)

        i += 1

    # Build task string
    if is_workflow:
        # Named workflow
        try:
            task = build_task_from_workflow(workflow_name, **workflow_params)
            if verbose:
                print(f"\n[WORKFLOW] {workflow_name}")
                print(f"[TASK] {task}\n")
        except WorkflowError as e:
            print(f"\nError: {e}")
            print(f"\nUse 'python run_ada.py {workflow_name} --help' for usage\n")
            return
    else:
        # Natural language (backward compatible)
        if not task_parts:
            print("Error: No task specified")
            print("Usage: python run_ada.py <task>")
            print("       python run_ada.py <workflow> [options]")
            return
        task = " ".join(task_parts)

    # Execute the task
    try:
        asyncio.run(execute_task(task, verbose=verbose, trace=trace))
    except KeyboardInterrupt:
        print("\n\nTask cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
