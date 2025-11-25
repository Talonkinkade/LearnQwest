# 🔒 GitHub Setup - Private Repository

**IMPORTANT: All LearnQwest repositories MUST be PRIVATE**

---

## 🚨 Privacy Requirements

- ✅ **All repos:** PRIVATE only
- ❌ **Never public:** Contains proprietary learning systems
- 🔐 **Access control:** Invite-only collaboration

---

## 📋 Create Private Repository

### Option 1: GitHub Web Interface (Recommended)

1. **Go to GitHub:**
   - Visit: https://github.com/new

2. **Repository Settings:**
   - **Name:** `LearnQwest`
   - **Description:** "LINK's permanent learning and automation platform"
   - **Visibility:** ⚠️ **PRIVATE** (critical!)
   - **Initialize:** Leave unchecked (we have existing code)

3. **Create Repository:**
   - Click "Create repository"

4. **Push Existing Code:**
   ```bash
   cd C:\Users\talon\OneDrive\Projects\LearnQwest
   git remote add origin https://github.com/Talonkinkade/LearnQwest.git
   git branch -M main
   git push -u origin main
   ```

---

### Option 2: GitHub CLI (After Token Fix)

**Current Issue:** `GITHUB_TOKEN` env var has wrong permissions

**Solution:**
```bash
# Clear the environment variable
$env:GITHUB_TOKEN = $null

# Create private repo
gh repo create LearnQwest --private --source=. --push
```

---

## 🔐 Repository Security

### Required Settings

After creating the repo, configure these settings:

1. **Settings → General:**
   - ✅ Private repository
   - ❌ Disable "Allow forking"
   - ❌ Disable "Sponsorships"

2. **Settings → Branches:**
   - ✅ Protect `main` branch
   - ✅ Require pull request reviews
   - ✅ Require status checks

3. **Settings → Secrets:**
   - Add `ANTHROPIC_API_KEY`
   - Add `YOUTUBE_API_KEY`
   - Add `OPENAI_API_KEY` (optional)

---

## 👥 Collaboration

### Adding Collaborators

Only invite trusted collaborators:

1. **Settings → Collaborators**
2. Click "Add people"
3. Enter GitHub username
4. Select role:
   - **Admin** - Full access
   - **Write** - Can push code
   - **Read** - View only

---

## 🔑 Access Tokens

### Personal Access Token (PAT)

For CLI operations, create a PAT with these scopes:

1. **Go to:** https://github.com/settings/tokens
2. **Generate new token (classic)**
3. **Select scopes:**
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Actions)
   - ✅ `delete_repo` (if needed)
4. **Copy token** and save securely

### Use Token

```bash
# Set token for this session
$env:GITHUB_TOKEN = "your_token_here"

# Or add to .env file (DO NOT COMMIT)
echo "GITHUB_TOKEN=your_token_here" >> .env
```

---

## 📦 .gitignore

Ensure sensitive files are never committed:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# API Keys
*_api_key.txt
secrets/

# Logs
*.log
ada_logs/
ada_feedback.jsonl

# Python
__pycache__/
*.pyc
venv/
*.egg-info/

# Node/Bun
node_modules/
.bun/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Private data
processed_content/
intake_zones/*/
output/
```

---

## ✅ Verification Checklist

Before pushing code, verify:

- [ ] Repository is set to PRIVATE
- [ ] `.gitignore` is configured
- [ ] No API keys in code
- [ ] No sensitive data in commits
- [ ] `.env` file is gitignored
- [ ] Secrets are in GitHub Secrets (not code)

---

## 🚨 If Accidentally Made Public

**Immediate actions:**

1. **Make private immediately:**
   - Settings → Danger Zone → Change visibility → Private

2. **Rotate all API keys:**
   - Anthropic API key
   - YouTube API key
   - Any other exposed keys

3. **Check commit history:**
   ```bash
   # Search for potential secrets
   git log --all --full-history --source --all -- '*secret*' '*key*' '*.env'
   ```

4. **Consider new repository:**
   - If secrets were committed, create fresh private repo
   - Copy clean code only (no git history)

---

## 📞 Support

If you need help with GitHub setup:

- **GitHub Docs:** https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
- **GitHub Support:** https://support.github.com/

---

## 🎯 Current Status

**Repository Status:**
- Name: `LearnQwest`
- Owner: `Talonkinkade`
- Visibility: ⚠️ **MUST BE PRIVATE**
- Status: Ready to create

**Next Steps:**
1. Create private repo at github.com/new
2. Push local code
3. Configure security settings
4. Add collaborators (if needed)

---

*Remember: PRIVATE repositories only. No exceptions.* 🔒
