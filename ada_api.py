#!/usr/bin/env python3
"""
LearnQwest™ ADA REST API
========================
REST API for the ADA Orchestrator - student uploads, teacher dashboard, status monitoring

Created by: LINK & Claude Code
Date: October 24, 2025
Version: 1.0 - LearnQwest™ Edition
"""

import asyncio
from typing import Optional
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from pathlib import Path
import logging
from datetime import datetime

from ada_orchestrator import ADAOrchestrator, QuestDomain, TaskPriority

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [LearnQwest™ API] - %(levelname)s - %(message)s",
)
logger = logging.getLogger("LearnQwest_API")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global ADA orchestrator instance
ada: Optional[ADAOrchestrator] = None
ada_task: Optional[asyncio.Task] = None


def get_ada() -> ADAOrchestrator:
    """Get or create ADA orchestrator instance"""
    global ada, ada_task
    if ada is None:
        ada = ADAOrchestrator(max_concurrent=5)
        # Start in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ada.start())
        logger.info("[OK] ADA Orchestrator started")
    return ada


# ================================
# HEALTH & STATUS ENDPOINTS
# ================================


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    import sys
    import flask

    return jsonify(
        {
            "status": "healthy",
            "service": "LearnQwest™ ADA API",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "flask_version": flask.__version__,
            "venv": (
                "learnqwest_test_venv"
                if "learnqwest_test_venv" in sys.executable
                else "system"
            ),
        }
    )


@app.route("/api/status", methods=["GET"])
def system_status():
    """Get complete system status"""
    orchestrator = get_ada()
    return jsonify(orchestrator.get_system_status())


# ================================
# STUDENT WORK UPLOAD
# ================================


@app.route("/api/student/upload", methods=["POST"])
def upload_student_work():
    """
    Upload student work for analysis

    Expected form data:
    - file: The student work file (PDF, image, etc.)
    - studentId: Student identifier
    - subject: Subject area (math, reading, etc.)
    - gradeLevel: Student's grade level
    - assignmentType: Type of assignment
    """
    try:
        # Check if file was included
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Get metadata
        student_id = request.form.get("studentId", "anonymous")
        subject = request.form.get("subject", "general")
        grade_level = int(request.form.get("gradeLevel", 5))
        assignment_type = request.form.get("assignmentType", "homework")

        # Save file
        upload_dir = Path("uploads") / student_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        filepath = upload_dir / safe_filename

        file.save(str(filepath))
        logger.info(f"[UPLOAD] File uploaded: {filepath} (Student: {student_id})")

        # Submit to ADA orchestrator
        orchestrator = get_ada()

        # Map subject to domain
        domain_map = {
            "math": QuestDomain.MATH,
            "reading": QuestDomain.READING,
            "science": QuestDomain.SCIENCE,
            "social_studies": QuestDomain.SOCIAL_STUDIES,
            "creative": QuestDomain.CREATIVE,
        }
        domain = domain_map.get(subject.lower(), QuestDomain.GENERAL)

        # Create async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task_id = loop.run_until_complete(
            orchestrator.submit_task(
                description=f"Analyze {grade_level}th grade {subject} {assignment_type}",
                domain=domain,
                priority=TaskPriority.NORMAL,
                student_id=student_id,
                grade_level=grade_level,
                file_path=str(filepath),
                metadata={
                    "filename": file.filename,
                    "upload_time": timestamp,
                    "assignment_type": assignment_type,
                    "file_size": filepath.stat().st_size,
                },
            )
        )

        return jsonify(
            {
                "success": True,
                "task_id": task_id,
                "message": f"Work submitted for analysis",
                "student_id": student_id,
                "estimated_time": "< 10 seconds",
                "status_url": f"/api/task/{task_id}",
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Upload error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500


# ================================
# TASK MANAGEMENT
# ================================


@app.route("/api/task/submit", methods=["POST"])
def submit_task():
    """
    Submit a task without file upload (for testing/API integration)

    Expected JSON:
    {
        "description": "Task description",
        "domain": "math|reading|science|etc",
        "priority": "low|normal|high|urgent",
        "studentId": "student123",
        "gradeLevel": 5
    }
    """
    try:
        data = request.get_json()

        if not data or "description" not in data:
            return jsonify({"error": "Task description required"}), 400

        # Parse request
        description = data["description"]
        domain_str = data.get("domain", "general")
        priority_str = data.get("priority", "normal")
        student_id = data.get("studentId")
        grade_level = data.get("gradeLevel", 5)

        # Map strings to enums
        domain_map = {
            "math": QuestDomain.MATH,
            "reading": QuestDomain.READING,
            "science": QuestDomain.SCIENCE,
            "social_studies": QuestDomain.SOCIAL_STUDIES,
            "creative": QuestDomain.CREATIVE,
            "general": QuestDomain.GENERAL,
        }
        domain = domain_map.get(domain_str.lower(), QuestDomain.GENERAL)

        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT,
        }
        priority = priority_map.get(priority_str.lower(), TaskPriority.NORMAL)

        # Submit to orchestrator
        orchestrator = get_ada()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task_id = loop.run_until_complete(
            orchestrator.submit_task(
                description=description,
                domain=domain,
                priority=priority,
                student_id=student_id,
                grade_level=grade_level,
            )
        )

        return jsonify(
            {"success": True, "task_id": task_id, "status_url": f"/api/task/{task_id}"}
        )

    except Exception as e:
        logger.error(f"[ERROR] Task submission error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """Get status of a specific task"""
    orchestrator = get_ada()
    status = orchestrator.get_task_status(task_id)

    if status:
        return jsonify(status)
    else:
        return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """List all tasks with optional filters"""
    orchestrator = get_ada()

    # Get query parameters
    status_filter = request.args.get("status")  # queued, executing, completed, failed
    student_id = request.args.get("studentId")
    limit = int(request.args.get("limit", 50))

    # Get all tasks
    all_tasks = []

    # Active tasks
    for task in orchestrator.task_queue.active_tasks.values():
        all_tasks.append(orchestrator._task_to_dict(task))

    # Queued tasks
    for task in orchestrator.task_queue.queue:
        all_tasks.append(orchestrator._task_to_dict(task))

    # Completed tasks (most recent first)
    completed = list(orchestrator.task_queue.completed_tasks.values())
    completed.sort(key=lambda t: t.updated_at, reverse=True)
    for task in completed[:limit]:
        all_tasks.append(orchestrator._task_to_dict(task))

    # Apply filters
    if status_filter:
        all_tasks = [t for t in all_tasks if t["status"] == status_filter]

    if student_id:
        all_tasks = [t for t in all_tasks if t.get("student_id") == student_id]

    # Apply limit
    all_tasks = all_tasks[:limit]

    return jsonify({"total": len(all_tasks), "tasks": all_tasks})


# ================================
# QUEST/AGENT INFORMATION
# ================================


@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Get information about available learning agents"""
    orchestrator = get_ada()

    # Try to get from Quest Manager if available
    try:
        from quest_manager import QuestManager

        qm = QuestManager()

        return jsonify(
            {
                "total_agents": len(qm.agents),
                "by_category": qm.get_category_summary(),
                "roster": qm.get_agent_roster(),
            }
        )
    except:
        # Fallback to basic info
        return jsonify(
            {
                "total_agents": 60,
                "status": "LearnQwest™ learning agents ready",
                "note": "Full roster requires Quest Manager module",
            }
        )


@app.route("/api/agents/<agent_name>", methods=["GET"])
def get_agent_info(agent_name):
    """Get detailed info about a specific agent"""
    try:
        from quest_manager import QuestManager

        qm = QuestManager()

        info = qm.get_agent_info(agent_name)
        if info:
            return jsonify(info)
        else:
            return jsonify({"error": "Agent not found"}), 404
    except:
        return jsonify({"error": "Quest Manager not available"}), 503


# ================================
# METRICS & ANALYTICS
# ================================


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Get system metrics and analytics"""
    orchestrator = get_ada()
    return jsonify(orchestrator.monitor.get_metrics())


@app.route("/api/metrics/student/<student_id>", methods=["GET"])
def get_student_metrics(student_id):
    """Get metrics for a specific student"""
    orchestrator = get_ada()

    # Find all tasks for this student
    student_tasks = []
    for task in orchestrator.task_queue.completed_tasks.values():
        if task.student_id == student_id:
            student_tasks.append(orchestrator._task_to_dict(task))

    # Calculate metrics
    total_tasks = len(student_tasks)
    completed = len([t for t in student_tasks if t["status"] == "completed"])
    failed = len([t for t in student_tasks if t["status"] == "failed"])

    return jsonify(
        {
            "student_id": student_id,
            "total_assignments": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": f"{(completed / max(total_tasks, 1)) * 100:.1f}%",
            "recent_tasks": student_tasks[:10],  # Last 10 tasks
        }
    )


# ================================
# TEACHER DASHBOARD
# ================================


@app.route("/api/teacher/overview", methods=["GET"])
def teacher_overview():
    """Get overview for teacher dashboard"""
    orchestrator = get_ada()

    # Collect stats
    queue_status = orchestrator.task_queue.get_status()
    metrics = orchestrator.monitor.get_metrics()

    # Get unique students (from recent tasks)
    students = set()
    for task in orchestrator.task_queue.completed_tasks.values():
        if task.student_id:
            students.add(task.student_id)

    return jsonify(
        {
            "summary": {
                "total_students": len(students),
                "assignments_today": queue_status["completed"],
                "currently_processing": queue_status["active"],
                "queued_assignments": queue_status["queued"],
            },
            "performance": {
                "success_rate": metrics["success_rate"],
                "average_time": f"{metrics['average_time']:.2f}s",
                "total_processed": metrics["total_tasks"],
            },
            "system": {
                "status": "operational",
                "agents_available": 60,
                "capacity": queue_status["capacity"],
            },
        }
    )


# ================================
# STATIC FILES (Frontend)
# ================================


@app.route("/command", methods=["GET"])
def command_center():
    """Serve the interactive command center"""
    from pathlib import Path

    file_path = Path(__file__).parent / "web" / "ada_command_center.html"
    return send_file(file_path)


@app.route("/", methods=["GET"])
def index():
    """Serve the main dashboard"""
    return """
    <html>
    <head>
        <title>LearnQwest™ - AI-Powered Learning</title>
        <style>
            body {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #0a0e27;
                color: #e0e0e0;
            }
            .header {
                background: linear-gradient(135deg, #ff006e 0%, #8338ec 50%, #3a86ff 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(131, 56, 236, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 42px;
                text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
                letter-spacing: 2px;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.95;
                font-size: 16px;
            }
            .card {
                background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(131, 56, 236, 0.3);
            }
            .card h2 {
                margin-top: 0;
                color: #8338ec;
                text-shadow: 0 0 10px rgba(131, 56, 236, 0.5);
                font-size: 24px;
            }
            .card h3 {
                color: #3a86ff;
                margin-top: 20px;
                font-size: 18px;
            }
            .endpoint {
                background: rgba(58, 134, 255, 0.1);
                padding: 12px;
                margin: 10px 0;
                border-radius: 8px;
                font-family: 'Consolas', monospace;
                border-left: 3px solid #3a86ff;
                transition: all 0.3s ease;
            }
            .endpoint:hover {
                background: rgba(58, 134, 255, 0.2);
                transform: translateX(5px);
            }
            .method {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 1px;
            }
            .get { 
                background: linear-gradient(135deg, #06ffa5 0%, #00d4aa 100%);
                color: #0a0e27;
                box-shadow: 0 0 10px rgba(6, 255, 165, 0.5);
            }
            .post { 
                background: linear-gradient(135deg, #ff006e 0%, #ff4d8f 100%);
                color: white;
                box-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
            }
            pre {
                background: #000;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #8338ec;
                color: #06ffa5;
                overflow-x: auto;
            }
            code {
                color: #ff006e;
                background: rgba(255, 0, 110, 0.1);
                padding: 2px 6px;
                border-radius: 3px;
            }
            ul {
                line-height: 1.8;
            }
            li {
                margin: 8px 0;
            }
            strong {
                color: #3a86ff;
            }
            .test-btn {
                background: linear-gradient(135deg, #8338ec 0%, #3a86ff 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                margin: 5px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(131, 56, 236, 0.4);
            }
            .test-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(131, 56, 236, 0.6);
            }
            .test-btn:active {
                transform: translateY(0);
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>[TARGET] LearnQwest™</h1>
            <p>AI-Powered Personalized Learning for Texas Schools</p>
        </div>

        <div class="card">
            <h2>[OK] System Status</h2>
            <p>API is running and ready to process student work!</p>
            <p><strong>Base URL:</strong> http://localhost:5001</p>
            <div style="margin-top: 15px; padding: 15px; background: rgba(6, 255, 165, 0.1); border-left: 3px solid #06ffa5; border-radius: 5px;">
                <p style="margin: 5px 0;"><strong>🐍 Python:</strong> <span id="python-version">Loading...</span></p>
                <p style="margin: 5px 0;"><strong>🌐 Flask:</strong> <span id="flask-version">Loading...</span></p>
                <p style="margin: 5px 0;"><strong>📦 Virtual Env:</strong> <span id="venv-info">Loading...</span></p>
                <p style="margin: 5px 0;"><strong>📁 Working Dir:</strong> <code style="font-size: 11px;">C:\\Users\\talon\\OneDrive\\Projects\\LearnQwest</code></p>
            </div>
        </div>

        <div class="card">
            <h2>📚 API Endpoints</h2>

            <h3>Student Endpoints</h3>
            <div class="endpoint">
                <span class="method post">POST</span> /api/student/upload - Upload student work
            </div>

            <h3>Task Management</h3>
            <div class="endpoint">
                <span class="method post">POST</span> /api/task/submit - Submit a task
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/task/{task_id} - Get task status
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/tasks - List all tasks
            </div>

            <h3>System Information</h3>
            <div class="endpoint">
                <span class="method get">GET</span> /api/health - Health check
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/status - System status
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/metrics - Performance metrics
            </div>

            <h3>Teacher Dashboard</h3>
            <div class="endpoint">
                <span class="method get">GET</span> /api/teacher/overview - Dashboard overview
            </div>

            <h3>Agent Information</h3>
            <div class="endpoint">
                <span class="method get">GET</span> /api/agents - List all agents
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/agents/{name} - Agent details
            </div>
        </div>

        <div class="card">
            <h2>[TEST] Interactive Test Panel</h2>
            <p>Click to test the API:</p>
            <button onclick="testHealth()" class="test-btn">Test Health Check</button>
            <button onclick="testStatus()" class="test-btn">Get System Status</button>
            <button onclick="testMetrics()" class="test-btn">View Metrics</button>
            <div id="result" style="margin-top: 20px;"></div>
        </div>
        
        <script>
            // Load system info on page load
            window.addEventListener('DOMContentLoaded', async () => {
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    document.getElementById('python-version').textContent = data.python_version || 'Unknown';
                    document.getElementById('flask-version').textContent = data.flask_version || 'Unknown';
                    document.getElementById('venv-info').textContent = data.venv || 'Unknown';
                } catch (error) {
                    console.error('Failed to load system info:', error);
                }
            });
            
            async function testHealth() {
                const result = document.getElementById('result');
                result.innerHTML = '<p style="color: #3a86ff;">⏳ Testing...</p>';
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    result.innerHTML = '<pre style="background: #000; padding: 15px; border-radius: 8px; color: #06ffa5;">' + 
                                      JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    result.innerHTML = '<p style="color: #ff006e;">[ERROR] Error: ' + error.message + '</p>';
                }
            }
            
            async function testStatus() {
                const result = document.getElementById('result');
                result.innerHTML = '<p style="color: #3a86ff;">⏳ Loading status...</p>';
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    result.innerHTML = '<pre style="background: #000; padding: 15px; border-radius: 8px; color: #06ffa5;">' + 
                                      JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    result.innerHTML = '<p style="color: #ff006e;">[ERROR] Error: ' + error.message + '</p>';
                }
            }
            
            async function testMetrics() {
                const result = document.getElementById('result');
                result.innerHTML = '<p style="color: #3a86ff;">⏳ Loading metrics...</p>';
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    result.innerHTML = '<pre style="background: #000; padding: 15px; border-radius: 8px; color: #06ffa5;">' + 
                                      JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    result.innerHTML = '<p style="color: #ff006e;">[ERROR] Error: ' + error.message + '</p>';
                }
            }
        </script>

        <div class="card">
            <h2>📖 Next Steps</h2>
            <ul>
                <li>Upload student work via <code>/api/student/upload</code></li>
                <li>Check task status with <code>/api/task/{task_id}</code></li>
                <li>View teacher dashboard at <code>/api/teacher/overview</code></li>
                <li>Monitor system metrics at <code>/api/metrics</code></li>
            </ul>
        </div>
    </body>
    </html>
    """


def main():
    """Start the API server"""
    print("\n" + "=" * 70)
    print("[TARGET] LearnQwest™ ADA API Server")
    print("=" * 70)
    print("[START] Starting server...")
    print("[INFO] Server URL: http://localhost:5001")
    print("[INFO] API Docs: http://localhost:5001")
    print("\n" + "=" * 70 + "\n")

    # Initialize ADA
    get_ada()

    # Start Flask server
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,  # Set to False for production
        threaded=True,
    )


if __name__ == "__main__":
    main()
