# 🔄 LearnQwest Workflow Catalog

**Automated workflows for development and documentation**

---

## 📋 Available Workflows

### 1. 🔧 Daemonization Workflow
**File:** `GitHubQwest`  
**Execution Mode:** Safe Mode  
**Purpose:** Daemonization and background process management

**Content:**
- GitHubQwest formula
- LEARNQWEST automation
- Background service setup

---

### 2. 🔒 GitHub Private Repository Workflow
**File:** `GitHub Private`  
**Execution Mode:** Safe Mode  
**Purpose:** Private repository management and setup

**Content:**
- Repository configuration
- Access control
- Security settings
- Push/pull automation

---

### 3. 🚀 Getting Started Workflow
**File:** `GettingStarted`  
**Execution Mode:** Safe Mode  
**Purpose:** Onboarding and initial setup

**Content:**
- Installation steps
- Environment configuration
- First-time setup
- Quick start guide

---

### 4. 🤖 ADA Orchestrator Workflow
**File:** `ADA Orchestrator`  
**Execution Mode:** Safe Mode  
**Purpose:** ADA system deployment and management

**Content:**
- ADA initialization
- Agent routing setup
- Feedback loop configuration
- Logger setup

---

### 5. 🧠 Full Intelligence Pipeline Workflow
**File:** `Full Intelligence Pipeline`  
**Execution Mode:** Safe Mode  
**Purpose:** Execute the complete intelligence pipeline

**Content:**
- Question classification
- Step generation
- Agent execution
- Logging and learning

---

## 🎯 Workflow Execution

### Safe Mode (Default)
All workflows run in **Safe Mode** by default:
- User approval required for destructive operations
- Automatic validation of inputs
- Rollback on errors
- Comprehensive logging

### Auto-Execution Mode
Some workflows support `auto_execution_mode: 1`:
- Automated execution without prompts
- Used for trusted, repeatable operations
- Enabled via YAML frontmatter

---

## 📖 Usage

### Via Windsurf
1. Open workflow card
2. Review configuration
3. Click "Execute"
4. Monitor progress

### Via CLI
```bash
# Execute workflow
windsurf workflow run <workflow-name>

# List workflows
windsurf workflow list

# Validate workflow
windsurf workflow validate <workflow-name>
```

---

## 🔗 Related Documentation

- **[Workflow System](../development/WORKFLOW_SYSTEM.md)** - Architecture
- **[Automation Guide](../development/AUTOMATION.md)** - Best practices
- **[Safe Mode](../reference/SAFE_MODE.md)** - Execution safety

---

## 🛠️ Creating Custom Workflows

### Workflow Template

```yaml
---
name: My Custom Workflow
description: Description of what this does
execution_mode: safe
auto_execution_mode: 0
---

# Workflow Steps

## Step 1: Initialize
- Action 1
- Action 2

## Step 2: Execute
- Action 3
- Action 4

## Step 3: Validate
- Check results
- Log outcomes
```

### Best Practices

1. **Always use Safe Mode** for new workflows
2. **Document each step** clearly
3. **Add validation** at each stage
4. **Log all operations** for debugging
5. **Test thoroughly** before auto-execution

---

## 📊 Workflow Status

| Workflow | Status | Last Run | Success Rate |
|----------|--------|----------|--------------|
| Daemonization | ✅ Active | - | - |
| GitHub Private | ✅ Active | - | - |
| GettingStarted | ✅ Active | - | - |
| ADA Orchestrator | ✅ Active | - | - |
| Full Intelligence Pipeline | ✅ Active | - | - |

---

*Workflows enable automated, repeatable operations across LearnQwest*
