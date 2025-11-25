# LearnQwest CodeMap - Quick Start Guide

## What You Just Built

LearnQwest CodeMap is a **visual exploration tool** that connects:
- **Your codebase** (functions, classes, files)
- **YouTube learning videos** (from IndyDevDan and others)
- **Interactive quests** (step-by-step learning paths)

Think of it as a "living map" of your code + the videos that taught you how to build it.

## System Requirements

- Python 3.9+
- Modern web browser
- VS Code (optional, for deep linking)

## File Structure

```
LearnQwest/
├── scripts/
│   ├── gen_codemap.py      # Scans codebase → generates JSON
│   └── gen_quests.py        # Adds learning quests to the map
├── web/
│   ├── index.html           # Web app entry point
│   ├── main.js              # React loader
│   └── CodeMapApp.jsx       # Main UI component
├── codemap.json             # Generated map (created by you)
└── QUICKSTART.md            # This file
```

## Step 1: Generate Your Codemap

**Scan RAGEFORCE project:**
```bash
cd C:\Users\talon\OneDrive\Projects\LearnQwest
python scripts/gen_codemap.py C:\Users\talon\OneDrive\Projects\RAGEFORCE --out codemap_rageforce.json
```

**Scan LearnQwest itself:**
```bash
python scripts/gen_codemap.py . --out codemap_learnqwest.json
```

**Output:** JSON file with all functions, classes, imports, and file relationships.

## Step 2: Add Learning Quests (Optional)

```bash
python scripts/gen_quests.py
```

This adds interactive learning paths based on your code patterns.

## Step 3: View in Browser

### Option A: VS Code Live Server (Recommended)

1. Open `C:\Users\talon\OneDrive\Projects\LearnQwest\web\` in VS Code
2. Right-click `index.html` → "Open with Live Server"
3. Browser opens at `http://localhost:5500`

### Option B: Python HTTP Server

```bash
cd C:\Users\talon\OneDrive\Projects\LearnQwest\web
python -m http.server 8000
```

Open `http://localhost:8000` in your browser.

### Option C: Any Static Server

Just serve the `web/` folder with any static file server.

## Step 4: Connect Real Data

**Update CodeMapApp.jsx to load your actual codemap:**

Find this line in [web/CodeMapApp.jsx](web/CodeMapApp.jsx:117):
```javascript
const [data, setData] = useState(sampleCodeMap);
```

Replace with:
```javascript
const [data, setData] = useState(null);

useEffect(() => {
  fetch('/codemap_rageforce.json')
    .then(r => r.json())
    .then(setData);
}, []);
```

## Using the Interface

### Search Files
- Type in search box: file names, function names, tags
- Example: "dropzone" shows all dropzone-related files

### Explore Code
- Click any file card to see:
  - Functions and classes
  - Imports
  - Related files (dependency graph)
  - VS Code deep link
  - YouTube video links

### Learning Quests
- Right panel shows step-by-step learning tasks
- Based on actual code patterns in your project
- Validates your understanding

## Connecting YouTube Videos

**Edit [scripts/gen_codemap.py](scripts/gen_codemap.py:312-315):**

```python
YOUTUBE_HINTS = {
    "dropzone": {
        "title": "File-based automation with dropzones",
        "url": "https://www.youtube.com/watch?v=ACTUAL_VIDEO_ID&t=123"
    },
    "teks": {
        "title": "TEKS standards mapping",
        "url": "https://www.youtube.com/watch?v=ANOTHER_VIDEO_ID&t=456"
    },
    # Add more patterns based on your IndyDevDan transcripts
}
```

Then re-run `gen_codemap.py` to update links.

## Advanced: Auto-Link from Transcripts

You have 31 IndyDevDan videos processed! Let's connect them:

```bash
# Create a script to map transcripts → code keywords
python scripts/link_youtube_to_code.py
```

**TODO:** Build this script to:
1. Read transcripts from `processed_content/indydevdan/txt/`
2. Extract key concepts (dropzone, agent, orchestrator, etc.)
3. Match to files by keyword
4. Update `YOUTUBE_HINTS` automatically

## Customization

### Add More File Types

Edit [gen_codemap.py](scripts/gen_codemap.py:289-310) EXT_FUN dict:

```python
".jsx": {
    "func": re.compile(r"function\s+([A-Za-z_]\w*)\(|const\s+([A-Za-z_]\w*)\s*=\s*\(.*?\)\s*=>", re.M),
    "class": re.compile(r"class\s+([A-Za-z_]\w*)\b", re.M),
    "import": re.compile(r"import\s+.*?from\s+['\"]([@\w\-/\.]+)['\"]", re.M),
},
```

### Add More Quest Templates

Edit [gen_quests.py](scripts/gen_quests.py:387-411):

```python
{
  "match": "your_keyword",
  "quest": {
    "title": "[BRACKET] Your Quest Title",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "validate": "How to verify completion"
  }
}
```

### Change UI Colors

Edit [CodeMapApp.jsx](web/CodeMapApp.jsx:88):

```javascript
const gradientBg = "bg-gradient-to-r from-[#667eea] to-[#764ba2]";
```

Uses Tailwind CSS - any valid Tailwind classes work.

## Real-World Use Cases

### 1. Onboarding New Developers
- "Here's the codebase map + videos that explain each part"
- Click through to learn the architecture

### 2. Documentation That Never Gets Stale
- Auto-generated from actual code
- Always up-to-date
- Linked to video explanations

### 3. Learning Path Creator
- "Want to learn dropzones? Follow these quests"
- Interactive, validated learning

### 4. Code Navigation
- Visual dependency graph
- Jump to VS Code with one click
- See what imports what

## Troubleshooting

**Codemap shows no files:**
- Check that Python found your target directory
- Look for errors in terminal output

**Web page is blank:**
- Open browser console (F12)
- Check for CORS errors
- Make sure you're using a web server (not file://)

**VS Code links don't work:**
- Make sure VS Code is installed
- On Windows, `vscode://` protocol should work automatically

**React errors:**
- Check that you have internet (loads React from CDN)
- Try a different browser

## Next Steps

1. Generate codemap for all your projects
2. Map more YouTube videos to code sections
3. Create custom quests for learning workflows
4. Share with team for onboarding
5. Build automated linking from transcripts

## Philosophy

**This tool is about LEARNING, not just documentation.**

Every line of code you write was influenced by something you learned. LearnQwest CodeMap makes that connection explicit and navigable.

- See the code
- Watch the video that taught it
- Practice with quests
- Validate your understanding

**Learn → Build → Validate → Repeat**

---

Built by LINK | Powered by LearnQwest™ | "Learning that compounds, forever"
