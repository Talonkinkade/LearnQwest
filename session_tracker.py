#!/usr/bin/env python3
"""
Session Tracker - Never Lose Context Again
===========================================
Tracks what you're working on so you can pick up instantly.

Run at end of session: python session_tracker.py save
Run at start of session: python session_tracker.py load
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class SessionTracker:
    """Track session state for continuity"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.sessions_dir = self.project_root / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        self.current_session_file = self.sessions_dir / "current_session.json"
        self.history_file = self.sessions_dir / "session_history.jsonl"

    def get_git_status(self) -> dict:
        """Get current git state"""
        try:
            # Current branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            ).stdout.strip()

            # Last commit
            last_commit = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                capture_output=True, text=True, cwd=self.project_root
            ).stdout.strip()

            # Modified files
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=self.project_root
            ).stdout.strip()

            modified = [line[3:] for line in status.split('\n') if line.startswith(' M')]
            untracked = [line[3:] for line in status.split('\n') if line.startswith('??')]

            # Recent commits today
            today = datetime.now().strftime('%Y-%m-%d')
            recent = subprocess.run(
                ["git", "log", "--oneline", "--since", today],
                capture_output=True, text=True, cwd=self.project_root
            ).stdout.strip().split('\n')

            return {
                "branch": branch,
                "last_commit": last_commit,
                "modified_files": modified[:10],
                "untracked_files": untracked[:10],
                "commits_today": [c for c in recent if c][:5]
            }
        except Exception as e:
            return {"error": str(e)}

    def get_recent_logs(self) -> list:
        """Get recent ADA activity from logs"""
        logs_dir = self.project_root / "ada_logs"
        if not logs_dir.exists():
            return []

        log_files = sorted(logs_dir.glob("ada_*.jsonl"), reverse=True)
        if not log_files:
            return []

        recent_activity = []
        with open(log_files[0]) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('event_type') == 'agent_execution':
                        recent_activity.append({
                            "time": entry.get('timestamp', ''),
                            "agent": entry.get('agent_name', ''),
                            "success": entry.get('success', False),
                            "duration_ms": entry.get('execution_time_ms', 0)
                        })
                except:
                    continue

        return recent_activity[-10:]

    def get_feedback_summary(self) -> dict:
        """Get feedback loop summary"""
        feedback_file = self.project_root / "ada_feedback.jsonl"
        if not feedback_file.exists():
            return {"total_entries": 0}

        entries = []
        with open(feedback_file) as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    continue

        if not entries:
            return {"total_entries": 0}

        success_count = sum(1 for e in entries if e.get('success', False))

        return {
            "total_entries": len(entries),
            "success_rate": (success_count / len(entries) * 100) if entries else 0,
            "recent_agents": list(set(
                agent for e in entries[-10:]
                for agent in e.get('agents_used', [])
            ))
        }

    def save_session(self, notes: str = None):
        """Save current session state"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "git": self.get_git_status(),
            "recent_activity": self.get_recent_logs(),
            "feedback_summary": self.get_feedback_summary(),
            "notes": notes or ""
        }

        # Save current session
        with open(self.current_session_file, 'w') as f:
            json.dump(session, f, indent=2)

        # Append to history
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(session) + '\n')

        return session

    def load_session(self) -> dict:
        """Load last session state"""
        if not self.current_session_file.exists():
            return None

        with open(self.current_session_file) as f:
            return json.load(f)

    def print_context(self):
        """Print context for starting a new session"""
        session = self.load_session()

        print()
        print("=" * 70)
        print("  ADA SESSION CONTEXT - Pick Up Where You Left Off")
        print("=" * 70)

        if not session:
            print("\n  No previous session found. Starting fresh!")
            print()
            return

        print(f"\n  Last Session: {session.get('date', 'Unknown')} at {session.get('time', 'Unknown')}")
        print()

        # Git status
        git = session.get('git', {})
        print("  GIT STATUS")
        print("  " + "-" * 66)
        print(f"    Branch: {git.get('branch', 'unknown')}")
        print(f"    Last Commit: {git.get('last_commit', 'unknown')}")

        commits_today = git.get('commits_today', [])
        if commits_today:
            print(f"\n    Today's Commits ({len(commits_today)}):")
            for c in commits_today[:3]:
                print(f"      - {c}")

        modified = git.get('modified_files', [])
        if modified:
            print(f"\n    Modified Files ({len(modified)}):")
            for f in modified[:5]:
                print(f"      - {f}")

        # Recent activity
        activity = session.get('recent_activity', [])
        if activity:
            print("\n  RECENT ADA ACTIVITY")
            print("  " + "-" * 66)
            for a in activity[-5:]:
                status = "[OK]" if a.get('success') else "[XX]"
                print(f"    {status} {a.get('agent', 'unknown'):25} {a.get('duration_ms', 0):6.0f}ms")

        # Feedback summary
        feedback = session.get('feedback_summary', {})
        if feedback.get('total_entries', 0) > 0:
            print("\n  LEARNING STATUS (Iron Sharpens Iron)")
            print("  " + "-" * 66)
            print(f"    Total Feedback Entries: {feedback.get('total_entries', 0)}")
            print(f"    Success Rate: {feedback.get('success_rate', 0):.1f}%")
            agents = feedback.get('recent_agents', [])
            if agents:
                print(f"    Recent Agents: {', '.join(agents[:5])}")

        # Notes
        notes = session.get('notes', '')
        if notes:
            print("\n  NOTES FROM LAST SESSION")
            print("  " + "-" * 66)
            print(f"    {notes}")

        print()
        print("=" * 70)
        print("  Ready to continue. What would you like to work on?")
        print("=" * 70)
        print()


def main():
    import sys

    tracker = SessionTracker()

    if len(sys.argv) < 2:
        print("Usage: python session_tracker.py [save|load]")
        print("  save - Save current session state")
        print("  load - Load and display last session context")
        return

    command = sys.argv[1].lower()

    if command == "save":
        notes = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        session = tracker.save_session(notes)
        print(f"Session saved at {session['timestamp']}")
        if notes:
            print(f"Notes: {notes}")

    elif command == "load":
        tracker.print_context()

    else:
        print(f"Unknown command: {command}")
        print("Use 'save' or 'load'")


if __name__ == "__main__":
    main()
