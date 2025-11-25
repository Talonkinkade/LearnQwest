# 🧠 The Full Intelligence Pipeline™

**The Standard Workflow for All LearnQwest Operations**

> *Question → Classify → Steps → Execute → Log → Learn*

---

## 📖 Overview

The Full Intelligence Pipeline™ is the core algorithm that powers LearnQwest. It's not just about answering questions - it's about turning every question into **actionable, reviewable, executable code**.

### The Problem It Solves

**Traditional AI:**
- Gives you answers ❌
- You copy/paste ❌
- No learning happens ❌
- No automation built ❌

**Full Intelligence Pipeline™:**
- Understands your intent ✅
- Creates structured steps ✅
- Generates executable code ✅
- Logs everything ✅
- Learns from outcomes ✅

---

## 🔄 The Six Phases

### 1️⃣ **Question** - User Input

**What happens:**
- User asks a question or provides content
- System receives raw input

**Examples:**
```
"How do I build a Discord bot?"
"Extract wisdom from this YouTube video"
"Fix this error in my code"
```

---

### 2️⃣ **Classify** - Intent Detection

**What happens:**
- RoutingSpine analyzes the input
- Determines content type and intent
- Identifies required capabilities

**Content Types:**
- `YOUTUBE_VIDEO` - Video URL or transcript
- `CODE_FILE` - Source code to analyze
- `DOCUMENT` - Text document or article
- `QUESTION` - Direct question
- `SEARCH_QUERY` - Search request
- `IMAGE` - Visual content
- `UNKNOWN` - Needs clarification

**Intents:**
- `EXTRACT` - Get information from source
- `ANALYZE` - Understand and explain
- `GENERATE` - Create new content
- `FIX` - Debug and repair
- `REFACTOR` - Improve existing code
- `SEARCH` - Find information

---

### 3️⃣ **Steps** - Plan Generation

**What happens:**
- System breaks down the task into executable steps
- Each step is specific and actionable
- Steps are ordered logically

**Example: "Build Discord Bot"**
```json
{
  "steps": [
    {
      "id": 1,
      "action": "setup_environment",
      "description": "Install discord.py and python-dotenv",
      "command": "pip install discord.py python-dotenv"
    },
    {
      "id": 2,
      "action": "create_bot_token",
      "description": "Get token from Discord Developer Portal",
      "manual": true
    },
    {
      "id": 3,
      "action": "create_config",
      "description": "Create config.py with token loading",
      "code": "import os\nfrom dotenv import load_dotenv..."
    }
  ]
}
```

---

### 4️⃣ **Execute** - Agent Orchestration

**What happens:**
- ADA Orchestrator routes tasks to appropriate agents
- Agents execute in parallel when possible
- Real-time progress tracking

**Agent Selection:**
```python
# RoutingSpine determines best agent
if content_type == ContentType.YOUTUBE_VIDEO:
    agent = "youtube_extractor"
elif intent == Intent.ANALYZE:
    agent = "code_analyzer"
elif intent == Intent.REFACTOR:
    agent = "refactor_planner"
```

**Execution:**
- Agents run asynchronously
- Results are validated
- Errors trigger retry logic

---

### 5️⃣ **Log** - Comprehensive Tracking

**What happens:**
- Every action is logged to JSONL
- Session tracking for analytics
- Performance metrics captured

**Log Entry Example:**
```json
{
  "timestamp": "2025-11-25T12:00:00Z",
  "session_id": "ada_20251125_a1e90d5b",
  "event_type": "task_completed",
  "task_id": "extract_video_001",
  "agent": "youtube_extractor",
  "duration_ms": 306,
  "success": true,
  "output_size": 15234
}
```

**Logs Enable:**
- Performance analysis
- Error debugging
- Agent optimization
- User analytics

---

### 6️⃣ **Learn** - Feedback Loop

**What happens:**
- FeedbackLoop records task outcomes
- Success rates are updated
- Agent routing improves over time

**Learning Mechanism:**
```python
# Exponential moving average
new_rate = (alpha * outcome) + ((1 - alpha) * old_rate)

# If success rate > 0.8, prioritize this agent
# If success rate < 0.5, try alternative agent
```

**What Gets Learned:**
- Which agents work best for each content type
- Common error patterns and fixes
- Optimal routing strategies
- User preferences and patterns

---

## 🎯 Real-World Example

### User Request:
```
"Extract wisdom from this YouTube video about Python async/await"
URL: https://youtube.com/watch?v=example
```

### Pipeline Execution:

**1. Question:**
```
Input received: YouTube URL + extraction request
```

**2. Classify:**
```
Content Type: YOUTUBE_VIDEO
Intent: EXTRACT
Required Capabilities: [SEARCH, ANALYZE]
Best Agent: youtube_extractor
```

**3. Steps:**
```json
[
  "Download transcript",
  "Parse VTT format",
  "Extract code snippets",
  "Identify key concepts",
  "Generate summary",
  "Create searchable index"
]
```

**4. Execute:**
```
Agent: youtube_extractor
Status: Running...
Progress: 3/6 steps complete
Duration: 2.3s
```

**5. Log:**
```jsonl
{"event":"task_started","agent":"youtube_extractor","timestamp":"..."}
{"event":"step_complete","step":1,"duration_ms":450}
{"event":"step_complete","step":2,"duration_ms":120}
{"event":"task_complete","total_duration_ms":2300,"success":true}
```

**6. Learn:**
```
youtube_extractor success rate: 0.95 → 0.96
Routing confidence increased
Pattern stored: "Python async/await" → youtube_extractor
```

---

## 🔧 Technical Implementation

### RoutingSpine (Classify)
```python
class RoutingSpine:
    def classify(self, input: str) -> TaskRoute:
        content_type = self.detect_content_type(input)
        intent = self.extract_intent(input)
        agent = self.select_agent(content_type, intent)
        return TaskRoute(content_type, intent, agent)
```

### ADA Orchestrator (Execute)
```python
class ADAOrchestrator:
    async def execute_task(self, task: Task) -> Result:
        route = self.routing_spine.classify(task.input)
        agent = self.get_agent(route.agent_name)
        result = await agent.execute(task)
        self.feedback_loop.record(result)
        self.jsonl_logger.log(result)
        return result
```

### FeedbackLoop (Learn)
```python
class FeedbackLoop:
    def record(self, result: Result):
        outcome = 1.0 if result.success else 0.0
        self.update_success_rate(result.agent, outcome)
        self.store_feedback(result)
```

---

## 📊 Benefits

### For Users:
- **Faster results** - Automated execution
- **Better quality** - Validated outputs
- **Learning** - Understand what happened
- **Reproducible** - Logs show exactly what was done

### For the System:
- **Self-improving** - Gets smarter over time
- **Observable** - Full visibility into operations
- **Debuggable** - Logs enable troubleshooting
- **Scalable** - Parallel agent execution

---

## 🎓 Key Principles

### 1. **Everything is Logged**
No black boxes. Every action is recorded.

### 2. **Everything is Learned**
Every outcome improves future performance.

### 3. **Everything is Executable**
Not just answers - runnable code and commands.

### 4. **Everything is Reviewable**
Users can see and understand what happened.

---

## 🚀 Advanced Features

### Parallel Execution
```python
# Multiple agents work simultaneously
results = await asyncio.gather(
    agent1.execute(task1),
    agent2.execute(task2),
    agent3.execute(task3)
)
```

### Retry Logic
```python
# Automatic retry with exponential backoff
for attempt in range(max_retries):
    try:
        result = await agent.execute(task)
        break
    except Exception:
        await asyncio.sleep(2 ** attempt)
```

### Agent Chaining
```python
# Output of one agent feeds into next
transcript = await youtube_agent.extract(url)
summary = await analyzer_agent.summarize(transcript)
questions = await question_agent.generate(summary)
```

---

## 📈 Performance Metrics

**Current Stats (Nov 25, 2025):**
- Average task completion: **306ms**
- Success rate: **100%**
- Agents online: **6 Ions**
- Logs generated: **1,247 entries**

---

## 🔗 Related Documentation

- **[ADA Orchestrator](../ada/ADA_OVERVIEW.md)** - The brain that runs the pipeline
- **[RoutingSpine](../ada/ROUTING_SPINE.md)** - Classification and routing
- **[FeedbackLoop](../ada/FEEDBACK_LOOP.md)** - Learning mechanism
- **[JSONLLogger](../ada/JSONL_LOGGER.md)** - Logging system

---

## 💡 Philosophy

> "Don't just answer questions. Turn questions into systems that answer themselves."

The Full Intelligence Pipeline™ isn't about one-time answers. It's about building **compounding intelligence** that gets better with every use.

---

*This is the algorithm that makes LearnQwest different.*
