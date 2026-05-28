# 🔍 Job Hunter Bot — Automated Daily Job Search

> Powered by **Claude (Anthropic API)** + **GitHub Actions** + **SerpAPI**
> 
> Automatically searches Stepstone, Indeed, and LinkedIn every day at **12:00 PM**,
> scores each job against your profile using AI, and generates a **Word (.docx) + HTML report**
> committed directly to this repository.

---

## 📁 Project Structure

```
job-hunter/
│
├── .github/
│   └── workflows/
│       └── daily_jobs.yml          ← GitHub Actions schedule (runs daily at 12:00 PM)
│
├── job_scraper/
│   ├── main.py                     ← Entry point — orchestrates the full pipeline
│   ├── scraper.py                  ← Fetches jobs from Stepstone/Indeed/LinkedIn
│   ├── analyzer.py                 ← Claude API scores & enriches each listing
│   ├── report_generator.py         ← Builds .docx and .html reports
│   └── config.py                   ← ⚙️ YOUR PROFILE — edit this to customize
│
├── output/
│   └── reports/                    ← All generated reports stored here (by date)
│       ├── jobs_2026-05-28.docx
│       ├── jobs_2026-05-28.html
│       └── jobs_2026-05-28.json
│
├── docs/
│   └── index.html                  ← GitHub Pages — always shows latest report
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Setup Guide (One-Time, ~10 minutes)

### Step 1 — Fork / Create the GitHub Repo

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `job-hunter` (or anything you like)
3. Upload all files from this project, **or** clone and push:

```bash
git init
git add .
git commit -m "🚀 Initial commit — Job Hunter Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-hunter.git
git push -u origin main
```

---

### Step 2 — Get Your API Keys (both free)

#### A) Anthropic API Key (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in with your Claude account
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)

> 💡 Free credits are available for new accounts. The daily job search uses ~$0.01–0.05/day.

#### B) SerpAPI Key (job search)
1. Go to [serpapi.com](https://serpapi.com) → **Sign Up** (free)
2. Free tier: **100 searches/month** (enough for ~3 runs/day of queries)
3. Go to **Dashboard** → copy your API key

---

### Step 3 — Add Secrets to GitHub

1. In your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key (`sk-ant-...`) |
| `SERPAPI_KEY` | Your SerpAPI key |

---

### Step 4 — Enable GitHub Pages (for the HTML web view)

1. In your repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` → Folder: `/docs`
4. Click **Save**

After the first run, your live report will be at:
```
https://YOUR_USERNAME.github.io/job-hunter/
```

---

### Step 5 — Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will run automatically every day at **12:00 PM UTC** (1:00 PM CET / 2:00 PM CEST)

**To trigger a manual run immediately:**
- Actions tab → **Daily Job Hunter** → **Run workflow** → **Run workflow**

---

## ⚙️ Customization

Edit `job_scraper/config.py` to update:

| Section | What to change |
|---|---|
| `CANDIDATE` | Your name, location, study program |
| `SKILLS` | Add/remove skills as you learn new things |
| `JOB_PREFERENCES` | Hours per week, remote preference, commute radius |
| `PROFESSIONAL_QUERIES` | Search terms for professional jobs |
| `GENERAL_QUERIES` | Search terms for general/warehouse jobs |
| `OUTPUT` | Max jobs per category, output formats |

After editing, just commit and push — the next run picks up your changes automatically.

---

## 📥 Downloading Your Reports

**Option 1 — GitHub (always available):**
- Go to `output/reports/` in the repo
- Click any `.docx` or `.html` file → **Download**

**Option 2 — GitHub Pages (HTML only):**
- Visit `https://YOUR_USERNAME.github.io/job-hunter/`
- Always shows the latest report with live filter buttons

**Option 3 — Clone locally:**
```bash
git pull origin main
# Reports are in output/reports/
```

---

## 🔄 How It Works (Daily Pipeline)

```
12:00 PM UTC
     │
     ▼
GitHub Actions triggers daily_jobs.yml
     │
     ▼
[1] scraper.py — queries SerpAPI for fresh listings
     │           (Stepstone + Indeed + LinkedIn)
     ▼
[2] analyzer.py — sends batches to Claude API
     │            Claude scores each job 0–10
     │            Identifies match reasons & concerns
     │            Flags German language requirements
     │            Gives cover letter tips
     ▼
[3] report_generator.py — builds:
     │    • jobs_YYYY-MM-DD.docx  (Word report)
     │    • jobs_YYYY-MM-DD.html  (web report)
     │    • jobs_YYYY-MM-DD.json  (raw data)
     ▼
[4] Git commit + push → reports saved to repo
     │
     ▼
You open GitHub or GitHub Pages → download latest report
```

---

## 💡 Tips

- **Add this to your CV:** "Built an automated AI-powered job search pipeline using Claude API, GitHub Actions, and Python" — it's a real project that demonstrates ML API integration, automation, and software engineering.
- **Claude skills:** The analyzer uses Claude's structured output to score jobs. You can extend `analyzer.py` to generate full cover letter drafts per job.
- **Extending the project:** Ideas for future improvements:
  - Email delivery via GitHub Actions + SendGrid (free tier)
  - Telegram bot notification when high-score jobs appear
  - Fine-tune queries based on past applications
  - Add salary scraping and filtering

---

## 🛠 Running Locally (for development)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/job-hunter.git
cd job-hunter

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export SERPAPI_KEY="your-serpapi-key"

# Run the pipeline
cd job_scraper
python main.py

# Reports will be in ../output/reports/
```

---

## 📊 Report Scores Explained

| Score | Meaning | Recommendation |
|---|---|---|
| 8–10 ⭐ | Strong match — apply immediately | ✅ APPLY |
| 5–7 🟡 | Partial match — worth considering | 🟡 CONSIDER |
| 0–4 🔴 | Poor match or German B2+ required | ❌ SKIP |

---

*Built as a learning project by Arash Karimi — MSc Human-Centered Intelligent Systems, RWTH Aachen*  
*Powered by Claude (Anthropic) · GitHub Actions · SerpAPI · python-docx*
