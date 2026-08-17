# Day 4B — Per-File Import Audit & Pro Mode NameError Fix Report

**Date**: August 10, 2026  
**Status**: Completed  
**Target Repository**: StockSense AI Platform  

---

## Executive Summary

A regression was identified in `views/pro.py` where line 111 referenced `px.bar(...)` (Plotly Express bar chart) without an explicit `import plotly.express as px` statement in that specific file. To prevent similar regressions from indirect or missing imports, a complete AST-based per-file import audit was performed across all views in `views/` and root codebase modules.

---

## 1. Primary Bug Fix (`views/pro.py`)

- **Root Cause**: `views/pro.py` called `px.bar(...)` to render the stock score comparison bar chart in Pro Mode. During Day 2 cleanup, `import plotly.express as px` was properly removed from `ui_components.py` (where it was unused), leaving `views/pro.py` without an explicit module binding for `px`.
- **Fix Applied**: Added `import plotly.express as px` to the top of `views/pro.py`.

```python
import streamlit as st
import plotly.express as px
from data_service import screen_stocks_with_progress, load_ticker_list
from ui_components import apply_theme
```

---

## 2. Per-File Import Audit Results (`views/` Directory)

Every Python file inside `views/` was parsed using Python's `ast` (Abstract Syntax Tree) module to verify that every module-level identifier referenced (`st`, `px`, `go`, `pd`, `np`, `yf`, `time`, `re`, `datetime`, `requests`) is explicitly imported **within that same file**.

| View File | Module Identifiers Referenced | Explicit Imports Present in File | Audit Status |
| :--- | :--- | :--- | :--- |
| **`views/beginner.py`** | `st` | `st` | ✅ Verified Self-Contained |
| **`views/compare.py`** | `go`, `st` | `go`, `st` | ✅ Verified Self-Contained |
| **`views/home.py`** | `datetime`, `st` | `datetime`, `st` | ✅ Verified Self-Contained |
| **`views/login.py`** | `re`, `st`, `time` | `re`, `st`, `time` | ✅ Verified Self-Contained |
| **`views/pro.py`** | `px`, `st` | `px`, `st` *(Added `px`)* | ✅ Verified Self-Contained |
| **`views/search.py`** | `st` | `st` | ✅ Verified Self-Contained |
| **`views/stock_detail.py`** | `datetime`, `st` | `datetime`, `st` | ✅ Verified Self-Contained |
| **`views/trending.py`** | `st`, `yf` | `st`, `yf` | ✅ Verified Self-Contained |
| **`views/watchlist.py`** | `st`, `yf` | `st`, `yf` | ✅ Verified Self-Contained |

---

## 3. Root Level Module Import Audit

The same AST-based verification was conducted on root modules to ensure zero cross-module dependency leaking:

- **`app.py`**: References `st` -> Explicitly imports `import streamlit as st`.
- **`data_service.py`**: References `pd`, `requests`, `st`, `yf` -> Explicitly imports `pandas as pd`, `requests`, `streamlit as st`, `yfinance as yf`.
- **`ui_components.py`**: References `go`, `st` -> Explicitly imports `plotly.graph_objects as go`, `streamlit as st`.

---

## 4. Verification & Rendering Test

1. Executed a programmatic test of Pro Mode score bar chart generation (`px.bar` with custom color scales and `apply_theme`).
2. Verified that `px.bar` constructs the figure without raising `NameError` or missing attribute errors.

```
Score bar chart generated successfully without any NameError!
```
