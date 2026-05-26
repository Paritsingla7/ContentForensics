# 🔍 SEO Analyzer - Complete Guide

A comprehensive SEO analysis tool that analyzes websites for sentiment, entities, links, and spam detection.

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

### Step 2: Analyze a Website

```bash
python main.py "https://example.com"
```

**What happens:**
- Scrapes the website content
- Analyzes sentiment (positive/negative/neutral)
- Identifies named entities (people, organizations, locations)
- Counts internal/external links
- Detects spam techniques (keyword stuffing, hidden text)
- Saves results to `report.json`

### Step 3: View the Beautiful Report

```bash
python serve.py
```

**What happens:**
- Starts a local web server
- Opens your browser automatically
- Displays the report with a beautiful dark theme UI

**⚠️ IMPORTANT**: Never double-click `report_veiwer.html`! Always use `serve.py` to avoid CORS errors.

---

## 📁 FILE PURPOSES (What Each File Does)

### **CORE PYTHON FILES** (Backend - Do the Analysis)

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `main.py` | **Main script** - Coordinates everything, generates report.json | ❌ NO - Essential |
| `scraper.py` | Fetches and cleans website HTML | ❌ NO - Essential |
| `analyzer.py` | Performs sentiment analysis and entity recognition | ❌ NO - Essential |
| `spamdexing.py` | Detects keyword stuffing and hidden text | ❌ NO - Essential |
| `serve.py` | Runs local web server to view reports | ❌ NO - Essential |

### **FRONTEND FILES** (Display the Results)

| File | Purpose | Can Delete? |
|------|---------|-------------|
| `report_veiwer.html` | Report viewer webpage structure | ❌ NO - Essential |
| `script.js` | Loads and displays data from report.json | ❌ NO - Essential |
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
 |                              scraper.py (fetch HTML)                           |
 |                              analyzer.py (sentiment + entities)                |
 |                              spamdexing.py (spam detection)                    |
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

### 1. **Sentiment Analysis**
- Determines if content is positive, negative, or neutral
- Shows subjectivity score (objective vs subjective)

### 2. **Named Entity Recognition (NER)**
- Identifies people (PERSON)
- Identifies organizations (ORG)
- Identifies locations (GPE - Geo-Political Entity)
- Shows count for each entity

### 3. **Link Analysis**
- Counts internal links (links to same website)
- Counts external links (links to other websites)
- Identifies generic anchor text ("click here", "read more")

### 4. **Spam Detection**
- **Keyword Stuffing**: Detects overused words (>5% density)
- **Hidden Text**: Finds text hidden with CSS (display:none, etc.)

---

## 🎨 REPORT VIEWER FEATURES

- **Glassmorphism UI** - Modern frosted glass design
- **Dark Theme** - Easy on the eyes
- **Animated Background** - Smooth gradient animation
- **Color-Coded Entities** - Different colors for ORG/PERSON/GPE
- **Responsive Design** - Works on desktop and mobile
- **All Warnings Listed** - Shows every spam instance found

---

## ⚡ QUICK REFERENCE

### Analyze a website:
```bash
python main.py "https://wikipedia.org/wiki/Python"
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

---

## 🗑️ FILES YOU CAN DELETE

✅ **Safe to delete:**
- `report.json` (regenerated each run)
- `__pycache__/` folder (auto-recreated)
- `README.md` (this file - if you don't need help)

❌ **DO NOT delete:**
- Any `.py` files (main.py, scraper.py, analyzer.py, spamdexing.py, serve.py)
- Any frontend files (report_veiwer.html, script.js, styles.css)

---

## 💡 PRO TIPS

1. **Test with Wikipedia** - Good for testing (lots of entities)
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

4. **Analyze local HTML** - You can modify scraper.py to analyze local files

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

**Created**: October 2025  
**Python Version**: 3.7+  
**License**: Not specified (add a `LICENSE` file if publishing)

