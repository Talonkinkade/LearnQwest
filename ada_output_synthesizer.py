#!/usr/bin/env python3
"""
Output Synthesis Engine
=======================
Combines multiple Ion outputs into coherent reports.

This replaces Link's mental synthesis of 4 Claude outputs into
ONE coherent, actionable report.

Usage:
    from ada_output_synthesizer import OutputSynthesizer, IonOutput

    synthesizer = OutputSynthesizer()
    report = synthesizer.synthesize("codebase_analysis", ion_outputs)
    print(synthesizer.format_as_text(report))
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class IonOutput:
    """Single Ion execution result"""

    ion_name: str
    description: str
    success: bool
    result: Dict[str, Any]
    execution_time_ms: int
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class SynthesizedReport:
    """Final combined report"""

    title: str
    summary: str
    sections: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    raw_outputs: List[IonOutput]
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class OutputSynthesizer:
    """
    Combines multiple Ion outputs into readable reports

    This replaces Link's mental synthesis of 4 Claude outputs.
    Instead of manually reading ALPHA, BRAVO, CHARLIE, CLOUD outputs
    and combining them in your head, this does it automatically.

    Patterns supported:
    - codebase_analysis: duplicate-detector + dead-code + code-grouper + refactor-planner
    - content_research: omnisearch + quality-assessor results
    - project_status: git state + activity logs + health checks
    - code_cleanup: all cleanup Ions combined
    - learning_materials: content extraction + module generation
    """

    def __init__(self):
        self.synthesizers: Dict[str, Callable] = {
            # Core patterns
            "codebase_analysis": self._synthesize_codebase_analysis,
            "analyze_codebase": self._synthesize_codebase_analysis,  # Alias
            "content_research": self._synthesize_content_research,
            "research_topic": self._synthesize_content_research,  # Alias
            "project_status": self._synthesize_project_status,
            "code_cleanup": self._synthesize_code_cleanup,
            "learning_materials": self._synthesize_learning_materials,
            "create_learning": self._synthesize_learning_materials,  # Alias
            # Additional patterns
            "assess_quality": self._synthesize_quality_assessment,
            "quality_assessment": self._synthesize_quality_assessment,  # Alias
            "refactor_code": self._synthesize_refactoring,
            "refactoring": self._synthesize_refactoring,  # Alias
            "generate_docs": self._synthesize_documentation,
            "documentation": self._synthesize_documentation,  # Alias
            "extract_content": self._synthesize_content_extraction,
            "content_extraction": self._synthesize_content_extraction,  # Alias
            "generate_quiz": self._synthesize_quiz_generation,
            "quiz_generation": self._synthesize_quiz_generation,  # Alias
            # Sub-patterns (map to their parent)
            "find_duplicates": self._synthesize_codebase_analysis,
            "find_dead_code": self._synthesize_codebase_analysis,
            "organize_code": self._synthesize_codebase_analysis,
        }

    def synthesize(
        self, task_pattern: str, ion_outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Main entry point: Combine Ion outputs into one report

        Args:
            task_pattern: The pattern used for decomposition
            ion_outputs: Results from all Ions

        Returns:
            One coherent report
        """
        synthesize_fn = self.synthesizers.get(task_pattern, self._synthesize_generic)

        return synthesize_fn(ion_outputs)

    # =========================================================================
    # CODEBASE ANALYSIS SYNTHESIS
    # =========================================================================

    def _synthesize_codebase_analysis(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize codebase analysis from multiple Ions

        Inputs: duplicate-detector, dead-code-eliminator, code-grouper, refactor-planner
        Output: One executive summary with prioritized actions
        """
        sections = []
        recommendations = []

        # Find each Ion's output
        dup_out = self._find_output(outputs, "duplicate-detector")
        dead_out = self._find_output(outputs, "dead-code-eliminator")
        group_out = self._find_output(outputs, "code-grouper")
        refactor_out = self._find_output(outputs, "refactor-planner")

        # Build executive summary
        summary_parts = []
        total_issues = 0

        if dup_out and dup_out.success:
            dup_count = dup_out.result.get("duplicates_found", 0)
            total_issues += dup_count
            summary_parts.append(f"{dup_count} duplicate code blocks")
            if dup_count > 5:
                recommendations.append(
                    "HIGH: Refactor duplicate code to shared utilities"
                )

        if dead_out and dead_out.success:
            dead_funcs = dead_out.result.get("unused_functions", 0)
            dead_imports = dead_out.result.get("unused_imports", 0)
            total_issues += dead_funcs + dead_imports
            summary_parts.append(
                f"{dead_funcs} unused functions, {dead_imports} unused imports"
            )
            if dead_funcs > 0:
                recommendations.append(
                    "MEDIUM: Remove dead code to reduce maintenance burden"
                )

        if group_out and group_out.success:
            misplaced = group_out.result.get("misplaced_files", 0)
            if misplaced > 0:
                summary_parts.append(f"{misplaced} files could be better organized")
                recommendations.append("LOW: Consider reorganizing file structure")

        if refactor_out and refactor_out.success:
            priority_count = len(refactor_out.result.get("priority_actions", []))
            if priority_count > 0:
                summary_parts.append(
                    f"{priority_count} refactoring actions recommended"
                )

        summary = (
            f"Codebase analysis complete. Found {total_issues} issues: "
            + ", ".join(summary_parts)
            + "."
        )

        # Build sections
        if dup_out and dup_out.success:
            sections.append(
                {
                    "title": "Duplicate Code",
                    "icon": "[DUP]",
                    "content": self._format_duplicate_section(dup_out.result),
                    "priority": (
                        "high"
                        if dup_out.result.get("duplicates_found", 0) > 5
                        else "medium"
                    ),
                    "ion": "duplicate-detector",
                }
            )

        if dead_out and dead_out.success:
            sections.append(
                {
                    "title": "Dead Code",
                    "icon": "[DEL]",
                    "content": self._format_dead_code_section(dead_out.result),
                    "priority": "medium",
                    "ion": "dead-code-eliminator",
                }
            )

        if group_out and group_out.success:
            sections.append(
                {
                    "title": "Code Organization",
                    "icon": "[ORG]",
                    "content": self._format_organization_section(group_out.result),
                    "priority": "low",
                    "ion": "code-grouper",
                }
            )

        if refactor_out and refactor_out.success:
            sections.append(
                {
                    "title": "Refactoring Plan",
                    "icon": "[REF]",
                    "content": self._format_refactoring_section(refactor_out.result),
                    "priority": "high",
                    "ion": "refactor-planner",
                }
            )

        # Sort sections by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sections.sort(key=lambda s: priority_order.get(s.get("priority", "low"), 3))

        metadata = self._build_metadata(outputs)

        return SynthesizedReport(
            title="LearnQwest Codebase Analysis",
            summary=summary,
            sections=sections,
            metadata=metadata,
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_duplicate_section(self, result: Dict) -> str:
        """Format duplicate detector output"""
        lines = []
        lines.append(f"Total duplicates: {result.get('duplicates_found', 0)}")
        lines.append(f"Lines affected: {result.get('total_lines_duplicated', 0)}")
        lines.append(
            f"Space savings potential: {result.get('space_savings', '0 bytes')}"
        )

        if "groups" in result:
            lines.append("")
            lines.append("Top duplicate groups:")
            for i, group in enumerate(result["groups"][:5], 1):
                files = group.get("files", [])
                file_list = ", ".join(f[:30] for f in files[:3])
                if len(files) > 3:
                    file_list += f" (+{len(files)-3} more)"
                lines.append(
                    f"  {i}. {group.get('lines', 0)} lines across {len(files)} files"
                )
                lines.append(f"     Files: {file_list}")

        return "\n".join(lines)

    def _format_dead_code_section(self, result: Dict) -> str:
        """Format dead code eliminator output"""
        lines = []
        lines.append(f"Unused functions: {result.get('unused_functions', 0)}")
        lines.append(f"Unused imports: {result.get('unused_imports', 0)}")
        lines.append(f"Unused variables: {result.get('unused_variables', 0)}")
        lines.append(f"Removable lines: {result.get('removable_lines', 0)}")

        if "top_unused" in result:
            lines.append("")
            lines.append("Top candidates for removal:")
            for item in result["top_unused"][:5]:
                lines.append(
                    f"  - {item.get('name', 'unknown')} in {item.get('file', 'unknown')}"
                )

        return "\n".join(lines)

    def _format_organization_section(self, result: Dict) -> str:
        """Format code grouper output"""
        lines = []
        lines.append(f"Files analyzed: {result.get('files_analyzed', 0)}")
        lines.append(
            f"Current structure score: {result.get('organization_score', 'N/A')}/100"
        )

        if "suggested_moves" in result:
            lines.append("")
            lines.append("Suggested reorganizations:")
            for move in result["suggested_moves"][:5]:
                lines.append(
                    f"  - Move {move.get('file', '?')} to {move.get('suggested_location', '?')}"
                )

        if "new_directories" in result:
            lines.append("")
            lines.append("Suggested new directories:")
            for dir_name in result["new_directories"][:5]:
                lines.append(f"  - {dir_name}")

        return "\n".join(lines)

    def _format_refactoring_section(self, result: Dict) -> str:
        """Format refactor planner output"""
        lines = []

        if "priority_actions" in result:
            lines.append("Priority refactoring actions:")
            for i, action in enumerate(result["priority_actions"][:7], 1):
                if isinstance(action, dict):
                    lines.append(
                        f"  {i}. [{action.get('priority', 'MED')}] {action.get('description', 'No description')}"
                    )
                    if action.get("estimated_effort"):
                        lines.append(f"     Effort: {action.get('estimated_effort')}")
                else:
                    lines.append(f"  {i}. {action}")

        if "estimated_total_effort" in result:
            lines.append("")
            lines.append(f"Total estimated effort: {result['estimated_total_effort']}")

        return "\n".join(lines)

    # =========================================================================
    # CONTENT RESEARCH SYNTHESIS
    # =========================================================================

    def _synthesize_content_research(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize research results from search and quality assessment

        Inputs: omnisearch results, quality-assessor scores
        Output: Curated, ranked research findings
        """
        sections = []
        recommendations = []

        search_out = self._find_output(outputs, "omnisearch")
        quality_out = self._find_output(outputs, "quality-assessor")

        # Build summary
        total_results = 0
        high_quality_count = 0

        if search_out and search_out.success:
            results = search_out.result.get("results", [])
            total_results = len(results)

        if quality_out and quality_out.success:
            assessments = quality_out.result.get("assessments", [])
            high_quality_count = sum(1 for a in assessments if a.get("score", 0) >= 80)

        summary = f"Research complete. Found {total_results} sources, {high_quality_count} high-quality."

        # Search Results Section
        if search_out and search_out.success:
            sections.append(
                {
                    "title": "Search Results",
                    "icon": "[SRC]",
                    "content": self._format_search_results(search_out.result),
                    "priority": "high",
                    "ion": "omnisearch",
                }
            )

        # Quality Assessment Section
        if quality_out and quality_out.success:
            sections.append(
                {
                    "title": "Quality Assessment",
                    "icon": "[QUA]",
                    "content": self._format_quality_assessment(quality_out.result),
                    "priority": "high",
                    "ion": "quality-assessor",
                }
            )

            # Generate recommendations based on quality
            if high_quality_count > 0:
                recommendations.append(
                    f"HIGH: {high_quality_count} high-quality sources identified for immediate use"
                )
            if total_results > high_quality_count:
                recommendations.append(
                    f"LOW: {total_results - high_quality_count} sources need verification before use"
                )

        # Combined ranked results
        if search_out and quality_out:
            sections.append(
                {
                    "title": "Ranked Recommendations",
                    "icon": "[TOP]",
                    "content": self._format_ranked_sources(
                        search_out.result, quality_out.result
                    ),
                    "priority": "high",
                    "ion": "combined",
                }
            )

        return SynthesizedReport(
            title="Content Research Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_search_results(self, result: Dict) -> str:
        """Format omnisearch results"""
        lines = []
        results = result.get("results", [])

        lines.append(f"Total results: {len(results)}")
        lines.append(
            f"Sources searched: {', '.join(result.get('sources', ['unknown']))}"
        )
        lines.append("")

        if results:
            lines.append("Top results:")
            for i, r in enumerate(results[:10], 1):
                title = r.get("title", "Untitled")[:50]
                source = r.get("source", "unknown")
                lines.append(f"  {i}. [{source}] {title}")
                if r.get("url"):
                    lines.append(f"     {r.get('url')[:60]}")

        return "\n".join(lines)

    def _format_quality_assessment(self, result: Dict) -> str:
        """Format quality assessor results"""
        lines = []
        assessments = result.get("assessments", [])

        if assessments:
            avg_score = sum(a.get("score", 0) for a in assessments) / len(assessments)
            lines.append(f"Average quality score: {avg_score:.1f}/100")
            lines.append(f"Items assessed: {len(assessments)}")
            lines.append("")

            # Group by quality tier
            high = [a for a in assessments if a.get("score", 0) >= 80]
            medium = [a for a in assessments if 50 <= a.get("score", 0) < 80]
            low = [a for a in assessments if a.get("score", 0) < 50]

            lines.append(f"Quality breakdown:")
            lines.append(f"  High (80+):   {len(high)}")
            lines.append(f"  Medium (50-79): {len(medium)}")
            lines.append(f"  Low (<50):    {len(low)}")

        return "\n".join(lines)

    def _format_ranked_sources(self, search_result: Dict, quality_result: Dict) -> str:
        """Combine and rank sources by quality"""
        lines = []

        results = search_result.get("results", [])
        assessments = {a.get("id"): a for a in quality_result.get("assessments", [])}

        # Combine and sort
        ranked = []
        for r in results:
            assessment = assessments.get(r.get("id"), {})
            score = assessment.get("score", 50)
            ranked.append({**r, "quality_score": score})

        ranked.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        lines.append("Top recommended sources (by quality):")
        for i, r in enumerate(ranked[:5], 1):
            lines.append(
                f"  {i}. [{r.get('quality_score', 0)}/100] {r.get('title', 'Untitled')[:45]}"
            )

        return "\n".join(lines)

    # =========================================================================
    # PROJECT STATUS SYNTHESIS
    # =========================================================================

    def _synthesize_project_status(self, outputs: List[IonOutput]) -> SynthesizedReport:
        """
        Synthesize project status from multiple sources

        Inputs: git state, activity logs, health checks, test results
        Output: Executive project status dashboard
        """
        sections = []
        recommendations = []

        git_out = self._find_output(outputs, "git-status")
        health_out = self._find_output(outputs, "health-check")
        activity_out = self._find_output(outputs, "activity-log")
        test_out = self._find_output(outputs, "test-runner")

        # Build status summary
        status_parts = []
        overall_health = "HEALTHY"

        if git_out and git_out.success:
            branch = git_out.result.get("branch", "unknown")
            uncommitted = git_out.result.get("uncommitted_changes", 0)
            status_parts.append(f"Branch: {branch}")
            if uncommitted > 0:
                status_parts.append(f"{uncommitted} uncommitted changes")
                recommendations.append("LOW: Commit or stash uncommitted changes")

        if health_out and health_out.success:
            health_score = health_out.result.get("score", 100)
            if health_score < 50:
                overall_health = "CRITICAL"
                recommendations.append(
                    "HIGH: Address critical health issues immediately"
                )
            elif health_score < 80:
                overall_health = "WARNING"
                recommendations.append("MEDIUM: Review health warnings")
            status_parts.append(f"Health: {health_score}%")

        if test_out and test_out.success:
            passed = test_out.result.get("passed", 0)
            failed = test_out.result.get("failed", 0)
            status_parts.append(f"Tests: {passed} passed, {failed} failed")
            if failed > 0:
                overall_health = (
                    "WARNING" if overall_health == "HEALTHY" else overall_health
                )
                recommendations.append("HIGH: Fix failing tests")

        summary = f"Project Status: {overall_health}. " + ", ".join(status_parts) + "."

        # Git Section
        if git_out and git_out.success:
            sections.append(
                {
                    "title": "Git Status",
                    "icon": "[GIT]",
                    "content": self._format_git_status(git_out.result),
                    "priority": "medium",
                    "ion": "git-status",
                }
            )

        # Health Section
        if health_out and health_out.success:
            sections.append(
                {
                    "title": "System Health",
                    "icon": "[HLT]",
                    "content": self._format_health_status(health_out.result),
                    "priority": (
                        "high" if health_out.result.get("score", 100) < 80 else "low"
                    ),
                    "ion": "health-check",
                }
            )

        # Activity Section
        if activity_out and activity_out.success:
            sections.append(
                {
                    "title": "Recent Activity",
                    "icon": "[ACT]",
                    "content": self._format_activity_log(activity_out.result),
                    "priority": "low",
                    "ion": "activity-log",
                }
            )

        # Test Section
        if test_out and test_out.success:
            sections.append(
                {
                    "title": "Test Results",
                    "icon": "[TST]",
                    "content": self._format_test_results(test_out.result),
                    "priority": (
                        "high" if test_out.result.get("failed", 0) > 0 else "low"
                    ),
                    "ion": "test-runner",
                }
            )

        return SynthesizedReport(
            title="Project Status Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_git_status(self, result: Dict) -> str:
        """Format git status"""
        lines = []
        lines.append(f"Branch: {result.get('branch', 'unknown')}")
        lines.append(f"Last commit: {result.get('last_commit', 'unknown')}")
        lines.append(f"Uncommitted changes: {result.get('uncommitted_changes', 0)}")
        lines.append(f"Untracked files: {result.get('untracked_files', 0)}")

        if result.get("commits_today"):
            lines.append("")
            lines.append(f"Today's commits ({len(result['commits_today'])}):")
            for c in result["commits_today"][:5]:
                lines.append(f"  - {c}")

        return "\n".join(lines)

    def _format_health_status(self, result: Dict) -> str:
        """Format health check results"""
        lines = []
        lines.append(f"Overall score: {result.get('score', 0)}/100")

        if result.get("checks"):
            lines.append("")
            lines.append("Health checks:")
            for check in result["checks"]:
                status = "[OK]" if check.get("passed") else "[XX]"
                lines.append(f"  {status} {check.get('name', 'unknown')}")

        return "\n".join(lines)

    def _format_activity_log(self, result: Dict) -> str:
        """Format activity log"""
        lines = []
        activities = result.get("activities", [])

        lines.append(f"Recent activities: {len(activities)}")
        if activities:
            lines.append("")
            for act in activities[:10]:
                time_str = act.get("time", "unknown")
                action = act.get("action", "unknown")
                lines.append(f"  [{time_str}] {action}")

        return "\n".join(lines)

    def _format_test_results(self, result: Dict) -> str:
        """Format test results"""
        lines = []
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        total = passed + failed

        lines.append(f"Total tests: {total}")
        lines.append(f"Passed: {passed}")
        lines.append(f"Failed: {failed}")
        if total > 0:
            lines.append(f"Success rate: {(passed/total)*100:.1f}%")

        if result.get("failed_tests"):
            lines.append("")
            lines.append("Failed tests:")
            for test in result["failed_tests"][:5]:
                lines.append(f"  - {test}")

        return "\n".join(lines)

    # =========================================================================
    # CODE CLEANUP SYNTHESIS
    # =========================================================================

    def _synthesize_code_cleanup(self, outputs: List[IonOutput]) -> SynthesizedReport:
        """
        Synthesize code cleanup recommendations

        Inputs: All cleanup-related Ion outputs
        Output: Prioritized cleanup action plan
        """
        sections = []
        recommendations = []

        # Aggregate all cleanup findings
        total_issues = 0
        total_savings = 0

        for output in outputs:
            if output.success:
                issues = output.result.get("issues_found", 0)
                savings = output.result.get("lines_removable", 0)
                total_issues += issues
                total_savings += savings

        summary = f"Code cleanup analysis complete. {total_issues} issues found, {total_savings} lines can be cleaned up."

        # Group outputs by type
        for output in outputs:
            if output.success:
                sections.append(
                    {
                        "title": f"{output.ion_name.replace('-', ' ').title()}",
                        "icon": f"[{output.ion_name[:3].upper()}]",
                        "content": self._format_cleanup_findings(output.result),
                        "priority": self._determine_cleanup_priority(output.result),
                        "ion": output.ion_name,
                    }
                )

        # Priority sort
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sections.sort(key=lambda s: priority_order.get(s.get("priority", "low"), 3))

        # Generate recommendations
        if total_issues > 10:
            recommendations.append(
                "HIGH: Significant cleanup opportunity - schedule dedicated cleanup sprint"
            )
        if total_savings > 500:
            recommendations.append(
                f"MEDIUM: Can remove {total_savings} lines - reduces maintenance burden"
            )

        return SynthesizedReport(
            title="Code Cleanup Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_cleanup_findings(self, result: Dict) -> str:
        """Format generic cleanup findings"""
        lines = []
        lines.append(f"Issues found: {result.get('issues_found', 0)}")
        lines.append(f"Lines removable: {result.get('lines_removable', 0)}")

        if result.get("top_items"):
            lines.append("")
            lines.append("Top items:")
            for item in result["top_items"][:5]:
                if isinstance(item, dict):
                    lines.append(f"  - {item.get('description', str(item))}")
                else:
                    lines.append(f"  - {item}")

        return "\n".join(lines)

    def _determine_cleanup_priority(self, result: Dict) -> str:
        """Determine priority based on cleanup metrics"""
        issues = result.get("issues_found", 0)
        if issues > 10:
            return "high"
        elif issues > 3:
            return "medium"
        return "low"

    # =========================================================================
    # LEARNING MATERIALS SYNTHESIS
    # =========================================================================

    def _synthesize_learning_materials(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize learning material generation

        Inputs: Content extraction, module generation, quiz creation
        Output: Complete learning package overview
        """
        sections = []
        recommendations = []

        extract_out = self._find_output(outputs, "content-extractor")
        module_out = self._find_output(outputs, "module-generator")
        quiz_out = self._find_output(outputs, "quiz-generator")

        # Build summary
        content_items = 0
        modules_created = 0
        questions_generated = 0

        if extract_out and extract_out.success:
            content_items = extract_out.result.get("items_extracted", 0)

        if module_out and module_out.success:
            modules_created = module_out.result.get("modules_created", 0)

        if quiz_out and quiz_out.success:
            # Check both result and metrics for questions count
            questions_generated = quiz_out.result.get("questions_generated", 0)
            if questions_generated == 0:
                # Try getting from questions array
                questions = quiz_out.result.get("questions", [])
                questions_generated = len(questions)

        summary = f"Learning materials ready. {content_items} content items extracted, {modules_created} modules created, {questions_generated} quiz questions generated."

        # Content Extraction Section
        if extract_out and extract_out.success:
            sections.append(
                {
                    "title": "Content Extraction",
                    "icon": "[EXT]",
                    "content": self._format_content_extraction(extract_out.result),
                    "priority": "high",
                    "ion": "content-extractor",
                }
            )

        # Module Generation Section
        if module_out and module_out.success:
            sections.append(
                {
                    "title": "Generated Modules",
                    "icon": "[MOD]",
                    "content": self._format_module_generation(module_out.result),
                    "priority": "high",
                    "ion": "module-generator",
                }
            )

        # Quiz Generation Section
        if quiz_out and quiz_out.success:
            sections.append(
                {
                    "title": "Quiz Questions",
                    "icon": "[QIZ]",
                    "content": self._format_quiz_generation(quiz_out.result),
                    "priority": "medium",
                    "ion": "quiz-generator",
                }
            )

        # Recommendations
        if modules_created > 0:
            recommendations.append(
                f"HIGH: {modules_created} modules ready for review and deployment"
            )
        if questions_generated > 0:
            recommendations.append(
                f"MEDIUM: Review {questions_generated} generated questions for accuracy"
            )

        return SynthesizedReport(
            title="Learning Materials Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_content_extraction(self, result: Dict) -> str:
        """Format content extraction results"""
        lines = []
        lines.append(f"Items extracted: {result.get('items_extracted', 0)}")
        lines.append(f"Source type: {result.get('source_type', 'unknown')}")
        lines.append(f"Total duration: {result.get('total_duration', 'N/A')}")

        if result.get("topics"):
            lines.append("")
            lines.append("Topics identified:")
            for topic in result["topics"][:5]:
                lines.append(f"  - {topic}")

        return "\n".join(lines)

    def _format_module_generation(self, result: Dict) -> str:
        """Format module generation results"""
        lines = []
        lines.append(f"Modules created: {result.get('modules_created', 0)}")

        if result.get("modules"):
            lines.append("")
            lines.append("Generated modules:")
            for mod in result["modules"][:5]:
                if isinstance(mod, dict):
                    lines.append(
                        f"  - {mod.get('title', 'Untitled')} ({mod.get('duration', 'N/A')})"
                    )
                else:
                    lines.append(f"  - {mod}")

        return "\n".join(lines)

    def _format_quiz_generation(self, result: Dict) -> str:
        """Format quiz generation results"""
        lines = []

        # Get questions from result
        questions = result.get("questions", [])
        questions_count = (
            len(questions) if questions else result.get("questions_generated", 0)
        )

        lines.append(f"Questions generated: {questions_count}")

        # Show actual questions if available
        if questions:
            lines.append("")
            lines.append("Sample questions:")
            for i, q in enumerate(questions[:3], 1):
                q_type = q.get("type", "unknown")
                difficulty = q.get("difficulty", "medium")
                question_text = q.get("question", "No text")[:80]
                lines.append(f"  {i}. [{q_type}] [{difficulty}] {question_text}...")

            if len(questions) > 3:
                lines.append(f"  ... and {len(questions) - 3} more questions")

        # Question type distribution
        if questions:
            type_counts = {}
            for q in questions:
                qtype = q.get("type", "unknown")
                type_counts[qtype] = type_counts.get(qtype, 0) + 1

            if type_counts:
                lines.append("")
                lines.append("Question types:")
                for qtype, count in sorted(type_counts.items()):
                    lines.append(f"  - {qtype}: {count}")
        elif result.get("by_type"):
            lines.append("")
            lines.append("Question types:")
            for qtype, count in result["by_type"].items():
                lines.append(f"  - {qtype}: {count}")

        # Difficulty distribution
        if questions:
            diff_counts = {}
            for q in questions:
                diff = q.get("difficulty", "medium")
                diff_counts[diff] = diff_counts.get(diff, 0) + 1

            if diff_counts:
                lines.append("")
                lines.append("Difficulty distribution:")
                for diff, count in sorted(diff_counts.items()):
                    lines.append(f"  - {diff}: {count}")
        elif result.get("by_difficulty"):
            lines.append("")
            lines.append("Difficulty distribution:")
            for diff, count in result["by_difficulty"].items():
                lines.append(f"  - {diff}: {count}")

        return "\n".join(lines)

    # =========================================================================
    # QUALITY ASSESSMENT SYNTHESIS
    # =========================================================================

    def _synthesize_quality_assessment(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize quality assessment results

        Inputs: quality-assessor Ion output(s)
        Output: Quality report with scores and recommendations
        """
        sections = []
        recommendations = []

        # Find quality assessor output
        quality_out = self._find_output(outputs, "quality-assessor")

        if quality_out and quality_out.success:
            result = quality_out.result

            # Overall score
            overall_score = result.get("overall_score", 0)
            dimension_scores = result.get("dimension_scores", {})

            # Build summary
            summary = f"Content Quality Score: {overall_score:.1f}/100"

            # Add dimension breakdown section
            if dimension_scores:
                dim_lines = []
                for dim, score in dimension_scores.items():
                    status = (
                        "EXCELLENT"
                        if score >= 80
                        else "GOOD" if score >= 60 else "NEEDS WORK"
                    )
                    dim_lines.append(f"{dim.title()}: {score:.1f}/100 ({status})")

                sections.append(
                    {
                        "title": "Quality Dimensions",
                        "icon": "[QA]",
                        "content": "\n".join(dim_lines),
                        "priority": "high",
                        "ion": "quality-assessor",
                    }
                )

            # Generate recommendations based on scores
            if overall_score < 60:
                recommendations.append("HIGH: Content quality needs improvement")
            for dim, score in dimension_scores.items():
                if score < 50:
                    recommendations.append(
                        f"MEDIUM: Improve {dim} (currently {score:.0f}/100)"
                    )

            # Add any Ion-provided recommendations
            if result.get("recommendations"):
                for rec in result["recommendations"]:
                    recommendations.append(f"LOW: {rec}")
        else:
            summary = "Quality assessment could not be completed"
            recommendations.append("HIGH: Re-run quality assessment with valid content")

        # Add generic outputs for other Ions
        for output in outputs:
            if output.ion_name != "quality-assessor":
                sections.append(
                    {
                        "title": (
                            f"[OK] {output.ion_name}"
                            if output.success
                            else f"[XX] {output.ion_name}"
                        ),
                        "icon": "[OK]" if output.success else "[XX]",
                        "content": self._format_generic_output(output),
                        "priority": "medium",
                        "ion": output.ion_name,
                    }
                )

        return SynthesizedReport(
            title="Content Quality Assessment",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    # =========================================================================
    # REFACTORING SYNTHESIS
    # =========================================================================

    def _synthesize_refactoring(self, outputs: List[IonOutput]) -> SynthesizedReport:
        """
        Synthesize refactoring recommendations

        Inputs: refactor-planner + supporting analysis Ions
        Output: Prioritized refactoring roadmap
        """
        sections = []
        recommendations = []

        # Find refactor planner output
        refactor_out = self._find_output(outputs, "refactor-planner")

        if refactor_out and refactor_out.success:
            result = refactor_out.result

            # Build summary from roadmap
            total_items = result.get("total_items", 0)
            high_priority = result.get("high_priority_count", 0)
            estimated_hours = result.get("estimated_hours", 0)

            summary = f"Refactoring Roadmap: {total_items} items identified, {high_priority} high-priority"
            if estimated_hours > 0:
                summary += f" (Est. {estimated_hours}h total)"

            # High priority section
            if result.get("high_priority"):
                high_lines = []
                for item in result["high_priority"][:5]:
                    high_lines.append(f"- {item.get('description', 'Unknown')}")
                    if item.get("reason"):
                        high_lines.append(f"  Reason: {item['reason']}")

                sections.append(
                    {
                        "title": "High Priority Refactors",
                        "icon": "[!!!]",
                        "content": "\n".join(high_lines),
                        "priority": "high",
                        "ion": "refactor-planner",
                    }
                )
                recommendations.append(
                    f"HIGH: Address {len(result['high_priority'])} critical refactoring items"
                )

            # Medium priority section
            if result.get("medium_priority"):
                med_lines = []
                for item in result["medium_priority"][:5]:
                    med_lines.append(f"- {item.get('description', 'Unknown')}")

                sections.append(
                    {
                        "title": "Medium Priority Refactors",
                        "icon": "[!!]",
                        "content": "\n".join(med_lines),
                        "priority": "medium",
                        "ion": "refactor-planner",
                    }
                )

            # Low priority section
            if result.get("low_priority"):
                low_lines = []
                for item in result["low_priority"][:3]:
                    low_lines.append(f"- {item.get('description', 'Unknown')}")

                sections.append(
                    {
                        "title": "Low Priority Refactors",
                        "icon": "[!]",
                        "content": "\n".join(low_lines),
                        "priority": "low",
                        "ion": "refactor-planner",
                    }
                )
        else:
            summary = "Refactoring analysis completed"

        # Add supporting analysis (duplicates, dead code, etc.)
        for output in outputs:
            if output.ion_name != "refactor-planner" and output.success:
                sections.append(
                    {
                        "title": f"Supporting: {output.ion_name}",
                        "icon": "[+]",
                        "content": self._format_generic_output(output),
                        "priority": "low",
                        "ion": output.ion_name,
                    }
                )

        return SynthesizedReport(
            title="Refactoring Roadmap",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    # =========================================================================
    # DOCUMENTATION SYNTHESIS
    # =========================================================================

    def _synthesize_documentation(self, outputs: List[IonOutput]) -> SynthesizedReport:
        """
        Synthesize documentation generation results

        Inputs: doc-generator Ion output(s)
        Output: Generated documentation summary
        """
        sections = []
        recommendations = []

        # Collect all documentation outputs
        docs_generated = 0
        for output in outputs:
            if output.success:
                result = output.result
                docs_count = result.get("docs_generated", 1)
                docs_generated += docs_count

                sections.append(
                    {
                        "title": f"Generated: {output.ion_name}",
                        "icon": "[DOC]",
                        "content": self._format_doc_output(result),
                        "priority": "medium",
                        "ion": output.ion_name,
                    }
                )

        summary = f"Documentation generated: {docs_generated} document(s)"

        if docs_generated == 0:
            recommendations.append(
                "HIGH: No documentation was generated - check inputs"
            )

        return SynthesizedReport(
            title="Documentation Generation Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_doc_output(self, result: Dict) -> str:
        """Format documentation generation results"""
        lines = []
        if result.get("output_path"):
            lines.append(f"Output: {result['output_path']}")
        if result.get("format"):
            lines.append(f"Format: {result['format']}")
        if result.get("sections"):
            lines.append(f"Sections: {len(result['sections'])}")
        if result.get("word_count"):
            lines.append(f"Word count: {result['word_count']}")
        return "\n".join(lines) if lines else "Documentation generated successfully"

    # =========================================================================
    # CONTENT EXTRACTION SYNTHESIS
    # =========================================================================

    def _synthesize_content_extraction(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize content extraction results

        Inputs: content-fetcher, omnisearch, etc.
        Output: Extracted content summary
        """
        sections = []
        recommendations = []
        total_items = 0

        for output in outputs:
            if output.success:
                result = output.result

                # Count extracted items
                items = result.get("items_extracted", result.get("results_count", 1))
                total_items += items

                # Build section content
                content_lines = []
                if result.get("title"):
                    content_lines.append(f"Title: {result['title']}")
                if result.get("source"):
                    content_lines.append(f"Source: {result['source']}")
                if result.get("duration"):
                    content_lines.append(f"Duration: {result['duration']}")
                if result.get("transcript_length"):
                    content_lines.append(
                        f"Transcript: {result['transcript_length']} chars"
                    )

                sections.append(
                    {
                        "title": f"Extracted: {output.ion_name}",
                        "icon": "[EXT]",
                        "content": (
                            "\n".join(content_lines)
                            if content_lines
                            else "Content extracted"
                        ),
                        "priority": "medium",
                        "ion": output.ion_name,
                    }
                )
            else:
                sections.append(
                    {
                        "title": f"Failed: {output.ion_name}",
                        "icon": "[XX]",
                        "content": f"Error: {output.error or 'Unknown error'}",
                        "priority": "high",
                        "ion": output.ion_name,
                    }
                )
                recommendations.append(f"HIGH: {output.ion_name} extraction failed")

        summary = f"Content extraction complete: {total_items} item(s) extracted"

        return SynthesizedReport(
            title="Content Extraction Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    # =========================================================================
    # QUIZ GENERATION SYNTHESIS
    # =========================================================================

    def _synthesize_quiz_generation(
        self, outputs: List[IonOutput]
    ) -> SynthesizedReport:
        """
        Synthesize quiz generation results

        Inputs: quiz-generator Ion output
        Output: Quiz generation summary with questions
        """
        sections = []
        recommendations = []

        # Find quiz generator output
        quiz_out = self._find_output(outputs, "quiz-generator")

        if quiz_out and quiz_out.success:
            result = quiz_out.result

            questions = result.get("questions", [])
            summary = f"Generated {len(questions)} quiz question(s)"

            # Questions overview section
            if questions:
                q_lines = []
                for i, q in enumerate(questions[:5], 1):
                    q_type = q.get("type", "unknown")
                    difficulty = q.get("difficulty", "medium")
                    q_lines.append(
                        f"{i}. [{q_type}] [{difficulty}] {q.get('question', 'No text')[:60]}..."
                    )

                if len(questions) > 5:
                    q_lines.append(f"... and {len(questions) - 5} more questions")

                sections.append(
                    {
                        "title": "Generated Questions",
                        "icon": "[Q]",
                        "content": "\n".join(q_lines),
                        "priority": "high",
                        "ion": "quiz-generator",
                    }
                )

            # TEKS alignment section
            teks_aligned = [q for q in questions if q.get("teks_alignment")]
            if teks_aligned:
                teks_set = set(q["teks_alignment"] for q in teks_aligned)
                sections.append(
                    {
                        "title": "TEKS Alignment",
                        "icon": "[TEKS]",
                        "content": f"Standards covered: {', '.join(sorted(teks_set))}",
                        "priority": "medium",
                        "ion": "quiz-generator",
                    }
                )

            # Difficulty distribution
            diff_counts = {}
            for q in questions:
                d = q.get("difficulty", "medium")
                diff_counts[d] = diff_counts.get(d, 0) + 1

            if diff_counts:
                diff_lines = [f"{d}: {c}" for d, c in sorted(diff_counts.items())]
                sections.append(
                    {
                        "title": "Difficulty Distribution",
                        "icon": "[D]",
                        "content": "\n".join(diff_lines),
                        "priority": "low",
                        "ion": "quiz-generator",
                    }
                )
        else:
            summary = "Quiz generation failed or incomplete"
            recommendations.append("HIGH: Review quiz generation input and try again")

        return SynthesizedReport(
            title="Quiz Generation Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    # =========================================================================
    # GENERIC SYNTHESIS
    # =========================================================================

    def _synthesize_generic(self, outputs: List[IonOutput]) -> SynthesizedReport:
        """Generic synthesis for unknown patterns"""
        sections = []

        successful = [o for o in outputs if o.success]
        failed = [o for o in outputs if not o.success]

        summary = (
            f"Completed {len(successful)}/{len(outputs)} Ion executions successfully."
        )

        for output in outputs:
            status = "[OK]" if output.success else "[XX]"
            sections.append(
                {
                    "title": f"{status} {output.ion_name}",
                    "icon": status,
                    "content": self._format_generic_output(output),
                    "priority": "medium" if output.success else "high",
                    "ion": output.ion_name,
                }
            )

        recommendations = []
        if failed:
            recommendations.append(f"HIGH: {len(failed)} Ion(s) failed - review errors")

        return SynthesizedReport(
            title="Task Execution Report",
            summary=summary,
            sections=sections,
            metadata=self._build_metadata(outputs),
            raw_outputs=outputs,
            recommendations=recommendations,
        )

    def _format_generic_output(self, output: IonOutput) -> str:
        """Format generic Ion output"""
        lines = []
        lines.append(f"Ion: {output.ion_name}")
        lines.append(f"Description: {output.description}")
        lines.append(f"Success: {output.success}")
        lines.append(f"Execution time: {output.execution_time_ms}ms")

        if output.error:
            lines.append(f"Error: {output.error}")

        if output.result:
            lines.append("")
            lines.append("Result:")
            result_str = json.dumps(output.result, indent=2)
            # Truncate if too long
            if len(result_str) > 500:
                result_str = result_str[:500] + "\n... (truncated)"
            lines.append(result_str)

        return "\n".join(lines)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _find_output(
        self, outputs: List[IonOutput], ion_name: str
    ) -> Optional[IonOutput]:
        """Find output by Ion name"""
        return next((o for o in outputs if o.ion_name == ion_name), None)

    def _build_metadata(self, outputs: List[IonOutput]) -> Dict[str, Any]:
        """Build standard metadata from outputs"""
        return {
            "total_ions": len(outputs),
            "successful_ions": sum(1 for o in outputs if o.success),
            "failed_ions": sum(1 for o in outputs if not o.success),
            "total_execution_time_ms": sum(o.execution_time_ms for o in outputs),
            "average_execution_time_ms": (
                sum(o.execution_time_ms for o in outputs) / len(outputs)
                if outputs
                else 0
            ),
            "timestamp": datetime.now().isoformat(),
            "ions_used": [o.ion_name for o in outputs],
        }

    # =========================================================================
    # OUTPUT FORMATTERS
    # =========================================================================

    def format_as_text(self, report: SynthesizedReport) -> str:
        """Format synthesized report as readable terminal text"""
        lines = []

        # Header
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"  {report.title.upper()}")
        lines.append("=" * 80)
        lines.append(
            f"  Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("")

        # Summary
        lines.append("[SUMMARY]")
        lines.append("-" * 80)
        lines.append(f"  {report.summary}")
        lines.append("")

        # Recommendations (if any)
        if report.recommendations:
            lines.append("[RECOMMENDATIONS]")
            lines.append("-" * 80)
            for rec in report.recommendations:
                lines.append(f"  -> {rec}")
            lines.append("")

        # Sections
        for section in report.sections:
            icon = section.get("icon", "[---]")
            title = section.get("title", "Section")
            priority = section.get("priority", "medium").upper()

            lines.append(f"{icon} {title} [{priority}]")
            lines.append("-" * 80)

            # Indent content
            for line in section["content"].split("\n"):
                lines.append(f"  {line}")
            lines.append("")

        # Metadata footer
        lines.append("=" * 80)
        lines.append("  EXECUTION METADATA")
        lines.append("=" * 80)
        lines.append(f"  Ions executed: {report.metadata.get('total_ions', 0)}")
        lines.append(f"  Successful: {report.metadata.get('successful_ions', 0)}")
        lines.append(f"  Failed: {report.metadata.get('failed_ions', 0)}")
        lines.append(
            f"  Total time: {report.metadata.get('total_execution_time_ms', 0):.0f}ms"
        )
        lines.append(
            f"  Average time: {report.metadata.get('average_execution_time_ms', 0):.0f}ms"
        )
        lines.append("")

        return "\n".join(lines)

    def format_as_markdown(self, report: SynthesizedReport) -> str:
        """Format synthesized report as markdown"""
        lines = []

        # Header
        lines.append(f"# {report.title}")
        lines.append("")
        lines.append(
            f"*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*"
        )
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(report.summary)
        lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Sections
        for section in report.sections:
            title = section.get("title", "Section")
            priority = section.get("priority", "medium")

            lines.append(f"## {title}")
            lines.append("")
            lines.append(f"**Priority:** {priority}")
            lines.append("")
            lines.append("```")
            lines.append(section["content"])
            lines.append("```")
            lines.append("")

        # Metadata
        lines.append("## Execution Metadata")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Ions executed | {report.metadata.get('total_ions', 0)} |")
        lines.append(f"| Successful | {report.metadata.get('successful_ions', 0)} |")
        lines.append(f"| Failed | {report.metadata.get('failed_ions', 0)} |")
        lines.append(
            f"| Total time | {report.metadata.get('total_execution_time_ms', 0):.0f}ms |"
        )
        lines.append(
            f"| Average time | {report.metadata.get('average_execution_time_ms', 0):.0f}ms |"
        )
        lines.append("")

        return "\n".join(lines)

    def format_as_json(self, report: SynthesizedReport) -> str:
        """Format synthesized report as JSON"""
        return json.dumps(
            {
                "title": report.title,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "sections": report.sections,
                "metadata": report.metadata,
                "generated_at": report.generated_at.isoformat(),
                "raw_output_count": len(report.raw_outputs),
            },
            indent=2,
        )

    def format_as_html(self, report: SynthesizedReport) -> str:
        """Format synthesized report as HTML"""
        priority_colors = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}

        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html><head>")
        html.append("<title>" + report.title + "</title>")
        html.append("<style>")
        html.append(
            "body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }"
        )
        html.append(
            "h1 { color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }"
        )
        html.append("h2 { color: #ff6b6b; margin-top: 30px; }")
        html.append(
            ".summary { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }"
        )
        html.append(
            ".section { background: #0f3460; padding: 15px; border-radius: 8px; margin: 15px 0; }"
        )
        html.append(
            ".priority { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }"
        )
        html.append(
            ".metadata { background: #1a1a2e; border: 1px solid #333; padding: 15px; border-radius: 8px; }"
        )
        html.append(
            ".recommendations { background: #2d132c; padding: 15px; border-radius: 8px; margin: 20px 0; }"
        )
        html.append(
            "pre { background: #0a0a15; padding: 15px; border-radius: 4px; overflow-x: auto; }"
        )
        html.append("</style>")
        html.append("</head><body>")

        # Header
        html.append(f"<h1>{report.title}</h1>")
        html.append(
            f"<p><em>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</em></p>"
        )

        # Summary
        html.append("<div class='summary'>")
        html.append(f"<strong>Summary:</strong> {report.summary}")
        html.append("</div>")

        # Recommendations
        if report.recommendations:
            html.append("<div class='recommendations'>")
            html.append("<h2>Recommendations</h2>")
            html.append("<ul>")
            for rec in report.recommendations:
                html.append(f"<li>{rec}</li>")
            html.append("</ul>")
            html.append("</div>")

        # Sections
        for section in report.sections:
            priority = section.get("priority", "medium")
            color = priority_colors.get(priority, "#6c757d")

            html.append("<div class='section'>")
            html.append(f"<h2>{section.get('title', 'Section')} ")
            html.append(
                f"<span class='priority' style='background:{color};color:#fff;'>{priority.upper()}</span></h2>"
            )
            html.append(f"<pre>{section['content']}</pre>")
            html.append("</div>")

        # Metadata
        html.append("<div class='metadata'>")
        html.append("<h2>Execution Metadata</h2>")
        html.append("<table>")
        html.append(
            f"<tr><td>Ions executed:</td><td>{report.metadata.get('total_ions', 0)}</td></tr>"
        )
        html.append(
            f"<tr><td>Successful:</td><td>{report.metadata.get('successful_ions', 0)}</td></tr>"
        )
        html.append(
            f"<tr><td>Failed:</td><td>{report.metadata.get('failed_ions', 0)}</td></tr>"
        )
        html.append(
            f"<tr><td>Total time:</td><td>{report.metadata.get('total_execution_time_ms', 0):.0f}ms</td></tr>"
        )
        html.append("</table>")
        html.append("</div>")

        html.append("</body></html>")

        return "\n".join(html)

    def save_report(
        self, report: SynthesizedReport, path: Path, format: str = "text"
    ) -> Path:
        """Save report to file in specified format"""
        formatters = {
            "text": (self.format_as_text, ".txt"),
            "markdown": (self.format_as_markdown, ".md"),
            "json": (self.format_as_json, ".json"),
            "html": (self.format_as_html, ".html"),
        }

        formatter, ext = formatters.get(format, (self.format_as_text, ".txt"))
        content = formatter(report)

        # Ensure path has correct extension
        if not str(path).endswith(ext):
            path = Path(str(path) + ext)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return path


# =============================================================================
# DEMO / TEST
# =============================================================================


def demo():
    """Demonstrate the OutputSynthesizer"""
    print("=" * 80)
    print("  OUTPUT SYNTHESIZER DEMO")
    print("=" * 80)
    print()

    synthesizer = OutputSynthesizer()

    # Create mock Ion outputs
    mock_outputs = [
        IonOutput(
            ion_name="duplicate-detector",
            description="Detect code duplicates",
            success=True,
            result={
                "duplicates_found": 7,
                "total_lines_duplicated": 156,
                "space_savings": "3.2 KB",
                "groups": [
                    {"lines": 45, "files": ["src/utils.py", "src/helpers.py"]},
                    {
                        "lines": 32,
                        "files": ["api/handlers.py", "api/routes.py", "api/views.py"],
                    },
                    {
                        "lines": 28,
                        "files": ["tests/test_utils.py", "tests/test_helpers.py"],
                    },
                ],
            },
            execution_time_ms=87,
        ),
        IonOutput(
            ion_name="dead-code-eliminator",
            description="Find unused code",
            success=True,
            result={
                "unused_functions": 12,
                "unused_imports": 8,
                "unused_variables": 5,
                "removable_lines": 234,
                "top_unused": [
                    {"name": "old_handler()", "file": "api/deprecated.py"},
                    {"name": "legacy_transform()", "file": "utils/compat.py"},
                ],
            },
            execution_time_ms=124,
        ),
        IonOutput(
            ion_name="code-grouper",
            description="Analyze code organization",
            success=True,
            result={
                "files_analyzed": 47,
                "organization_score": 72,
                "misplaced_files": 3,
                "suggested_moves": [
                    {
                        "file": "utils/api_helpers.py",
                        "suggested_location": "api/utils/",
                    },
                    {
                        "file": "tests/integration.py",
                        "suggested_location": "tests/integration/",
                    },
                ],
                "new_directories": ["api/utils/", "core/models/"],
            },
            execution_time_ms=56,
        ),
        IonOutput(
            ion_name="refactor-planner",
            description="Generate refactoring plan",
            success=True,
            result={
                "priority_actions": [
                    {
                        "priority": "HIGH",
                        "description": "Extract duplicate formatDate() to shared utils",
                        "estimated_effort": "30 min",
                    },
                    {
                        "priority": "HIGH",
                        "description": "Remove deprecated handler module",
                        "estimated_effort": "1 hour",
                    },
                    {
                        "priority": "MED",
                        "description": "Consolidate API response helpers",
                        "estimated_effort": "2 hours",
                    },
                    {
                        "priority": "LOW",
                        "description": "Reorganize test fixtures",
                        "estimated_effort": "1 hour",
                    },
                ],
                "estimated_total_effort": "4.5 hours",
            },
            execution_time_ms=198,
        ),
    ]

    # Synthesize
    print("Synthesizing codebase analysis from 4 Ion outputs...")
    print()

    report = synthesizer.synthesize("codebase_analysis", mock_outputs)

    # Output in different formats
    print("=" * 80)
    print("  TEXT FORMAT")
    print("=" * 80)
    print(synthesizer.format_as_text(report))

    print()
    print("=" * 80)
    print("  MARKDOWN FORMAT (first 50 lines)")
    print("=" * 80)
    md = synthesizer.format_as_markdown(report)
    print("\n".join(md.split("\n")[:50]))
    print("...")

    print()
    print("=" * 80)
    print("  JSON FORMAT (truncated)")
    print("=" * 80)
    json_out = synthesizer.format_as_json(report)
    print(json_out[:1000] + "\n...")

    print()
    print("[OK] Demo complete - synthesizer is operational!")
    print()


if __name__ == "__main__":
    demo()
