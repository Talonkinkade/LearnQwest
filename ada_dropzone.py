"""
ADA Dropzone - File-Based Activation Interface for ADA Orchestration

Watches dropzone directories and automatically triggers ADA Ion orchestration
when content is dropped in.

Usage:
    # Start dropzone monitor
    python ada_dropzone.py --watch

    # Process single file
    python ada_dropzone.py --file path/to/content.txt

    # Process once and exit
    python ada_dropzone.py --once

Dropzone Structure:
    dropzones/
    ├── inbox/          # Drop content here (YouTube URLs, text, JSON specs)
    ├── processing/     # Currently being processed
    ├── completed/      # Successfully processed
    ├── failed/         # Processing failed
    └── logs/           # Processing logs
"""

import asyncio
import json
import shutil
import sys
import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any, List


class DropzoneStatus(Enum):
    """Task processing status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DropzoneItem:
    """Represents an item dropped in the dropzone"""
    id: str
    filename: str
    filepath: Path
    content_type: str
    timestamp: datetime
    status: DropzoneStatus
    task_generated: Optional[str] = None
    ions_used: Optional[List[str]] = None
    processing_start: Optional[datetime] = None
    processing_end: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['filepath'] = str(self.filepath)
        data['timestamp'] = self.timestamp.isoformat()
        data['status'] = self.status.value
        if self.processing_start:
            data['processing_start'] = self.processing_start.isoformat()
        if self.processing_end:
            data['processing_end'] = self.processing_end.isoformat()
        return data


class ContentAnalyzer:
    """Analyzes dropped content to determine appropriate task"""

    # Content patterns that map to ADA tasks
    CONTENT_PATTERNS = {
        # YouTube content
        'youtube_url': {
            'patterns': ['youtube.com', 'youtu.be'],
            'task_template': 'Extract educational content from YouTube video: {content}',
            'ions': ['content-fetcher-ion', 'quality-assessor-ion']
        },
        # Quiz requests
        'quiz_json': {
            'patterns': ['"type": "quiz"', '"task_type": "quiz"'],
            'task_template': 'Create a quiz about {topic} for grade {grade} with {count} questions',
            'ions': ['quiz-generator-ion']
        },
        # Code analysis
        'code_file': {
            'extensions': ['.py', '.ts', '.js', '.tsx', '.jsx'],
            'task_template': 'Analyze this code file: {filename}',
            'ions': ['duplicate-detector-ion', 'dead-code-eliminator-ion', 'code-grouper-ion']
        },
        # Codebase audit request
        'audit_json': {
            'patterns': ['"type": "audit"', '"task_type": "audit"', '"task_type": "codebase"'],
            'task_template': 'Audit the codebase at {path}',
            'ions': ['duplicate-detector-ion', 'dead-code-eliminator-ion', 'code-grouper-ion', 'refactor-planner-ion']
        },
        # Research request
        'research_json': {
            'patterns': ['"type": "research"', '"task_type": "research"'],
            'task_template': 'Research {topic} and provide educational summary',
            'ions': ['omnisearch', 'quality-assessor-ion']
        },
        # Plain text content
        'text_content': {
            'extensions': ['.txt', '.md'],
            'task_template': 'Process this educational content: {summary}',
            'ions': ['quality-assessor-ion', 'context-builder-ion']
        }
    }

    def analyze(self, filepath: Path) -> Dict[str, Any]:
        """Analyze content and return task details"""
        content = self._read_content(filepath)
        extension = filepath.suffix.lower()

        # Try to parse as JSON first
        if extension == '.json' or content.strip().startswith('{'):
            return self._analyze_json(filepath, content)

        # Check for URLs
        if 'youtube.com' in content or 'youtu.be' in content:
            return self._analyze_youtube(filepath, content)

        # Check for code files
        if extension in ['.py', '.ts', '.js', '.tsx', '.jsx']:
            return self._analyze_code(filepath, content)

        # Default: plain text content
        return self._analyze_text(filepath, content)

    def _read_content(self, filepath: Path) -> str:
        """Read file content safely"""
        try:
            return filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return filepath.read_text(encoding='latin-1')

    def _analyze_json(self, filepath: Path, content: str) -> Dict[str, Any]:
        """Analyze JSON specification file"""
        try:
            spec = json.loads(content)
        except json.JSONDecodeError:
            return self._analyze_text(filepath, content)

        task_type = spec.get('type', spec.get('task_type', 'unknown'))

        if task_type == 'quiz':
            topic = spec.get('topic', 'general knowledge')
            grade = spec.get('grade_level', spec.get('grade', 5))
            count = spec.get('question_count', spec.get('count', 4))
            return {
                'content_type': 'quiz_json',
                'task': f'Create a quiz about {topic} for grade {grade} with {count} questions',
                'ions': ['quiz-generator-ion'],
                'metadata': spec
            }

        if task_type in ['audit', 'codebase', 'codebase_analysis']:
            path = spec.get('path', spec.get('codebase_path', './'))
            return {
                'content_type': 'audit_json',
                'task': f'Audit the codebase at {path}',
                'ions': ['duplicate-detector-ion', 'dead-code-eliminator-ion',
                        'code-grouper-ion', 'refactor-planner-ion'],
                'metadata': spec
            }

        if task_type == 'research':
            topic = spec.get('topic', 'unknown topic')
            return {
                'content_type': 'research_json',
                'task': f'Research {topic} and provide educational summary',
                'ions': ['omnisearch', 'quality-assessor-ion'],
                'metadata': spec
            }

        # Generic JSON - use content as task description
        task = spec.get('task', spec.get('description', f'Process JSON content from {filepath.name}'))
        return {
            'content_type': 'generic_json',
            'task': task,
            'ions': [],  # Let ADA auto-route
            'metadata': spec
        }

    def _analyze_youtube(self, filepath: Path, content: str) -> Dict[str, Any]:
        """Analyze YouTube URL content"""
        # Extract URL from content
        lines = content.strip().split('\n')
        url = None
        for line in lines:
            line = line.strip()
            if 'youtube.com' in line or 'youtu.be' in line:
                url = line
                break

        return {
            'content_type': 'youtube_url',
            'task': f'Extract educational content from YouTube video: {url}',
            'ions': ['content-fetcher-ion', 'quality-assessor-ion'],
            'metadata': {'url': url, 'source_file': str(filepath)}
        }

    def _analyze_code(self, filepath: Path, content: str) -> Dict[str, Any]:
        """Analyze code file"""
        line_count = len(content.split('\n'))
        return {
            'content_type': 'code_file',
            'task': f'Analyze code quality and patterns in {filepath.name} ({line_count} lines)',
            'ions': ['duplicate-detector-ion', 'dead-code-eliminator-ion', 'code-grouper-ion'],
            'metadata': {'filename': str(filepath), 'lines': line_count}
        }

    def _analyze_text(self, filepath: Path, content: str) -> Dict[str, Any]:
        """Analyze plain text content"""
        # Generate summary from first 100 chars
        summary = content[:100].replace('\n', ' ').strip()
        if len(content) > 100:
            summary += '...'

        return {
            'content_type': 'text_content',
            'task': f'Analyze and extract key learnings from: {summary}',
            'ions': ['quality-assessor-ion', 'context-builder-ion'],
            'metadata': {'summary': summary, 'length': len(content)}
        }


class ADADropzone:
    """Main dropzone processor that integrates with ADA Coordinator"""

    def __init__(self, base_path: str = ".", poll_interval: int = 3):
        self.base_path = Path(base_path)
        self.poll_interval = poll_interval
        self.analyzer = ContentAnalyzer()

        # Setup dropzone directories
        self.dropzones = {
            'inbox': self.base_path / 'dropzones' / 'inbox',
            'processing': self.base_path / 'dropzones' / 'processing',
            'completed': self.base_path / 'dropzones' / 'completed',
            'failed': self.base_path / 'dropzones' / 'failed',
            'logs': self.base_path / 'dropzones' / 'logs',
            'results': self.base_path / 'dropzones' / 'results'
        }

        # Ensure all directories exist
        for path in self.dropzones.values():
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Item tracking
        self.active_items: Dict[str, DropzoneItem] = {}
        self.history: List[DropzoneItem] = []

        # ADA Coordinator (lazy loaded)
        self._coordinator = None

    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.dropzones['logs'] / f"dropzone_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ADADropzone')

    @property
    def coordinator(self):
        """Lazy load ADA Coordinator"""
        if self._coordinator is None:
            from ada_coordinator import ADACoordinator
            self._coordinator = ADACoordinator()
        return self._coordinator

    def _generate_id(self, filepath: Path) -> str:
        """Generate unique item ID"""
        content = f"{filepath.name}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def scan_inbox(self) -> List[Path]:
        """Scan inbox for new files"""
        files = []
        for filepath in self.dropzones['inbox'].iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                files.append(filepath)
        return sorted(files, key=lambda p: p.stat().st_mtime)

    def create_item(self, filepath: Path) -> DropzoneItem:
        """Create a dropzone item from a file"""
        analysis = self.analyzer.analyze(filepath)

        item = DropzoneItem(
            id=self._generate_id(filepath),
            filename=filepath.name,
            filepath=filepath,
            content_type=analysis['content_type'],
            timestamp=datetime.now(),
            status=DropzoneStatus.PENDING,
            task_generated=analysis['task'],
            ions_used=analysis.get('ions', [])
        )

        return item

    async def process_item(self, item: DropzoneItem):
        """Process a single dropzone item through ADA"""
        try:
            self.logger.info(f"[{item.id}] Processing: {item.filename}")
            self.logger.info(f"[{item.id}] Content type: {item.content_type}")
            self.logger.info(f"[{item.id}] Generated task: {item.task_generated}")

            # Update status
            item.status = DropzoneStatus.ANALYZING
            item.processing_start = datetime.now()

            # Move to processing directory
            processing_path = self.dropzones['processing'] / f"{item.id}_{item.filename}"
            shutil.copy2(str(item.filepath), str(processing_path))
            item.filepath.unlink()  # Remove from inbox
            item.filepath = processing_path

            # Execute through ADA Coordinator
            item.status = DropzoneStatus.EXECUTING
            self.logger.info(f"[{item.id}] Executing via ADA Coordinator...")

            report = await self.coordinator.execute(item.task_generated, verbose=False, trace=True)

            # Capture results
            item.result = {
                'title': report.title,
                'summary': report.summary,
                'ions_executed': [t.ion_name for t in report.execution_trace] if report.execution_trace else [],
                'success_count': sum(1 for t in report.execution_trace if t.status == 'SUCCESS') if report.execution_trace else 0,
                'total_duration_ms': sum(t.duration_ms for t in report.execution_trace) if report.execution_trace else 0,
                'recommendations': report.recommendations if hasattr(report, 'recommendations') else []
            }

            # Save result to results directory
            result_file = self.dropzones['results'] / f"{item.id}_result.json"
            result_file.write_text(json.dumps(item.to_dict(), indent=2), encoding='utf-8')

            # Move to completed
            completed_path = self.dropzones['completed'] / item.filename
            shutil.move(str(item.filepath), str(completed_path))
            item.filepath = completed_path

            item.status = DropzoneStatus.COMPLETED
            item.processing_end = datetime.now()

            duration = (item.processing_end - item.processing_start).total_seconds()
            self.logger.info(f"[{item.id}] [OK] Completed in {duration:.1f}s")
            self.logger.info(f"[{item.id}] Summary: {report.summary[:100]}...")

        except Exception as e:
            self.logger.error(f"[{item.id}] [FAIL] Error: {str(e)}")

            # Move to failed directory
            failed_path = self.dropzones['failed'] / item.filename
            if item.filepath.exists():
                shutil.move(str(item.filepath), str(failed_path))
                item.filepath = failed_path

            item.status = DropzoneStatus.FAILED
            item.error = str(e)
            item.processing_end = datetime.now()

            # Save error details
            error_file = self.dropzones['failed'] / f"{item.id}_error.txt"
            error_file.write_text(f"Error: {str(e)}\n\nItem: {json.dumps(item.to_dict(), indent=2)}", encoding='utf-8')

        finally:
            self.history.append(item)
            if item.id in self.active_items:
                del self.active_items[item.id]

    async def watch(self):
        """Main watch loop - continuously monitor inbox"""
        self.logger.info("=" * 60)
        self.logger.info("ADA Dropzone Monitor Started")
        self.logger.info(f"Inbox: {self.dropzones['inbox']}")
        self.logger.info(f"Poll interval: {self.poll_interval}s")
        self.logger.info("=" * 60)
        self.logger.info("Drop files into the inbox to trigger ADA orchestration...")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("")

        while True:
            try:
                new_files = self.scan_inbox()

                if new_files:
                    self.logger.info(f"Found {len(new_files)} new file(s)")

                    for filepath in new_files:
                        item = self.create_item(filepath)
                        self.active_items[item.id] = item
                        await self.process_item(item)

                await asyncio.sleep(self.poll_interval)

            except KeyboardInterrupt:
                self.logger.info("")
                self.logger.info("Shutting down dropzone monitor...")
                break
            except Exception as e:
                self.logger.error(f"Error in watch loop: {e}")
                await asyncio.sleep(self.poll_interval)

    async def process_once(self):
        """Process all files in inbox once and exit"""
        self.logger.info("Processing inbox files once...")

        files = self.scan_inbox()
        if not files:
            self.logger.info("No files to process")
            return

        self.logger.info(f"Found {len(files)} file(s)")

        for filepath in files:
            item = self.create_item(filepath)
            self.active_items[item.id] = item
            await self.process_item(item)

        self.logger.info(f"Processed {len(files)} file(s)")

    async def process_file(self, filepath: str):
        """Process a single specific file"""
        path = Path(filepath)
        if not path.exists():
            self.logger.error(f"File not found: {filepath}")
            return

        item = self.create_item(path)
        self.active_items[item.id] = item
        await self.process_item(item)

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        completed = sum(1 for item in self.history if item.status == DropzoneStatus.COMPLETED)
        failed = sum(1 for item in self.history if item.status == DropzoneStatus.FAILED)

        return {
            'total_processed': len(self.history),
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / len(self.history) * 100) if self.history else 0,
            'active': len(self.active_items),
            'inbox_pending': len(self.scan_inbox())
        }


def print_banner():
    """Print startup banner"""
    print()
    print("=" * 60)
    print("  ADA Dropzone - File-Based AI Orchestration")
    print("=" * 60)
    print()


def print_help():
    """Print help message"""
    print_banner()
    print("Usage:")
    print("  python ada_dropzone.py --watch           Continuous monitoring")
    print("  python ada_dropzone.py --once            Process inbox once")
    print("  python ada_dropzone.py --file <path>     Process single file")
    print("  python ada_dropzone.py --status          Show dropzone status")
    print("  python ada_dropzone.py --help            Show this help")
    print()
    print("Dropzone Structure:")
    print("  dropzones/inbox/       Drop content here")
    print("  dropzones/completed/   Successfully processed")
    print("  dropzones/failed/      Processing failed")
    print("  dropzones/results/     JSON result files")
    print()
    print("Supported Content Types:")
    print("  - JSON specs: {\"type\": \"quiz\", \"topic\": \"...\", \"grade\": 6}")
    print("  - YouTube URLs: youtube.com/watch?v=...")
    print("  - Code files: .py, .ts, .js")
    print("  - Text content: .txt, .md")
    print()
    print("Example JSON Specs:")
    print()
    print("  Quiz Generation:")
    print('    {"type": "quiz", "topic": "photosynthesis", "grade": 6, "count": 10}')
    print()
    print("  Codebase Audit:")
    print('    {"type": "audit", "path": "./src"}')
    print()
    print("  Research:")
    print('    {"type": "research", "topic": "quantum computing"}')
    print()


def print_status(dropzone: ADADropzone):
    """Print dropzone status"""
    print_banner()
    stats = dropzone.get_stats()
    print("Dropzone Status:")
    print(f"  Inbox pending:    {stats['inbox_pending']}")
    print(f"  Currently active: {stats['active']}")
    print(f"  Total processed:  {stats['total_processed']}")
    print(f"  Completed:        {stats['completed']}")
    print(f"  Failed:           {stats['failed']}")
    print(f"  Success rate:     {stats['success_rate']:.1f}%")
    print()
    print("Directories:")
    for name, path in dropzone.dropzones.items():
        file_count = len(list(path.glob('*'))) if path.exists() else 0
        print(f"  {name:12} {path} ({file_count} files)")
    print()


def main():
    """Main entry point"""
    args = sys.argv[1:]

    if not args or '--help' in args or '-h' in args:
        print_help()
        return

    dropzone = ADADropzone()

    if '--status' in args or '-s' in args:
        print_status(dropzone)
        return

    if '--watch' in args or '-w' in args:
        print_banner()
        asyncio.run(dropzone.watch())
        return

    if '--once' in args:
        print_banner()
        asyncio.run(dropzone.process_once())
        return

    if '--file' in args or '-f' in args:
        try:
            idx = args.index('--file') if '--file' in args else args.index('-f')
            filepath = args[idx + 1]
            print_banner()
            asyncio.run(dropzone.process_file(filepath))
        except (IndexError, ValueError):
            print("Error: --file requires a path argument")
            print("Usage: python ada_dropzone.py --file <path>")
        return

    # Unknown args - show help
    print(f"Unknown arguments: {args}")
    print_help()


if __name__ == "__main__":
    main()
