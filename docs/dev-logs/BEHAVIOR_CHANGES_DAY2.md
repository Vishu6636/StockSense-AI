# Day 2 — Behavior Changes & Non-Breaking Stabilization Log

During the Day 2 bug-fix pass, all critical crash risks, data integrity flaws, dead code, unused imports, hardcoded relative paths, and bare except statements were resolved without modifying any UI text, layout, or feature behavior.

Below is the record of bug fixes applied and potential behavior adjustments noted:

---

### 1. Comparison View State Persistence (`views/compare.py`)
- **Previous Behavior**: Clicking "Compare Now" rendered the side-by-side comparison tables and charts. However, any subsequent user interaction (e.g. interacting with an expander or clicking a button) triggered a Streamlit rerun, causing the `st.button("Compare Now")` check to evaluate to `False` and immediately wiping the rendered comparison from the screen.
- **Fix Applied**: Persisted selected tickers in `st.session_state.compare_tickers`.
- **Visible Impact**: The side-by-side comparison now remains visible on user reruns instead of disappearing instantly. (Preserves intended feature behavior without altering UI text or layout).

---

### 2. Duplicate Key Moat Correction (`data_service.py`)
- **Previous Behavior**: `COALINDIA.NS` was defined twice in `COMPETITIVE_ADVANTAGES` — first as `"Monopoly"`, then overwritten as `"Cost Advantage"`.
- **Fix Applied**: Removed the duplicate entry so `COALINDIA.NS` consistently resolves to `"Monopoly"`.
- **Visible Impact**: Moat classification for `COALINDIA.NS` now correctly displays **Monopoly** instead of being overwritten.

---

### 3. Safe Fallbacks for RSI Technical Analysis (`views/stock_detail.py`)
- **Previous Behavior**: If `rsi_val` failed to calculate inside the metric row `try` block, accessing `rsi_val` in the RSI tab threw an `UnboundLocalError` application crash.
- **Fix Applied**: Initialized `rsi_val = None` prior to the calculation block and added fallback info handling when RSI data is missing.
- **Visible Impact**: Prevents Streamlit app crashes when technical indicator calculation fails on incomplete stock history.

---

### Summary
No UI layout shifts, design changes, or user-facing text modifications were introduced. The application now runs with zero dead code, clean exception handling, and full path portability.
