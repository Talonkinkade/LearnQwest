# 🚀 Getting Started with LearnQwest

**Get up and running in 5 minutes**

---

## 📋 Prerequisites

- **Python 3.9+** installed
- **Git** installed
- **GitHub account** (for private repo)
- **API Keys** (optional, for full features):
  - Anthropic Claude API key
  - YouTube Data API key

---

## ⚡ Quick Install

### 1. Clone the Repository

```bash
git clone https://github.com/Talonkinkade/LearnQwest.git
cd LearnQwest
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
notepad .env  # Windows
nano .env     # macOS/Linux
```

Add your keys:

```env
# Required for AI features
ANTHROPIC_API_KEY=your_claude_api_key_here

# Required for YouTube extraction
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here
```

---

## 🎯 Your First Task

### Test ADA Orchestrator

```python
# test_ada.py
import asyncio
from ada_orchestrator import ADAOrchestrator

async def main():
    # Initialize ADA
    ada = ADAOrchestrator()
    
    # Simple test task
    task = {
        "input": "Hello ADA! Test task.",
        "type": "test"
    }
    
    # Execute
    result = await ada.execute_task(task)
    
    # Check result
    print(f"✅ Task completed in {result.duration_ms}ms")
    print(f"Success: {result.success}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python test_ada.py
```

Expected output:

```
✅ Task completed in 306ms
Success: True
```

---

## 📚 Next Steps

### Learn the Basics

1. **[Full Intelligence Pipeline™](../concepts/FULL_INTELLIGENCE_PIPELINE.md)**
   - Understand the core workflow
   - Question → Classify → Steps → Execute → Log → Learn

2. **[ADA Orchestrator](../ada/ADA_OVERVIEW.md)**
   - Learn how ADA coordinates agents
   - RoutingSpine, FeedbackLoop, JSONLLogger

3. **[BMAD Ions](../concepts/BMAD_IONS.md)**
   - Explore the 6 specialized agents
   - Omnisearch, Quality Assessor, etc.

### Try Real Tasks

1. **[Extract YouTube Video](../use-cases/YOUTUBE_LEARNING.md)**
   ```python
   task = {
       "input": "Extract wisdom from this video",
       "url": "https://youtube.com/watch?v=example"
   }
   result = await ada.execute_task(task)
   ```

2. **[Analyze Code](../use-cases/CODE_ANALYSIS.md)**
   ```python
   task = {
       "input": "Analyze code quality",
       "file": "path/to/your/code.py"
   }
   result = await ada.execute_task(task)
   ```

3. **[Generate Qwest-ions](../use-cases/PROJECT_BUILDING.md)**
   ```python
   task = {
       "input": "Create learning questions",
       "topic": "Python async/await"
   }
   result = await ada.execute_task(task)
   ```

### Build Something

1. **[Build Your First Ion](../tutorials/BUILD_FIRST_ION.md)**
   - Create a custom agent
   - Wire it into ADA

2. **[Create Custom Qwest-ions](../tutorials/CREATE_QWESTIONS.md)**
   - Design learning content
   - Use Qwestian Companions

3. **[Wire Real Agents](../tutorials/WIRE_ADA_AGENTS.md)**
   - Connect BMAD Ions to ADA
   - Replace simulated execution

---

## 🛠️ Common Commands

### Run Tests

```bash
# All tests
python -m pytest

# Specific test
python -m pytest tests/test_ada.py

# With coverage
python -m pytest --cov=.
```

### Check Logs

```bash
# View recent ADA logs
python -c "from ada_orchestrator import ADAOrchestrator; ada = ADAOrchestrator(); print(ada.jsonl_logger.get_recent_logs(10))"

# View feedback data
cat ada_feedback.jsonl

# View session logs
ls ada_logs/
```

### Agent Status

```python
# check_agents.py
from ada_orchestrator import ADAOrchestrator

ada = ADAOrchestrator()
stats = ada.feedback_loop.get_agent_stats()

print("Agent Performance:")
for agent, rate in stats.items():
    print(f"  {agent}: {rate*100:.1f}% success rate")
```

---

## 🔧 Troubleshooting

### Issue: Import Error

```
ModuleNotFoundError: No module named 'ada_orchestrator'
```

**Solution:**
```bash
# Make sure you're in the right directory
cd LearnQwest

# Make sure venv is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API Key Error

```
Error: ANTHROPIC_API_KEY not found
```

**Solution:**
```bash
# Check .env file exists
ls .env

# Check key is set
cat .env | grep ANTHROPIC

# If missing, add it
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### Issue: Permission Error

```
PermissionError: [Errno 13] Permission denied: 'ada_logs'
```

**Solution:**
```bash
# Create logs directory
mkdir ada_logs

# Set permissions (macOS/Linux)
chmod 755 ada_logs
```

---

## 📖 Documentation

### Essential Reading

- **[Wiki Home](../WIKI_HOME.md)** - Complete documentation index
- **[Architecture](../development/ARCHITECTURE.md)** - System design
- **[API Reference](../ada/API_REFERENCE.md)** - Complete API docs

### Video Tutorials

- **Coming Soon:** Video walkthrough series
- **Coming Soon:** Live coding sessions
- **Coming Soon:** Community workshops

---

## 🤝 Get Help

### Community

- **[GitHub Discussions](https://github.com/Talonkinkade/LearnQwest/discussions)** - Ask questions
- **[Issue Tracker](https://github.com/Talonkinkade/LearnQwest/issues)** - Report bugs
- **Discord** - Coming soon

### Support

- **Email:** support@learnqwest.com (coming soon)
- **Twitter:** @LearnQwest (coming soon)

---

## ✅ Checklist

Before moving forward, make sure you have:

- [ ] Cloned the repository
- [ ] Created virtual environment
- [ ] Installed dependencies
- [ ] Configured `.env` file
- [ ] Tested ADA orchestrator
- [ ] Read the Full Intelligence Pipeline™ docs
- [ ] Explored the wiki

---

## 🎓 Learning Paths

### For Beginners

1. Complete this guide
2. Read [Full Intelligence Pipeline™](../concepts/FULL_INTELLIGENCE_PIPELINE.md)
3. Try [First Quest](./FIRST_QUEST.md)
4. Explore [YouTube Learning](../use-cases/YOUTUBE_LEARNING.md)

### For Developers

1. Complete this guide
2. Study [Architecture](../development/ARCHITECTURE.md)
3. Read [ADA Overview](../ada/ADA_OVERVIEW.md)
4. Build [Your First Ion](../tutorials/BUILD_FIRST_ION.md)

### For Power Users

1. Complete this guide
2. Master [Agent Orchestration](../workflows/AGENT_ORCHESTRATION.md)
3. Wire [Real Agents](../tutorials/WIRE_ADA_AGENTS.md)
4. Deploy [To Production](../tutorials/DEPLOY_PRODUCTION.md)

---

## 🚀 Ready to Build?

You're all set! Choose your next step:

- **[Try Your First Quest](./FIRST_QUEST.md)** - Guided project
- **[Explore Use Cases](../use-cases/YOUTUBE_LEARNING.md)** - See what's possible
- **[Build an Ion](../tutorials/BUILD_FIRST_ION.md)** - Create custom agent
- **[Read the Wiki](../WIKI_HOME.md)** - Deep dive into docs

---

*Welcome to LearnQwest. Let's turn questions into quests!* 🎯
