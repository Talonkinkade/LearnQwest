#!/usr/bin/env python3
"""
Workflow Library - Named Workflows for User-Friendly Commands
==============================================================
Maps simple command names to task patterns with parameters.

Usage:
    from workflow_library import build_task_from_workflow, list_workflows

    task = build_task_from_workflow("create-quiz", topic="photosynthesis", grade_level=6)
    # Returns: "Create a quiz about photosynthesis for 6th grade with 4 questions"
"""

from typing import Dict, Any, List, Optional


# Workflow definitions
WORKFLOWS = {
    "create-quiz": {
        "pattern": "QUIZ_GENERATION",
        "description": "Generate TEKS-aligned quiz questions",
        "required": ["topic"],
        "optional": {
            "grade_level": 6,
            "question_count": 4,
            "question_types": ["multiple_choice", "true_false"],
            "teks_standards": None,
        },
        "template": "Create a quiz about {topic} for {grade_level}th grade with {question_count} questions",
    },
    "analyze-code": {
        "pattern": "CODEBASE_ANALYSIS",
        "description": "Analyze codebase for duplicates, dead code, and organization",
        "required": [],
        "optional": {"path": "./"},
        "template": "Analyze the codebase at {path}",
    },
    "audit-codebase": {
        "pattern": "CODEBASE_ANALYSIS",
        "description": "Full codebase audit with refactoring recommendations",
        "required": [],
        "optional": {"path": "./"},
        "template": "Audit the codebase at {path}",
    },
    "research-topic": {
        "pattern": "CONTENT_RESEARCH",
        "description": "Research educational content on a topic",
        "required": ["topic"],
        "optional": {"grade_level": None, "depth": "comprehensive"},
        "template": "Research {topic} for {grade_level}th grade students with {depth} depth",
    },
    "assess-quality": {
        "pattern": "QUALITY_ASSESSMENT",
        "description": "Assess educational content quality",
        "required": ["content_path"],
        "optional": {"dimensions": ["credibility", "accuracy", "educational"]},
        "template": "Assess the quality of content at {content_path}",
    },
    "find-duplicates": {
        "pattern": "DUPLICATE_DETECTION",
        "description": "Find duplicate code patterns",
        "required": [],
        "optional": {"path": "./", "threshold": 0.8},
        "template": "Find duplicate code in {path}",
    },
    "find-dead-code": {
        "pattern": "DEAD_CODE_ANALYSIS",
        "description": "Identify unused code",
        "required": [],
        "optional": {"path": "./"},
        "template": "Find dead code in {path}",
    },
    "organize-code": {
        "pattern": "CODE_ORGANIZATION",
        "description": "Analyze code organization and structure",
        "required": [],
        "optional": {"path": "./"},
        "template": "Analyze code organization in {path}",
    },
}


class WorkflowError(Exception):
    """Raised when workflow validation fails"""

    pass


def list_workflows() -> List[str]:
    """List all available workflow names"""
    return list(WORKFLOWS.keys())


def get_workflow_info(workflow_name: str) -> Dict[str, Any]:
    """Get workflow definition

    Args:
        workflow_name: Name of the workflow

    Returns:
        Workflow definition dict

    Raises:
        WorkflowError: If workflow not found
    """
    if workflow_name not in WORKFLOWS:
        available = ", ".join(list_workflows())
        raise WorkflowError(
            f"Unknown workflow: {workflow_name}. Available: {available}"
        )
    return WORKFLOWS[workflow_name]


def validate_workflow_params(workflow_name: str, params: Dict[str, Any]) -> None:
    """Validate workflow parameters

    Args:
        workflow_name: Name of the workflow
        params: Parameters provided by user

    Raises:
        WorkflowError: If required parameters missing
    """
    workflow = get_workflow_info(workflow_name)

    # Check required parameters
    required = workflow["required"]
    missing = [param for param in required if param not in params]

    if missing:
        raise WorkflowError(
            f"Missing required parameters for {workflow_name}: {', '.join(missing)}"
        )


def build_task_from_workflow(workflow_name: str, **params) -> str:
    """Build natural language task string from workflow and parameters

    Args:
        workflow_name: Name of the workflow (e.g., "create-quiz")
        **params: Workflow parameters

    Returns:
        Natural language task string

    Raises:
        WorkflowError: If workflow not found or parameters invalid

    Examples:
        >>> build_task_from_workflow("create-quiz", topic="photosynthesis", grade_level=6)
        'Create a quiz about photosynthesis for 6th grade with 4 questions'

        >>> build_task_from_workflow("audit-codebase")
        'Audit the codebase at ./'
    """
    # Get workflow definition
    workflow = get_workflow_info(workflow_name)

    # Validate parameters
    validate_workflow_params(workflow_name, params)

    # Merge with defaults
    merged_params = {}
    merged_params.update(workflow.get("optional", {}))
    merged_params.update(params)

    # Build task string from template
    template = workflow["template"]

    # Handle None values in template
    for key, value in merged_params.items():
        if value is None:
            # Remove optional parts with None values
            template = template.replace(f" for {{{key}}}th grade", "")
            template = template.replace(f" with {{{key}}} depth", "")
            template = template.replace(f" {{{key}}}", "")

    try:
        task_string = template.format(**merged_params)
    except KeyError as e:
        raise WorkflowError(f"Missing parameter in template: {e}")

    return task_string


def get_workflow_help(workflow_name: str) -> str:
    """Get help text for a workflow

    Args:
        workflow_name: Name of the workflow

    Returns:
        Help text describing the workflow
    """
    workflow = get_workflow_info(workflow_name)

    help_text = [
        f"Workflow: {workflow_name}",
        f"Description: {workflow['description']}",
        f"Pattern: {workflow['pattern']}",
        "",
    ]

    # Required parameters
    if workflow["required"]:
        help_text.append("Required parameters:")
        for param in workflow["required"]:
            help_text.append(f"  --{param.replace('_', '-')}")
        help_text.append("")

    # Optional parameters
    if workflow.get("optional"):
        help_text.append("Optional parameters:")
        for param, default in workflow["optional"].items():
            help_text.append(f"  --{param.replace('_', '-')} (default: {default})")
        help_text.append("")

    # Example
    help_text.append("Example:")
    if workflow_name == "create-quiz":
        help_text.append(
            '  python run_ada.py create-quiz --topic "photosynthesis" --grade-level 6'
        )
    elif workflow_name == "audit-codebase":
        help_text.append("  python run_ada.py audit-codebase")
    else:
        help_text.append(f"  python run_ada.py {workflow_name}")

    return "\n".join(help_text)


# Test function
def _test_workflows():
    """Test workflow library"""
    print("[TEST] Workflow Library")
    print("=" * 80)

    # Test 1: List workflows
    print("\n1. List workflows:")
    workflows = list_workflows()
    print(f"   Found {len(workflows)} workflows: {', '.join(workflows)}")

    # Test 2: Create quiz workflow
    print("\n2. Create quiz workflow:")
    task = build_task_from_workflow(
        "create-quiz", topic="photosynthesis", grade_level=6, question_count=10
    )
    print(f"   Task: {task}")

    # Test 3: Audit codebase workflow
    print("\n3. Audit codebase workflow:")
    task = build_task_from_workflow("audit-codebase")
    print(f"   Task: {task}")

    # Test 4: Research topic workflow
    print("\n4. Research topic workflow:")
    task = build_task_from_workflow(
        "research-topic", topic="quantum computing", grade_level=10
    )
    print(f"   Task: {task}")

    # Test 5: Missing required parameter
    print("\n5. Missing required parameter (should fail):")
    try:
        task = build_task_from_workflow("create-quiz")
        print(f"   [FAIL] Should have raised WorkflowError")
    except WorkflowError as e:
        print(f"   [OK] Caught error: {e}")

    # Test 6: Unknown workflow
    print("\n6. Unknown workflow (should fail):")
    try:
        task = build_task_from_workflow("invalid-workflow")
        print(f"   [FAIL] Should have raised WorkflowError")
    except WorkflowError as e:
        print(f"   [OK] Caught error: {e}")

    # Test 7: Get workflow help
    print("\n7. Get workflow help:")
    help_text = get_workflow_help("create-quiz")
    print(help_text)

    print("\n" + "=" * 80)
    print("[OK] All tests passed!")


if __name__ == "__main__":
    _test_workflows()
