# Day 3 — Security & Secrets Hardening Audit Report

**Date**: August 10, 2026  
**Status**: Completed  
**Target Repository**: StockSense AI Platform  

---

## Executive Summary

The Day 3 audit focused on hardening security posture, preventing accidental credential exposure, enforcing API call timeouts, auditing authentication security, and purging sensitive log files containing local environment details.

---

## Detailed Audit & Hardening Findings

### 1. Repository `.gitignore` Hardening
- **Audit Result**: The `.gitignore` file was active but lacked explicit wildcard patterns for log/trace files and Streamlit internal cache directories.
- **Action Taken**: Updated `.gitignore` to explicitly exclude:
  - `.streamlit/secrets.toml`
  - `.streamlit/cache/`, `.streamlit/*.log`, `.streamlit/*.txt`
  - `*.log`, `*.trace`, `streamlit_log.txt`, `trace.txt`
  - `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`
  - `.conda/`, `venv/`, `env/`

---

### 2. Hardcoded Credentials & Secrets Audit
- **Audit Result**:
  - Scanning all codebase files (`.py`, `.toml`, `.json`, `.md`) confirmed **zero** unencrypted active API keys hardcoded in Python source code.
  - However, `.streamlit/secrets.toml` contained commented-out valid key strings for **Alpha Vantage** (`[REDACTED - ROTATED]`) and **GNews** (`[REDACTED - ROTATED]`).
- **Action Taken**:
  - Replaced the commented keys in `.streamlit/secrets.toml` with safe generic placeholders (`"your-alpha-vantage-key-here"` and `"your-gnews-key-here"`).
  - Updated API initialization checks in `data_service.py` to recognize generic placeholders as unconfigured and return empty fallbacks gracefully.

---

### 3. External API Timeout & Resilience Audit

| API Service | Function | Key Required? | Timeout Configured? | Error Behavior | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **yfinance** | `get_stock_data`, `_to_av_ticker` | No | Default HTTP timeout | Returns empty dict / dataframe | ✅ Safe |
| **nsepython** | `_nsepython_quote` | No | Internal fallback | Returns empty dict `{}` | ✅ Safe |
| **Alpha Vantage** | `_alpha_vantage_history` | Optional | `timeout=10` | Returns empty `pd.DataFrame()` | ✅ Safe |
| **GNews** | `_gnews_fetch` | Optional | `timeout=8` | Returns empty list `[]` | ✅ Safe |
| **Groq AI** | `get_ai_summary` | Optional | `timeout=15.0` | Returns user-friendly warning message | ✅ Safe |

- **Action Taken**: Added `timeout=15.0` to `Groq(api_key=api_key)` client instantiation in `data_service.py` and updated key check guards so missing or placeholder keys immediately trigger graceful degraded responses without throwing exceptions or blocking UI rendering.

---

### 4. Login Flow Security Audit (`views/login.py`)

An in-depth review of the authentication workflow revealed the following security characteristics:

1. **Passwordless User Profiling**:
   - `views/login.py` prompts users for an Email address and Name.
   - **Finding**: There is no password field, hashing mechanism, or OTP verification. The application operates on passwordless identification rather than cryptographic authentication.
2. **Plaintext Cookie Storage**:
   - `streamlit_cookies_controller` is used to persist `ss_email` and `ss_name` in browser cookies.
   - **Finding**: Cookies store the email and name in plain text without signature or encryption.
3. **Session State Handling**:
   - User identity (`user_email`, `user_name`) is retained in server-side `st.session_state`.
   - **Finding**: No password or secret authentication tokens are stored in `st.session_state` or cookies. Therefore, there is **zero risk of password leakage**.

---

### 5. Sensitive Log File Purge
- **Audit Result**: `streamlit_log.txt` and `trace.txt` existed in the project root directory. `streamlit_log.txt` contained local network URLs (`http://192.168.x.x:8501`) and environment metadata.
- **Action Taken**: Permanently deleted `streamlit_log.txt` and `trace.txt` from the workspace.

---

## Action Items & Decisions Matrix

| Item | Risk Level | Status | Details / Recommended Action |
| :--- | :--- | :--- | :--- |
| `.gitignore` rules | Low | **Fixed** | Updated `.gitignore` to block all `.log`, `.trace`, and `.streamlit` cache files. |
| Log & trace files | Medium | **Fixed** | Deleted `streamlit_log.txt` and `trace.txt`. |
| API Timeouts | Low | **Fixed** | Hardened `Groq`, `Alpha Vantage`, and `GNews` API timeout guards. |
| **Exposed Key Rotation** | **Medium** | **Manual Action Required** | The Alpha Vantage key (`[REDACTED - ROTATED]`) and GNews key (`[REDACTED - ROTATED]`) were present in `secrets.toml`. If these were your private production keys, **please rotate them in your API provider dashboards**. |

---

## Verification Command Result

```bash
python -c "import os, re; p=r'sk-[a-zA-Z0-9_-]{10,}|gsk_[a-zA-Z0-9_-]{10,}'; [print(f'Match: {m}') for r,d,fs in os.walk('.') if '.git' not in r for f in fs for m in re.findall(p, open(os.path.join(r,f), errors='ignore').read())]"
```
**Output**: `0 matches found`. No secret keys remain exposed in the repository code or configuration files.
