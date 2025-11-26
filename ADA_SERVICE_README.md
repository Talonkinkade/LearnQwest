# ADA Background Service - Quick Start

**Never Do Manual Work Again™**

---

## 🚀 Installation

```bash
# Run installation script
install_ada_service.bat
```

This will:
- Install required packages (pystray, pillow, pywin32)
- Create necessary directories
- Test the service

---

## 🎯 Usage

### **Option 1: System Tray (Recommended)**

```bash
# Start system tray interface
start_ada_tray.bat
```

**Features:**
- Right-click icon for menu
- Quick commands (Audit, Quiz, Duplicates, Analyze)
- Open results/logs folders
- Service control
- Status monitoring

### **Option 2: Background Service**

```bash
# Start service in foreground
start_ada_service.bat
```

**Features:**
- Monitors `commands/inbox.txt` every 5 seconds
- Monitors `dropzones/inbox/` for files
- Executes tasks automatically
- Saves results to `commands/results/`

---

## 📝 Sending Commands

### **Method 1: Text File**

```bash
# Write command to inbox
echo "Audit the codebase" > commands/inbox.txt

# ADA reads and executes automatically
# Results saved to: commands/results/task_TIMESTAMP.json
```

### **Method 2: System Tray**

1. Right-click ADA icon
2. Select "Quick Commands"
3. Choose command
4. Done!

### **Method 3: Dropzone**

1. Drop file into `dropzones/inbox/`
2. ADA processes automatically
3. Results in `dropzones/completed/`

---

## 📊 Status Monitoring

**Status File:** `ada_status.json`

```json
{
  "service_status": "running",
  "last_check": "2025-11-25T19:51:00",
  "tasks_completed": 5,
  "tasks_failed": 0,
  "uptime_start": "2025-11-25T19:00:00"
}
```

---

## 🎯 Quick Commands

**Available via System Tray:**
- **Audit Codebase** - Full codebase analysis
- **Create Quiz** - Generate quiz questions
- **Find Duplicates** - Detect duplicate code
- **Analyze Code** - Code structure analysis

---

## 📁 Directory Structure

```
LearnQwest/
├── ada_service.py              # Background service
├── ada_tray.py                 # System tray app
├── ada_service_config.json     # Configuration
├── start_ada_service.bat       # Service launcher
├── start_ada_tray.bat          # Tray launcher
├── install_ada_service.bat     # Installation
├── commands/
│   ├── inbox.txt              # Write commands here
│   └── results/               # Results appear here
├── dropzones/
│   ├── inbox/                 # Drop files here
│   ├── processing/            # Currently processing
│   ├── completed/             # Success
│   └── failed/                # Errors
├── ada_status.json            # Current status
└── ada_service.log            # Service logs
```

---

## ⚙️ Configuration

**File:** `ada_service_config.json`

```json
{
  "check_interval": 5,              // Check every 5 seconds
  "enable_dropzone": true,          // Enable dropzone monitoring
  "enable_commands": true,          // Enable command file monitoring
  "max_retries": 3                  // Retry failed tasks
}
```

---

## 🔧 Troubleshooting

**Service won't start:**
```bash
# Check Python version
python --version

# Reinstall packages
python -m pip install pystray pillow pywin32 --upgrade
```

**Commands not processing:**
- Check `ada_status.json` for service status
- Check `ada_service.log` for errors
- Ensure `commands/inbox.txt` exists and is writable

**System tray not showing:**
- Restart `start_ada_tray.bat`
- Check Task Manager for python.exe processes
- Check system tray overflow area

---

## 🚀 Advanced Usage

### **Auto-start with Windows:**

1. Press `Win+R`
2. Type: `shell:startup`
3. Copy `start_ada_tray.bat` to this folder
4. ADA starts automatically on login!

### **Custom Commands:**

Edit `ada_tray.py` to add your own quick commands:

```python
self.quick_commands = {
    "My Command": "Your custom task description here"
}
```

---

## 📋 Integration

**Works with:**
- ✅ ADA Coordinator (existing)
- ✅ ADA Dropzone (existing)
- ✅ Named Workflows
- ✅ All 12 Ions
- ✅ Observability/Trace

---

## [OK] Phase 7 Complete!

**ADA is now your persistent assistant!** 🎯

**Never Do Manual Work Again™**
