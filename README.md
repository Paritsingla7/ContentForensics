# 🔍 ContentForensics - Complete Guide

A content-quality, spam-risk, and AI-content-likelihood checker that crawls a whole website (not just one page) and reports sentiment, entities, link health, content-quality signals, site-wide duplicate/scaled-content patterns, and an AI-likelihood score per page.

---

## 🎯 HOW TO RUN THIS CODE (From Scratch)

### Step 1: Install Dependencies (One-time setup)

Open terminal in this directory and run:

```bash
# (Recommended) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python packages
python -m pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

**Note:** `requirements.txt` now includes `transformers` and `torch` for the AI-likelihood check (the `distilgpt2` model, ~350MB, downloads automatically the first time you run `main.py`). This install is noticeably heavier and slower than the rest of the dependencies — that's expected.

### Step 2: Crawl and Analyze a Website

```bash
python main.py "https://example.com"
```

Optionally pass a JSON file to override any default threshold/weight (see `config.py` for every configurable field):

```bash
python main.py "https://example.com" my_config.json
```

**What happens:**
- Discovers pages to crawl (sitemap.xml first, falls back to following same-domain links; respects `robots.txt`)
- Per page: scrapes content, analyzes sentiment, identifies named entities, counts internal/external links, detects spam techniques (keyword stuffing, hidden text)
- Per page: runs content-quality checks (readability, thin content, repetitive phrasing, anchor over-optimization) and computes an AI-likelihood score
- Across the whole crawl: checks for duplicate/near-duplicate pages and scaled-content patterns
- Saves everything to `report.json`

### Step 3: View the Beautiful Report

```bash
python serve.py
```

**What happens:**
- Starts a local web server
- Opens your browser automatically
- Displays the report with a beautiful dark theme UI — a site-wide issues summary up top, then a clickable list of every crawled page that expands into full per-page detail

**⚠️ IMPORTANT**: Never double-click `report_veiwer.html`! Always use `serve.py` to avoid CORS errors.

---

## 📁 FILE PURPOSES (What Each File Does)

### **CORE PYTHON FILES** (Backend - Do the Analysis)

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `main.py` | **Main script** - Coordinates the crawl + all analysis, generates report.json | ❌ NO - Essential |
| `config.py` | `Config` dataclass with every threshold/weight, plus JSON-override loading | ❌ NO - Essential |
| `crawler.py` | Discovers pages to analyze (sitemap.xml, BFS link-following, robots.txt) | ❌ NO - Essential |
| `scraper.py` | Fetches and cleans a single page's HTML | ❌ NO - Essential |
| `analyzer.py` | Sentiment/entity analysis + content-quality checks (readability, thin content, repetitive phrasing, anchor over-optimization) | ❌ NO - Essential |
| `site_checks.py` | Site-wide duplicate-page and scaled-content-pattern detection | ❌ NO - Essential |
| `ai_check.py` | AI-likelihood check (burstiness, perplexity via distilgpt2, vocabulary diversity, cliché phrases) | ❌ NO - Essential |
| `spamdexing.py` | Detects keyword stuffing and hidden text | ❌ NO - Essential |
| `serve.py` | Runs local web server to view reports | ❌ NO - Essential |

### **FRONTEND FILES** (Display the Results)

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `report_veiwer.html` | Report viewer webpage structure | ❌ NO - Essential |
| `script.js` | Loads report.json and renders the site-wide summary + per-page detail cards | ❌ NO - Essential |
| `styles.css` | Beautiful dark theme styling | ❌ NO - Essential |

### **GENERATED FILES** (Created by the program)

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `report.json` | Analysis results (created by main.py) | ✅ YES - Regenerated each run |
| `__pycache__/` | Python bytecode cache | ✅ YES - Auto-recreated |

### **DOCUMENTATION FILES**

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `README.md` | This guide you're reading | ⚠️ Optional - Helpful but not required |

---

## 🔄 COMPLETE WORKFLOW EXPLAINED

```
YOU                                  BACKEND (Python)                        FRONTEND (Browser)
 |                                        |                                        |
 | Step 1: Run analyzer                  |                                        |
 |---------------------------------> main.py                                      |
 |                                        |                                        |
 |                              crawler.py (discover pages to crawl)              |
 |                              scraper.py (fetch HTML, per page)                 |
 |                              analyzer.py (sentiment, entities, content quality)|
 |                              spamdexing.py (spam detection, per page)          |
 |                              ai_check.py (AI-likelihood score, per page)       |
 |                              site_checks.py (duplicates, scaled patterns)      |
 |                                        |                                        |
 |                              Creates report.json                               |
 |                                        |                                        |
 | Step 2: View report                   |                                        |
 |---------------------------------> serve.py                                     |
 |                                        |                                        |
 |                              Starts HTTP server                                |
 |                              Opens browser                                     |
 |                                        |                                        |
 |                                        |---------------------------------> report_veiwer.html
 |                                        |                                        |
 |                                        |                              script.js loads report.json
 |                                        |                              styles.css makes it pretty
 |                                        |                                        |
 |                                        |                              ✨ Beautiful Report Displayed!
```

---

## 📊 WHAT THE TOOL ANALYZES

### 1. **Page Discovery (Whole-Site Crawl)**
- Tries `sitemap.xml` first; falls back to following same-domain links (breadth-first, depth-limited)
- Respects `robots.txt`
- Retries a dead start URL, falling back to the sitemap if the homepage itself fails
- Configurable page/depth caps and politeness delay (`config.py`)

### 2. **Sentiment Analysis**
- Determines if content is positive, negative, or neutral
- Shows subjectivity score (objective vs subjective)

### 3. **Named Entity Recognition (NER)**
- Identifies people (PERSON), organizations (ORG), locations (GPE)
- Shows count for each entity

### 4. **Link Analysis**
- Counts internal links (links to same website)
- Counts external links (links to other websites)
- Identifies generic anchor text ("click here", "read more")

### 5. **Content Quality**
- **Readability**: Flesch Reading Ease score + label
- **Thin content**: flags pages below a configurable word-count floor
- **Repetitive phrasing**: flags n-gram phrases repeated past a configurable threshold
- **Anchor over-optimization**: flags when one anchor text dominates a page's outbound links

### 6. **Spam Detection**
- **Keyword Stuffing**: Detects overused words (>5% density)
- **Hidden Text**: Finds text hidden with CSS (display:none, etc.)

### 7. **Site-Wide Issues** (only computed when 2+ pages crawl successfully)
- **Duplicate/near-duplicate pages**: pairwise text-similarity comparison across the whole crawl
- **Scaled-content pattern**: flags when a large fraction of pages share near-identical content (a spam-policy red flag at scale)

### 8. **AI-Content-Likelihood Check**
Computes a 0-100 composite "AI-likelihood" score per page from four weighted signals, with a full breakdown of each:
- **Perplexity** (40%, default weight) — via the `distilgpt2` language model; more predictable text scores higher
- **Burstiness** (30%) — sentence-length variance; low variance (uniform sentence lengths) scores higher
- **Vocabulary diversity** (20%) — type-token ratio; low diversity scores higher
- **Cliché phrases** (10%) — matches against a list of common AI-writing stock phrases

Degrades gracefully: if the model fails to load, if perplexity fails for one specific page, or if a page's text is too short for a signal to be meaningful, that signal is marked unavailable/insufficient and the composite score renormalizes over whatever signals remain — the whole run never aborts because of this.

All weights and reference points are configurable in `config.py`.

---

## 🎨 REPORT VIEWER FEATURES

- **Glassmorphism UI** - Modern frosted glass design
- **Dark Theme** - Easy on the eyes
- **Animated Background** - Smooth gradient animation
- **Site-Wide Issues Summary** - Duplicate pages and scaled-content warnings shown up top
- **Click-to-Expand Page List** - One row per crawled page; click to expand full detail
- **Color-Coded Entities** - Different colors for ORG/PERSON/GPE
- **Responsive Design** - Works on desktop and mobile
- **All Warnings Listed** - Shows every spam instance found

---

## ⚡ QUICK REFERENCE

### Crawl and analyze a website:
```bash
python main.py "https://wikipedia.org/wiki/Python"
```

### Crawl with a custom config:
```bash
python main.py "https://wikipedia.org/wiki/Python" my_config.json
```

### View the report:
```bash
python serve.py
```

### Stop the server:
Press `Ctrl+C` in terminal

### Clear old reports:
```bash
rm -f report.json
```

Windows (PowerShell):
```powershell
Remove-Item report.json -ErrorAction SilentlyContinue
```

---

## 🐛 COMMON ERRORS & FIXES

### Error: "Failed to fetch"
**Cause**: Opened HTML file directly  
**Fix**: Use `python serve.py` instead

### Error: "report.json not found"
**Cause**: Haven't run analysis yet  
**Fix**: Run `python main.py "https://example.com"` first

### Error: "Module not found"
**Cause**: Dependencies not installed  
**Fix**: Run the pip install command from Step 1

### Error: "Port 8000 already in use"
**Cause**: Server already running or port taken  
**Fix**: Close other terminal or change PORT in serve.py

### Error: "spaCy model not found"
**Cause**: Language model not downloaded  
**Fix**: Run `python -m spacy download en_core_web_sm`

### "[!] Could not load perplexity model" in terminal output
**Cause**: No internet on first run (distilgpt2 needs to download once), or a `transformers`/`torch` install issue  
**Fix**: Check your connection and re-run; the crawl still completes without this one signal — it isn't fatal

---

## 🗑️ FILES YOU CAN DELETE

✅ **Safe to delete:**
- `report.json` (regenerated each run)
- `__pycache__/` folder (auto-recreated)
- `README.md` (this file - if you don't need help)

❌ **DO NOT delete:**
- Any `.py` files (`main.py`, `config.py`, `crawler.py`, `scraper.py`, `analyzer.py`, `site_checks.py`, `ai_check.py`, `spamdexing.py`, `serve.py`)
- Any frontend files (`report_veiwer.html`, `script.js`, `styles.css`)

---

## 💡 PRO TIPS

1. **Test with Wikipedia** - Good for testing (lots of entities, multiple linked pages)
   ```bash
   python main.py "https://en.wikipedia.org/wiki/Artificial_intelligence"
   ```

2. **Keep server running** - No need to restart between analyses
   - Run `python main.py "URL"` in one terminal
   - Keep `python serve.py` running in another terminal
   - Just refresh browser to see new report

3. **Export report** - The report.json is standard JSON, you can:
   - Open in any text editor
   - Import into Excel/Google Sheets
   - Process with other tools

4. **Tune thresholds without touching code** - Pass a JSON file as the second argument to `main.py` with just the fields you want to override (e.g. `{"max_pages": 10, "thin_content_word_floor": 150}`); every field in `config.py`'s `Config` dataclass can be overridden this way.

5. **Analyze local HTML** - You can modify scraper.py to analyze local files

---

## 🎓 DEMO WORKFLOW (For Teachers/Presentations)

### Best Way to Demo Multiple Sites:

**Step 1:** Start server ONCE (keep it running)
```bash
python serve.py
```
*(Browser opens automatically)*

**Step 2:** Open a NEW terminal, analyze each site:
```bash
# Site 1
python main.py "https://github.com"
# → Go to browser, press F5

# Site 2  
python main.py "https://wikipedia.org/wiki/Python"
# → Go to browser, press F5

# Site 3
python main.py "https://stackoverflow.com"
# → Go to browser, press F5
```

### ❓ Do I Need to Run serve.py Again?

**NO!** Just refresh the browser (F5) after running `python main.py` with a new URL.

| Action | Run main.py? | Run serve.py? | Refresh Browser? |
|--------|--------------|---------------|------------------|
| First site | ✅ YES | ✅ YES (once) | Auto-opens |
| New site | ✅ YES | ❌ NO | ✅ F5 |
| Another site | ✅ YES | ❌ NO | ✅ F5 |

**TL;DR:** Run `serve.py` **once**. For each new site, just run `main.py` and refresh browser!

---

## 📞 SUPPORT

If you see errors:
1. Check you ran the install commands
2. Make sure you're in the correct directory
3. Verify Python 3.7+ is installed (`python --version`)

---

**Python Version**: 3.7+  
**License**: Not specified (add a `LICENSE` file if publishing)
