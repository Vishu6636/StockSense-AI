# 🚀 Streamlit Community Cloud Deployment Guide — StockSense AI

This document provides step-by-step instructions to deploy **StockSense AI v4.0** to **Streamlit Community Cloud** (free hosting), configure environment secrets, and understand cloud runtime behavior and limitations.

---

## 📋 Prerequisites

Before deploying, ensure you have:
1. A **GitHub account** with access to the repository: [https://github.com/Vishu6636/StockSense-AI](https://github.com/Vishu6636/StockSense-AI)
2. A **Streamlit Community Cloud account** linked to your GitHub (sign up free at [share.streamlit.io](https://share.streamlit.io)).
3. (Optional) A **Groq API key** for AI stock summary analysis (get a free key at [console.groq.com](https://console.groq.com)).

---

## 🛠️ Step-by-Step Deployment Guide

### Step 1: Push Code to GitHub
Ensure all recent code changes are committed and pushed to your default repository branch (`main` or `master`):

```bash
git status
git add .
git commit -m "Prepare StockSense AI v4.0 for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Create a New App on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
2. Click the **"Create app"** or **"New app"** button.
3. Select **"I already have an app"**.
4. Fill out the deployment form:
   - **Repository**: `Vishu6636/StockSense-AI`
   - **Branch**: `main` (or your active branch)
   - **Main file path**: `app.py`
   - **App URL** (optional custom slug): e.g., `stocksense-ai`

### Step 3: Configure Advanced Settings & Secrets
Before clicking **"Deploy!"**, open **"Advanced settings..."** (or navigate to **Settings ⚙️ → Secrets** after creation):

In the **Secrets** text editor, paste the following configuration:

```toml
# Required for AI Stock Analysis (Groq Llama 3.3 model)
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"

# (Optional) Fallback Market Data Keys
ALPHA_VANTAGE_KEY = "your_alpha_vantage_key_here"
GNEWS_KEY = "your_gnews_key_here"
```

> ⚠️ **Important**: Do NOT upload `.streamlit/secrets.toml` to public GitHub. Streamlit Cloud securely injects these secrets into `st.secrets` at runtime.

### Step 4: Launch & Verify
1. Click **"Deploy!"**.
2. Streamlit Cloud will automatically build the environment using `requirements.txt` (Python 3.10+ runtime).
3. Once the build completes, your live application will be accessible at:
   `https://<your-custom-slug>.streamlit.app`

---

## ⚠️ Known Cloud Limitations & Architecture Notes

### 1. `nsepython` Scraper Limitation on Cloud Servers
- **Issue**: The `nsepython` package relies on web scraping direct NSE India endpoints (`https://www.nseindia.com`). National Stock Exchange endpoints actively block request headers coming from public cloud IP ranges (AWS, GCP, Azure, Streamlit Cloud) using Cloudflare rate-limiting.
- **Solution**: StockSense AI uses `yfinance` for Indian stocks (`.NS` / `.BO` tickers) and `Alpha Vantage` fallback endpoints. This ensures 100% data reliability on cloud deployment without IP blocking.

### 2. Memory Limits & Resource Management
- **Issue**: Streamlit Community Cloud free tier provides ~1 GB of RAM. Heavy concurrent multi-stock screening across 500+ stocks can cause memory spikes if unoptimized.
- **Solution**: 
  - StockSense AI utilizes `@st.cache_data(ttl=300)` to cache fetched yfinance data frames and ticker metadata across users.
  - The default screening mode uses **"Quick Scan (Top 50)"**, which processes data in micro-batches to remain lightweight.

### 3. Cookies & Session Persistence
- **Behavior**: The application uses `streamlit-cookies-controller` for local session login state persistence.
- **Limitation**: If a user has third-party cookies disabled in their browser, login state will remain in memory for the duration of the browser session without throwing an error.

---

## 🔍 Post-Deployment Verification Checklist

Once deployed, run through this quick 2-minute smoke test on your live app:

- [ ] **Home Page**: Verify live index ticker bar loads (Nifty, Sensex, S&P 500).
- [ ] **Market Switch**: Toggle between `IN ₹ India` and `US $ US` modes.
- [ ] **Stock Search**: Search for `RELIANCE.NS` or `AAPL` and view fundamental & technical charts.
- [ ] **Beginner Wizard & SIP Calculator**: Complete a 5-step screening flow and adjust SIP sliders.
- [ ] **Portfolio Analyzer**: Navigate to the `Portfolio` tab and click "Analyze Portfolio".
- [ ] **Groq AI Summary**: Click the "AI Summary" tab on any stock detail page (requires `GROQ_API_KEY`).
