#!/usr/bin/env python3
"""
ADA Background Service - Persistent Assistant
============================================
Runs continuously as Windows service, monitoring for commands and executing tasks.

Usage:
    python ada_service.py                    # Run in foreground (testing)
    python install_ada_service.bat           # Install as Windows service

Commands:
    Write to: commands/inbox.txt
    Results in: commands/results/
    Status in: ada_status.json
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import sys

# Import existing ADA components
from ada_coordinator import ADACoordinator
from ada_dropzone import ADADropzone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [ADA Service] - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ada_service.log"), logging.StreamHandler()],
)
logger = logging.getLogger("ADAService")


class ADAService:
    """
    Persistent ADA Assistant Service
    Monitors command files and dropzones, executes tasks automatically
    """

    def __init__(self, config_path: str = "ada_service_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
        self.coordinator: Optional[ADACoordinator] = None
        self.dropzone: Optional[ADADropzone] = None

        # Setup directories
        self._setup_directories()

        # Initialize status
        self.status = {
            "service_status": "initializing",
            "last_check": None,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "uptime_start": datetime.now().isoformat(),
        }

        logger.info("[OK] ADA Service initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load service configuration"""
        default_config = {
            "check_interval": 5,  # seconds
            "command_inbox": "commands/inbox.txt",
            "command_results": "commands/results/",
            "dropzone_path": "dropzones/inbox/",
            "status_file": "ada_status.json",
            "enable_dropzone": True,
            "enable_commands": True,
            "max_retries": 3,
        }

        if Path(self.config_path).exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    default_config.update(config)
                    logger.info(f"[OK] Config loaded from {self.config_path}")
            except Exception as e:
                logger.warning(f"[WARN] Could not load config: {e}, using defaults")

        return default_config

    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            "commands",
            "commands/results",
            "dropzones/inbox",
            "dropzones/processing",
            "dropzones/completed",
            "dropzones/failed",
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        logger.info("[OK] Directories created")

    def _save_status(self):
        """Save current status to file"""
        try:
            with open(self.config["status_file"], "w") as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            logger.error(f"[FAIL] Could not save status: {e}")

    async def _initialize_components(self):
        """Initialize ADA components"""
        try:
            # Initialize coordinator
            self.coordinator = ADACoordinator()
            logger.info("[OK] ADA Coordinator initialized")

            # Initialize dropzone if enabled
            if self.config["enable_dropzone"]:
                self.dropzone = ADADropzone()
                logger.info("[OK] ADA Dropzone initialized")

            self.status["service_status"] = "running"
            self._save_status()

        except Exception as e:
            logger.error(f"[FAIL] Component initialization failed: {e}")
            self.status["service_status"] = "error"
            self._save_status()
            raise

    async def _check_command_inbox(self):
        """Check for new commands in inbox"""
        inbox_path = Path(self.config["command_inbox"])

        if not inbox_path.exists():
            return

        try:
            # Read command
            with open(inbox_path, "r", encoding="utf-8") as f:
                command = f.read().strip()

            if not command:
                return

            logger.info(f"[COMMAND] Received: {command[:100]}...")

            # Clear inbox immediately
            inbox_path.unlink()

            # Execute command
            await self._execute_command(command)

        except Exception as e:
            logger.error(f"[FAIL] Command check error: {e}")

    async def _execute_command(self, command: str):
        """Execute a command via ADA Coordinator"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = Path(self.config["command_results"]) / f"task_{timestamp}.json"

        try:
            logger.info(f"[EXEC] Executing: {command}")

            # Execute via coordinator
            report = await self.coordinator.execute(command, verbose=False, trace=True)

            # Save result
            result = {
                "timestamp": timestamp,
                "command": command,
                "status": "success",
                "report": {
                    "summary": getattr(report, "summary", str(report)),
                    "recommendations": getattr(report, "recommendations", []),
                    "sections": [
                        {
                            "title": getattr(s, "title", "Section"),
                            "content": str(getattr(s, "content", s))[
                                :500
                            ],  # Truncate for file size
                            "priority": getattr(s, "priority", "normal"),
                        }
                        for s in getattr(report, "sections", [])
                    ],
                    "execution_trace": [
                        {
                            "wave": getattr(t, "wave", getattr(t, "wave_number", 0)),
                            "ion": getattr(t, "ion_name", "unknown"),
                            "status": getattr(t, "status", "unknown"),
                            "duration_ms": getattr(t, "duration_ms", 0),
                        }
                        for t in getattr(report, "execution_trace", [])
                    ],
                },
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            self.status["tasks_completed"] += 1
            logger.info(f"[OK] Task completed: {result_file}")

        except Exception as e:
            logger.error(f"[FAIL] Task execution failed: {e}")

            # Save error result
            result = {
                "timestamp": timestamp,
                "command": command,
                "status": "failed",
                "error": str(e),
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            self.status["tasks_failed"] += 1

        finally:
            self._save_status()

    async def _check_dropzone(self):
        """Check dropzone for new files"""
        if not self.config["enable_dropzone"] or not self.dropzone:
            return

        try:
            # Process dropzone (uses existing ADADropzone logic)
            inbox_path = Path(self.config["dropzone_path"])

            if not inbox_path.exists():
                return

            files = list(inbox_path.glob("*"))

            if not files:
                return

            logger.info(f"[DROPZONE] Found {len(files)} file(s)")

            # Process each file
            for file_path in files:
                if file_path.is_file():
                    try:
                        # Use dropzone's process_file method
                        await self.dropzone.process_file(file_path)
                        self.status["tasks_completed"] += 1
                    except Exception as e:
                        logger.error(f"[FAIL] Dropzone file error: {e}")
                        self.status["tasks_failed"] += 1

            self._save_status()

        except Exception as e:
            logger.error(f"[FAIL] Dropzone check error: {e}")

    async def _service_loop(self):
        """Main service loop"""
        logger.info("[OK] Service loop started")

        while self.running:
            try:
                self.status["last_check"] = datetime.now().isoformat()

                # Check command inbox
                if self.config["enable_commands"]:
                    await self._check_command_inbox()

                # Check dropzone
                if self.config["enable_dropzone"]:
                    await self._check_dropzone()

                # Update status
                self._save_status()

                # Wait before next check
                await asyncio.sleep(self.config["check_interval"])

            except Exception as e:
                logger.error(f"[FAIL] Service loop error: {e}")
                await asyncio.sleep(self.config["check_interval"])

    async def start(self):
        """Start the service"""
        logger.info("[FIRE] Starting ADA Service...")

        try:
            # Initialize components
            await self._initialize_components()

            # Start service loop
            self.running = True
            await self._service_loop()

        except KeyboardInterrupt:
            logger.info("[OK] Service stopped by user")
            await self.stop()
        except Exception as e:
            logger.error(f"[FAIL] Service error: {e}")
            self.status["service_status"] = "error"
            self._save_status()
            raise

    async def stop(self):
        """Stop the service"""
        logger.info("[OK] Stopping ADA Service...")
        self.running = False
        self.status["service_status"] = "stopped"
        self._save_status()


def main():
    """Main entry point"""
    print()
    print("=" * 60)
    print("  ADA Background Service")
    print("  Never Do Manual Work Again™")
    print("=" * 60)
    print()
    print("Starting service...")
    print("Press Ctrl+C to stop")
    print()

    service = ADAService()

    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        print("\n[OK] Service stopped")
    except Exception as e:
        print(f"\n[FAIL] Service error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
