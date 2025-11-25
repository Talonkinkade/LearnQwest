"""
Task Decomposition Engine - ADA Core Intelligence
Converts high-level requests into Ion-executable subtasks

This is the intelligence that replaces Link's manual coordination.
Instead of Link orchestrating 4 Claude instances, ADA orchestrates 60 Ions.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import re


class TaskPattern(Enum):
    """Recognized task patterns"""

    CODEBASE_ANALYSIS = "analyze_codebase"
    CONTENT_RESEARCH = "research_topic"
    PROJECT_STATUS = "project_status"
    CODE_CLEANUP = "code_cleanup"
    LEARNING_MATERIALS = "create_learning"
    QUALITY_ASSESSMENT = "assess_quality"
    REFACTORING = "refactor_code"
    DOCUMENTATION = "generate_docs"
    DUPLICATE_DETECTION = "find_duplicates"
    DEAD_CODE_ANALYSIS = "find_dead_code"
    CODE_ORGANIZATION = "organize_code"
    CONTENT_EXTRACTION = "extract_content"
    QUIZ_GENERATION = "generate_quiz"
    CUSTOM = "custom"


@dataclass
class SubTask:
    """A single executable subtask for an Ion"""

    task_id: str
    ion_name: str
    description: str
    input_data: Dict[str, Any]
    priority: int = 3  # 1=highest, 5=lowest
    depends_on: List[str] = field(default_factory=list)  # Task IDs this depends on
    can_parallelize: bool = True
    estimated_time_seconds: int = 5


@dataclass
class TaskPlan:
    """Complete execution plan for a complex task"""

    original_request: str
    pattern: TaskPattern
    subtasks: List[SubTask]
    estimated_time_seconds: int
    requires_synthesis: bool = True
    parallel_groups: List[List[str]] = field(
        default_factory=list
    )  # Groups that can run in parallel


class TaskDecomposer:
    """
    Decomposes complex tasks into Ion-executable subtasks

    This is the intelligence that replaces Link's manual coordination.

    Example:
        Link says: "Analyze the codebase"
        Decomposer creates:
            - duplicate-detector subtask
            - dead-code-eliminator subtask
            - code-grouper subtask
            - refactor-planner subtask (depends on above 3)

        ADA executes all 4, synthesizes results, returns one answer.
    """

    def __init__(self):
        self.patterns = {
            TaskPattern.CODEBASE_ANALYSIS: self._decompose_codebase_analysis,
            TaskPattern.CONTENT_RESEARCH: self._decompose_content_research,
            TaskPattern.PROJECT_STATUS: self._decompose_project_status,
            TaskPattern.CODE_CLEANUP: self._decompose_code_cleanup,
            TaskPattern.LEARNING_MATERIALS: self._decompose_learning_materials,
            TaskPattern.QUALITY_ASSESSMENT: self._decompose_quality_assessment,
            TaskPattern.REFACTORING: self._decompose_refactoring,
            TaskPattern.DOCUMENTATION: self._decompose_documentation,
            TaskPattern.DUPLICATE_DETECTION: self._decompose_duplicate_detection,
            TaskPattern.DEAD_CODE_ANALYSIS: self._decompose_dead_code_analysis,
            TaskPattern.CODE_ORGANIZATION: self._decompose_code_organization,
            TaskPattern.CONTENT_EXTRACTION: self._decompose_content_extraction,
            TaskPattern.QUIZ_GENERATION: self._decompose_quiz_generation,
        }

        self.task_counter = 0

    def decompose(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> TaskPlan:
        """
        Main entry point: Convert task string to execution plan

        Args:
            task: High-level task description from Link
            context: Optional context (file paths, parameters, etc.)

        Returns:
            TaskPlan with all subtasks and execution strategy
        """
        # Step 1: Identify pattern
        pattern = self._identify_pattern(task)

        # Step 2: Get decomposition function
        decompose_fn = self.patterns.get(pattern, self._decompose_custom)

        # Step 3: Generate subtasks
        subtasks = decompose_fn(task, context or {})

        # Step 4: Calculate parallel groups
        parallel_groups = self._calculate_parallel_groups(subtasks)

        # Step 5: Estimate total time
        estimated_time = self._estimate_total_time(subtasks, parallel_groups)

        return TaskPlan(
            original_request=task,
            pattern=pattern,
            subtasks=subtasks,
            estimated_time_seconds=estimated_time,
            requires_synthesis=len(subtasks) > 1,
            parallel_groups=parallel_groups,
        )

    def _identify_pattern(self, task: str) -> TaskPattern:
        """Identify which pattern this task matches

        IMPORTANT: More specific patterns must be checked BEFORE general ones!
        e.g., "find duplicate" should match DUPLICATE_DETECTION, not CONTENT_RESEARCH
        """
        task_lower = task.lower()

        # ============================================================
        # SPECIFIC CODE ANALYSIS PATTERNS (check first!)
        # These contain words like "find", "code" that overlap with general patterns
        # ============================================================

        # Duplicate detection - check before "find" triggers research
        # Enhanced with "find duplicate code" patterns
        if any(
            word in task_lower
            for word in [
                "duplicate",
                "duplicates",
                "repeated",
                "redundant",
                "copy",
                "copies",
            ]
        ) or any(
            phrase in task_lower
            for phrase in [
                "find duplicate",
                "duplicate code",
                "duplicate patterns",
                "similar code",
            ]
        ):
            return TaskPattern.DUPLICATE_DETECTION

        # Dead code analysis - check before general code analysis
        # Enhanced with "identify/find unused code" patterns
        if any(
            phrase in task_lower
            for phrase in [
                "dead code",
                "unused code",
                "unreachable",
                "identify unused",
                "find unused",
            ]
        ) or (
            ("unused" in task_lower or "dead" in task_lower) and "code" in task_lower
        ):
            return TaskPattern.DEAD_CODE_ANALYSIS

        # Code organization - check before general "organize" triggers cleanup
        # Enhanced with "analyze code organization" patterns
        if any(
            phrase in task_lower
            for phrase in [
                "code organization",
                "organize code",
                "group code",
                "structure code",
                "analyze organization",
                "analyze code organization",
            ]
        ) or (
            "code" in task_lower
            and any(word in task_lower for word in ["group", "structure", "arrange"])
        ):
            return TaskPattern.CODE_ORGANIZATION

        # ============================================================
        # LEARNING PATTERNS (check before general research)
        # ============================================================

        # Quiz generation - specific learning pattern
        if "quiz" in task_lower or "test questions" in task_lower:
            return TaskPattern.QUIZ_GENERATION

        # Learning materials - broader learning pattern
        if any(
            word in task_lower
            for word in ["questions", "teach", "explain", "lesson", "study", "learn"]
        ) and not any(word in task_lower for word in ["research", "search"]):
            return TaskPattern.LEARNING_MATERIALS

        # ============================================================
        # PROJECT/CODEBASE ANALYSIS PATTERNS
        # ============================================================

        # Codebase analysis patterns
        if any(
            word in task_lower for word in ["analyze", "audit", "assess", "review"]
        ) and any(
            word in task_lower
            for word in ["codebase", "code", "repository", "project", "files"]
        ):
            return TaskPattern.CODEBASE_ANALYSIS

        # Status patterns
        if any(
            word in task_lower
            for word in [
                "status",
                "where am i",
                "what was i",
                "context",
                "working on",
                "yesterday",
            ]
        ):
            return TaskPattern.PROJECT_STATUS

        # Cleanup patterns (check after specific code patterns)
        if any(word in task_lower for word in ["clean", "cleanup", "tidy"]):
            return TaskPattern.CODE_CLEANUP

        # Refactoring patterns
        # Enhanced with "generate refactoring plan" patterns
        if any(
            phrase in task_lower
            for phrase in [
                "refactor",
                "restructure",
                "improve code",
                "optimize code",
                "refactoring plan",
                "generate refactoring",
            ]
        ):
            return TaskPattern.REFACTORING

        # ============================================================
        # CONTENT PATTERNS
        # ============================================================

        # Quality assessment
        if any(
            word in task_lower for word in ["quality", "score", "rate", "evaluate"]
        ) and any(
            word in task_lower for word in ["content", "video", "article", "resource"]
        ):
            return TaskPattern.QUALITY_ASSESSMENT

        # Content extraction
        if any(
            word in task_lower
            for word in ["extract", "pull content", "get content", "transcript"]
        ):
            return TaskPattern.CONTENT_EXTRACTION

        # Documentation
        if any(word in task_lower for word in ["document", "docs", "readme", "guide"]):
            return TaskPattern.DOCUMENTATION

        # ============================================================
        # GENERAL RESEARCH (check last - most general pattern)
        # ============================================================

        # Research patterns - now check LAST since "find" is very general
        if any(
            word in task_lower
            for word in ["research", "search", "learn about", "discover", "look up"]
        ):
            return TaskPattern.CONTENT_RESEARCH

        # General "find" only if nothing more specific matched
        if "find" in task_lower:
            return TaskPattern.CONTENT_RESEARCH

        return TaskPattern.CUSTOM

    def _generate_task_id(self, ion_name: str) -> str:
        """Generate unique task ID"""
        self.task_counter += 1
        return f"{ion_name}_{self.task_counter:03d}"

    def _decompose_codebase_analysis(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose codebase analysis request

        Example: "Analyze the LearnQwest codebase"
        Subtasks: duplicate-detector, dead-code-eliminator, code-grouper, refactor-planner
        """
        path = context.get("path") or self._extract_path(task) or "./"

        # Phase 1: Parallel analysis (all can run simultaneously)
        dup_task = SubTask(
            task_id=self._generate_task_id("duplicate-detector"),
            ion_name="duplicate-detector",
            description="Find duplicate code patterns",
            input_data={"path": path, "min_lines": 6, "output": "duplicates.json"},
            priority=2,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        dead_task = SubTask(
            task_id=self._generate_task_id("dead-code-eliminator"),
            ion_name="dead-code-eliminator",
            description="Identify unused code",
            input_data={"path": path, "output": "dead_code.json"},
            priority=2,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        group_task = SubTask(
            task_id=self._generate_task_id("code-grouper"),
            ion_name="code-grouper",
            description="Analyze code organization",
            input_data={"path": path, "output": "groups.json"},
            priority=3,
            can_parallelize=True,
            estimated_time_seconds=8,
        )

        # Phase 2: Synthesis (depends on all above)
        refactor_task = SubTask(
            task_id=self._generate_task_id("refactor-planner"),
            ion_name="refactor-planner",
            description="Generate refactoring recommendations",
            input_data={
                "path": path,
                "duplicates": "duplicates.json",
                "dead_code": "dead_code.json",
                "groups": "groups.json",
                "output": "refactor_plan.json",
            },
            priority=1,
            depends_on=[dup_task.task_id, dead_task.task_id, group_task.task_id],
            can_parallelize=False,
            estimated_time_seconds=10,
        )

        return [dup_task, dead_task, group_task, refactor_task]

    def _decompose_content_research(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose research request

        Example: "Research quantum computing and create study materials"
        """
        topic = context.get("topic") or self._extract_topic(task)
        max_results = context.get("max_results", 10)

        # Phase 1: Search
        search_task = SubTask(
            task_id=self._generate_task_id("omnisearch"),
            ion_name="omnisearch",
            description=f"Search for content about {topic}",
            input_data={
                "query": topic,
                "sources": ["youtube", "web"],
                "max_results": max_results,
                "output": "search_results.json",
            },
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=15,
        )

        # Phase 2: Assess quality
        quality_task = SubTask(
            task_id=self._generate_task_id("quality-assessor"),
            ion_name="quality-assessor",
            description="Assess content quality",
            input_data={
                "input": "search_results.json",
                "mode": "testing",
                "output": "quality_scores.json",
            },
            priority=2,
            depends_on=[search_task.task_id],
            can_parallelize=False,
            estimated_time_seconds=2,
        )

        return [search_task, quality_task]

    def _decompose_project_status(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose status/context request

        Example: "What was I working on?"
        """
        lookback_hours = context.get("lookback_hours", 24)

        # For now, return a placeholder
        # Future: context-builder Ion that reads logs + git
        status_task = SubTask(
            task_id=self._generate_task_id("context-builder"),
            ion_name="context-builder",
            description="Build project context from logs and git",
            input_data={
                "lookback_hours": lookback_hours,
                "sources": ["ada_logs", "git", "files"],
                "output": "context.json",
            },
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=2,
        )

        return [status_task]

    def _decompose_code_cleanup(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose cleanup request

        Example: "Clean up the codebase"
        """
        path = context.get("path") or self._extract_path(task) or "./"

        # Phase 1: Find issues (parallel)
        dup_task = SubTask(
            task_id=self._generate_task_id("duplicate-detector"),
            ion_name="duplicate-detector",
            description="Find duplicates to consolidate",
            input_data={"path": path, "output": "duplicates.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        dead_task = SubTask(
            task_id=self._generate_task_id("dead-code-eliminator"),
            ion_name="dead-code-eliminator",
            description="Find code to remove",
            input_data={"path": path, "output": "dead_code.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        # Phase 2: Plan cleanup (depends on both)
        plan_task = SubTask(
            task_id=self._generate_task_id("refactor-planner"),
            ion_name="refactor-planner",
            description="Plan cleanup actions",
            input_data={
                "path": path,
                "duplicates": "duplicates.json",
                "dead_code": "dead_code.json",
                "output": "cleanup_plan.json",
            },
            priority=2,
            depends_on=[dup_task.task_id, dead_task.task_id],
            can_parallelize=False,
            estimated_time_seconds=10,
        )

        return [dup_task, dead_task, plan_task]

    def _decompose_learning_materials(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose learning material creation

        Example: "Create a quiz about photosynthesis"
        """
        topic = context.get("topic") or self._extract_topic(task)
        num_questions = context.get("num_questions", 5)
        grade_level = context.get("grade_level", "6-8")

        quiz_task = SubTask(
            task_id=self._generate_task_id("quiz-generator"),
            ion_name="quiz-generator",
            description=f"Generate quiz about {topic}",
            input_data={
                "content": context.get("content", f"Educational content about {topic}"),
                "topic": topic,
                "num_questions": num_questions,
                "grade_level": grade_level,
                "output": "quiz.json",
            },
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=3,
        )

        return [quiz_task]

    def _decompose_quality_assessment(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose quality assessment request

        Example: "Assess the quality of these videos"
        """
        input_file = context.get("input_file", "content.json")

        quality_task = SubTask(
            task_id=self._generate_task_id("quality-assessor"),
            ion_name="quality-assessor",
            description="Assess content quality",
            input_data={
                "input": input_file,
                "mode": "testing",
                "output": "quality_assessment.json",
            },
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=2,
        )

        return [quality_task]

    def _decompose_refactoring(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose refactoring request into 2-wave execution

        Wave 1: Gather intelligence (3 analysis Ions in parallel)
        Wave 2: Create refactoring plan (1 orchestrator Ion)

        Example: "Refactor the Ion system"
        """
        path = context.get("path") or self._extract_path(task) or "./"

        # Wave 1: Analysis Ions (run in parallel)

        # 1. Duplicate detection
        dup_task = SubTask(
            task_id=self._generate_task_id("duplicate-detector"),
            ion_name="duplicate-detector",
            description="Find duplicate code patterns for refactoring consideration",
            input_data={"path": path, "output": "duplicates.json"},
            priority=2,  # Higher priority = Wave 1
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        # 2. Dead code analysis
        dead_task = SubTask(
            task_id=self._generate_task_id("dead-code-eliminator"),
            ion_name="dead-code-eliminator",
            description="Identify unused code for removal recommendations",
            input_data={"path": path, "output": "dead_code.json"},
            priority=2,  # Higher priority = Wave 1
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        # 3. Organization analysis
        grouper_task = SubTask(
            task_id=self._generate_task_id("code-grouper"),
            ion_name="code-grouper",
            description="Analyze code organization for restructuring opportunities",
            input_data={"path": path, "output": "grouping.json"},
            priority=2,  # Higher priority = Wave 1
            can_parallelize=True,
            estimated_time_seconds=8,
        )

        # Wave 2: Refactoring plan (runs after Wave 1 complete)
        refactor_task = SubTask(
            task_id=self._generate_task_id("refactor-planner"),
            ion_name="refactor-planner",
            description="Generate comprehensive refactoring plan using analysis results",
            input_data={
                "path": path,
                "duplicates": "duplicates.json",
                "dead_code": "dead_code.json",
                "grouping": "grouping.json",
                "output": "refactor_plan.json",
            },
            priority=1,  # Lower priority = Wave 2
            depends_on=[dup_task.task_id, dead_task.task_id, grouper_task.task_id],
            can_parallelize=False,
            estimated_time_seconds=10,
        )

        return [dup_task, dead_task, grouper_task, refactor_task]

    def _decompose_documentation(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """
        Decompose documentation request

        Example: "Generate documentation for the Ions"
        """
        path = context.get("path") or self._extract_path(task) or "./"

        # Future: doc-generator Ion
        doc_task = SubTask(
            task_id=self._generate_task_id("doc-generator"),
            ion_name="doc-generator",
            description="Generate documentation",
            input_data={"path": path, "format": "markdown", "output": "docs/"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=15,
        )

        return [doc_task]

    def _decompose_duplicate_detection(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """Decompose duplicate detection request"""
        path = context.get("path") or self._extract_path(task) or "./"

        dup_task = SubTask(
            task_id=self._generate_task_id("duplicate-detector"),
            ion_name="duplicate-detector",
            description="Find duplicate code patterns",
            input_data={"path": path, "min_lines": 6, "output": "duplicates.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        return [dup_task]

    def _decompose_dead_code_analysis(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """Decompose dead code analysis request"""
        path = context.get("path") or self._extract_path(task) or "./"

        dead_task = SubTask(
            task_id=self._generate_task_id("dead-code-eliminator"),
            ion_name="dead-code-eliminator",
            description="Find unused code",
            input_data={"path": path, "output": "dead_code.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        return [dead_task]

    def _decompose_code_organization(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """Decompose code organization request"""
        path = context.get("path") or self._extract_path(task) or "./"

        org_task = SubTask(
            task_id=self._generate_task_id("code-grouper"),
            ion_name="code-grouper",
            description="Analyze code organization",
            input_data={"path": path, "output": "groups.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=8,
        )

        return [org_task]

    def _decompose_content_extraction(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """Decompose content extraction request"""
        url = context.get("url", "")

        extract_task = SubTask(
            task_id=self._generate_task_id("content-extractor"),
            ion_name="content-extractor",
            description="Extract content from source",
            input_data={"url": url, "output": "extracted_content.json"},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=10,
        )

        return [extract_task]

    def _decompose_quiz_generation(
        self, task: str, context: Dict[str, Any]
    ) -> List[SubTask]:
        """Decompose quiz generation request"""
        topic = context.get("topic") or self._extract_topic(task)
        num_questions = context.get("num_questions", 5)
        grade_level = context.get("grade_level", "6-8")

        quiz_task = SubTask(
            task_id=self._generate_task_id("quiz-generator"),
            ion_name="quiz-generator",
            description=f"Generate quiz about {topic}",
            input_data={
                "content": context.get("content", f"Educational content about {topic}"),
                "topic": topic,
                "num_questions": num_questions,
                "grade_level": grade_level,
                "output": "quiz.json",
            },
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=3,
        )

        return [quiz_task]

    def _decompose_custom(self, task: str, context: Dict[str, Any]) -> List[SubTask]:
        """Fallback for unrecognized patterns"""
        custom_task = SubTask(
            task_id=self._generate_task_id("general"),
            ion_name="general",
            description=task,
            input_data={"task": task, **context},
            priority=1,
            can_parallelize=True,
            estimated_time_seconds=5,
        )

        return [custom_task]

    def _extract_path(self, task: str) -> Optional[str]:
        """Extract file path from task description"""
        # Look for common path indicators
        if "learnqwest" in task.lower():
            return "./"

        # Look for explicit paths
        path_match = re.search(r'["\']([^"\']+)["\']', task)
        if path_match:
            return path_match.group(1)

        return None

    def _extract_topic(self, task: str) -> str:
        """Extract topic from task description"""
        # Remove common words
        stop_words = {
            "about",
            "on",
            "for",
            "the",
            "a",
            "an",
            "create",
            "generate",
            "make",
            "quiz",
            "questions",
        }

        words = task.lower().split()
        topic_words = [w for w in words if w not in stop_words and len(w) > 2]

        # Take last 3 meaningful words as topic
        return " ".join(topic_words[-3:]) if topic_words else "general topic"

    def _calculate_parallel_groups(self, subtasks: List[SubTask]) -> List[List[str]]:
        """
        Calculate which tasks can run in parallel

        Returns groups of task IDs that can execute simultaneously
        """
        groups = []
        remaining = set(st.task_id for st in subtasks)
        completed = set()

        while remaining:
            # Find tasks with no unmet dependencies
            current_group = []
            for task_id in list(remaining):
                task = next(st for st in subtasks if st.task_id == task_id)

                # Check if all dependencies are met
                if all(dep in completed for dep in task.depends_on):
                    current_group.append(task_id)

            if not current_group:
                # Circular dependency or error
                break

            groups.append(current_group)
            completed.update(current_group)
            remaining -= set(current_group)

        return groups

    def _estimate_total_time(
        self, subtasks: List[SubTask], parallel_groups: List[List[str]]
    ) -> int:
        """
        Estimate total execution time considering parallelization

        Sequential: sum of all times
        Parallel: sum of max time per group
        """
        total = 0

        for group in parallel_groups:
            # Max time in this parallel group
            group_tasks = [st for st in subtasks if st.task_id in group]
            max_time = max((st.estimated_time_seconds for st in group_tasks), default=0)
            total += max_time

        return total


def test_decomposer():
    """Test the decomposer with various tasks"""
    decomposer = TaskDecomposer()

    test_cases = [
        ("Analyze the LearnQwest codebase", {}),
        ("Research quantum computing for beginners", {"max_results": 5}),
        ("What was I working on yesterday?", {"lookback_hours": 24}),
        ("Clean up duplicate code in the project", {"path": "./qwest-ions"}),
        (
            "Create a quiz about photosynthesis",
            {"num_questions": 10, "grade_level": "6-8"},
        ),
        ("Assess the quality of educational videos", {"input_file": "videos.json"}),
    ]

    for task, context in test_cases:
        print(f"\n{'='*80}")
        print(f"Task: {task}")
        if context:
            print(f"Context: {context}")
        print("=" * 80)

        plan = decomposer.decompose(task, context)

        print(f"\nPattern: {plan.pattern.value}")
        print(f"Subtasks: {len(plan.subtasks)}")
        print(f"Estimated time: {plan.estimated_time_seconds}s")
        print(f"Requires synthesis: {plan.requires_synthesis}")
        print(f"\nParallel execution groups: {len(plan.parallel_groups)}")

        for i, group in enumerate(plan.parallel_groups, 1):
            print(f"  Group {i}: {len(group)} tasks (can run simultaneously)")

        print(f"\nSubtask Details:")
        for i, subtask in enumerate(plan.subtasks, 1):
            print(f"\n{i}. [{subtask.task_id}] {subtask.ion_name}")
            print(f"   Description: {subtask.description}")
            print(f"   Priority: {subtask.priority}")
            print(f"   Estimated time: {subtask.estimated_time_seconds}s")
            print(f"   Can parallelize: {subtask.can_parallelize}")
            if subtask.depends_on:
                print(f"   Depends on: {', '.join(subtask.depends_on)}")
            print(f"   Input: {subtask.input_data}")


if __name__ == "__main__":
    print("=" * 80)
    print("  TASK DECOMPOSITION ENGINE - TEST SUITE")
    print("  Replacing Link's manual coordination with automated intelligence")
    print("=" * 80)
    test_decomposer()
