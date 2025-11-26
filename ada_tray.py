#!/usr/bin/env python3
"""
ADA System Tray Interface
========================
System tray icon with quick commands and status monitoring.

Usage:
    python ada_tray.py

Features:
    - Color-coded status (green/blue/red)
    - Right-click menu with quick commands
    - Windows toast notifications
    - Service control
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import threading
import time

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Skip win32 - causes import hangs in some environments
HAS_WIN32 = False


class ADASystemTray:
    """System tray interface for ADA"""

    def __init__(self):
        self.icon = None
        self.status_file = "ada_status.json"
        self.service_running = False
        self.last_status = {}

        # Quick command templates
        self.quick_commands = {
            "Audit Codebase": "Audit the codebase and find issues",
            "Create Quiz": "Create a quiz about Python basics with 5 questions",
            "Find Duplicates": "Find duplicate code in the project",
            "Analyze Code": "Analyze the codebase structure and organization",
        }

    def create_icon_image(self, color="green"):
        """Create colored icon image"""
        # Create a simple colored circle
        size = 64
        image = Image.new("RGB", (size, size), color="white")
        draw = ImageDraw.Draw(image)

        # Color mapping
        colors = {
            "green": "#00FF00",  # Running
            "blue": "#0080FF",  # Processing
            "red": "#FF0000",  # Error
            "gray": "#808080",  # Stopped
        }

        fill_color = colors.get(color, colors["gray"])

        # Draw circle
        margin = 8
        draw.ellipse([margin, margin, size - margin, size - margin], fill=fill_color)

        return image

    def get_status(self):
        """Read current ADA status"""
        try:
            if Path(self.status_file).exists():
                with open(self.status_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass

        return {"service_status": "unknown", "tasks_completed": 0, "tasks_failed": 0}

    def update_icon_status(self):
        """Update icon based on status"""
        status = self.get_status()
        service_status = status.get("service_status", "unknown")

        # Determine color
        if service_status == "running":
            color = "green"
        elif service_status == "processing":
            color = "blue"
        elif service_status == "error":
            color = "red"
        else:
            color = "gray"

        # Update icon
        if self.icon:
            self.icon.icon = self.create_icon_image(color)
            self.icon.title = f"ADA - {service_status.title()}\nTasks: {status.get('tasks_completed', 0)}"

    def send_notification(self, title, message):
        """Send notification (console output)"""
        print(f"[NOTIFY] {title}: {message}")

    def send_command(self, command):
        """Send command to ADA service"""
        try:
            inbox_path = Path("commands/inbox.txt")

            # Write command
            with open(inbox_path, "w", encoding="utf-8") as f:
                f.write(command)

            self.send_notification("ADA Command", f"Sent: {command[:50]}...")
            print(f"[OK] Command sent: {command}")

        except Exception as e:
            self.send_notification("ADA Error", f"Failed to send command: {e}")
            print(f"[FAIL] Command error: {e}")

    def quick_command_audit(self, icon, item):
        """Quick command: Audit Codebase"""
        self.send_command(self.quick_commands["Audit Codebase"])

    def quick_command_quiz(self, icon, item):
        """Quick command: Create Quiz"""
        self.send_command(self.quick_commands["Create Quiz"])

    def quick_command_duplicates(self, icon, item):
        """Quick command: Find Duplicates"""
        self.send_command(self.quick_commands["Find Duplicates"])

    def quick_command_analyze(self, icon, item):
        """Quick command: Analyze Code"""
        self.send_command(self.quick_commands["Analyze Code"])

    def open_results_folder(self, icon, item):
        """Open results folder"""
        try:
            results_path = Path("commands/results").absolute()
            subprocess.Popen(f'explorer "{results_path}"')
        except Exception as e:
            print(f"[FAIL] Could not open results: {e}")

    def open_logs_folder(self, icon, item):
        """Open logs folder"""
        try:
            logs_path = Path("ada_logs").absolute()
            if not logs_path.exists():
                logs_path = Path(".").absolute()
            subprocess.Popen(f'explorer "{logs_path}"')
        except Exception as e:
            print(f"[FAIL] Could not open logs: {e}")

    def restart_service(self, icon, item):
        """Restart ADA service"""
        try:
            # Stop existing service
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq ADA*"],
                capture_output=True,
            )
            time.sleep(1)

            # Start service
            subprocess.Popen(
                [sys.executable, "ada_service.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

            self.send_notification("ADA Service", "Service restarted")

        except Exception as e:
            self.send_notification("ADA Error", f"Restart failed: {e}")

    def show_status(self, icon, item):
        """Show current status"""
        status = self.get_status()

        message = f"""ADA Status:
Service: {status.get('service_status', 'unknown')}
Tasks Completed: {status.get('tasks_completed', 0)}
Tasks Failed: {status.get('tasks_failed', 0)}
Last Check: {status.get('last_check', 'N/A')}
"""

        print(message)
        self.send_notification("ADA Status", message)

    def quit_tray(self, icon, item):
        """Quit system tray"""
        icon.stop()

    def create_menu(self):
        """Create system tray menu"""
        return Menu(
            MenuItem(
                "Quick Commands",
                Menu(
                    MenuItem("Audit Codebase", self.quick_command_audit),
                    MenuItem("Create Quiz", self.quick_command_quiz),
                    MenuItem("Find Duplicates", self.quick_command_duplicates),
                    MenuItem("Analyze Code", self.quick_command_analyze),
                ),
            ),
            Menu.SEPARATOR,
            MenuItem("Open Results Folder", self.open_results_folder),
            MenuItem("Open Logs Folder", self.open_logs_folder),
            Menu.SEPARATOR,
            MenuItem("Show Status", self.show_status),
            MenuItem("Restart Service", self.restart_service),
            Menu.SEPARATOR,
            MenuItem("Quit", self.quit_tray),
        )

    def status_monitor_loop(self):
        """Background thread to monitor status"""
        while True:
            try:
                self.update_icon_status()

                # Check for new results
                status = self.get_status()
                if status.get("tasks_completed", 0) > self.last_status.get(
                    "tasks_completed", 0
                ):
                    self.send_notification(
                        "ADA Task Complete",
                        f"Task completed! Total: {status['tasks_completed']}",
                    )

                self.last_status = status

            except Exception as e:
                print(f"[WARN] Status monitor error: {e}")

            time.sleep(5)  # Check every 5 seconds

    def run(self):
        """Run system tray application"""
        print()
        print("=" * 60)
        print("  ADA System Tray")
        print("  Never Do Manual Work Again™")
        print("=" * 60)
        print()
        print("[OK] System tray started")
        print("[OK] Right-click icon for menu")
        print()

        # Start status monitor thread
        monitor_thread = threading.Thread(target=self.status_monitor_loop, daemon=True)
        monitor_thread.start()

        # Create and run icon
        self.icon = Icon(
            "ADA", self.create_icon_image("green"), "ADA Assistant", self.create_menu()
        )

        self.icon.run()


def main():
    """Main entry point"""
    try:
        tray = ADASystemTray()
        tray.run()
    except KeyboardInterrupt:
        print("\n[OK] System tray stopped")
    except Exception as e:
        print(f"\n[FAIL] System tray error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
